"""MCP stdio server exposing LogicBrain tools."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

try:
    import anyio
    import mcp.types as mcp_types
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "MCP SDK is not installed. Install with: pip install logic-brain[mcp]"
    ) from exc

from logic_brain.mcp_tools import (
    check_assumptions,
    check_policy,
    counterfactual_branch,
    verify_argument,
    z3_check,
    z3_session,
)

ToolHandler = Callable[[dict[str, object]], dict[str, object]]

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, object]
    handler: ToolHandler


_VARIABLE_SPEC_SCHEMA: dict[str, object] = {
    "anyOf": [
        {"type": "string"},
        {
            "type": "object",
            "properties": {
                "sort": {"type": "string"},
                "size": {"type": "integer"},
            },
            "required": ["sort"],
            "additionalProperties": False,
        },
    ]
}
_ASSUMPTION_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "statement": {"type": "string"},
        "kind": {"type": "string", "enum": ["fact", "assumption", "hypothesis"]},
    },
    "required": ["id", "statement", "kind"],
    "additionalProperties": False,
}
_RULE_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "severity": {"type": "string", "enum": ["error", "warning"]},
        "message": {"type": "string"},
        "when_true": {"type": "array", "items": {"type": "string"}},
        "when_false": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["name", "severity", "message"],
    "additionalProperties": False,
}
_SESSION_ACTION_SCHEMA: dict[str, object] = {
    "type": "string",
    "enum": ["create", "declare", "assert", "check", "push", "pop", "destroy"],
}


def _tool(
    name: str,
    description: str,
    properties: dict[str, object],
    required: list[str],
    handler: ToolHandler,
) -> ToolSpec:
    return ToolSpec(
        name=name,
        description=description,
        input_schema={
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
        handler=handler,
    )


_TOOLS: tuple[ToolSpec, ...] = (
    _tool(
        "verify_argument",
        "Verify a logical argument and return a proof summary. Example: {'argument': 'P -> Q, P |- Q'}",
        {"argument": {"type": "string", "description": "Argument string to verify."}},
        ["argument"],
        verify_argument,
    ),
    _tool(
        "check_assumptions",
        "Check whether assumptions are jointly satisfiable via Z3. "
        "Example: {'assumptions': [{'id': 'a1', 'statement': 'x > 0', "
        "'kind': 'assumption'}], 'variables': {'x': 'Int'}}",
        {
            "assumptions": {
                "type": "array",
                "description": "Assumptions to load into an AssumptionSet.",
                "items": _ASSUMPTION_SCHEMA,
            },
            "variables": {
                "type": "object",
                "description": "Optional Z3 sorts keyed by variable name.",
                "additionalProperties": {"type": "string"},
            },
        },
        ["assumptions"],
        check_assumptions,
    ),
    _tool(
        "counterfactual_branch",
        "Evaluate named branches against shared base constraints. "
        "Example: {'variables': {'x': 'Int'}, 'base_constraints': ['x > 0'], "
        "'branches': {'b1': ['x < 10']}}",
        {
            "variables": {
                "type": "object",
                "description": "Variable declarations keyed by name.",
                "additionalProperties": _VARIABLE_SPEC_SCHEMA,
            },
            "base_constraints": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Constraints applied to every branch.",
            },
            "branches": {
                "type": "object",
                "description": "Named branch constraints.",
                "additionalProperties": {"type": "array", "items": {"type": "string"}},
            },
        },
        ["variables", "base_constraints", "branches"],
        counterfactual_branch,
    ),
    _tool(
        "z3_check",
        "Run a direct satisfiability check. Example: {'variables': {'x': 'Int'}, 'constraints': ['x > 0', 'x < 10']}",
        {
            "variables": {
                "type": "object",
                "description": "Variable declarations keyed by name.",
                "additionalProperties": _VARIABLE_SPEC_SCHEMA,
            },
            "constraints": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Constraints to assert into one Z3 session.",
            },
        },
        ["variables", "constraints"],
        z3_check,
    ),
    _tool(
        "check_policy",
        "Evaluate an action against policy rules. Example: {'rules': "
        "[{'name': 'needs_tests', 'severity': 'error', 'message': 'Add tests'}], "
        "'action': {'public_api': True}}",
        {
            "rules": {"type": "array", "items": _RULE_SCHEMA},
            "action": {
                "type": "object",
                "description": "Boolean action flags keyed by field name.",
                "additionalProperties": {"type": "boolean"},
            },
        },
        ["rules", "action"],
        check_policy,
    ),
    _tool(
        "z3_session",
        "Manage a stateful Z3 session across multiple MCP calls. Example: {'action': 'create', 'session_id': 'demo'}",
        {
            "action": _SESSION_ACTION_SCHEMA,
            "session_id": {"type": "string", "description": "Stable session identifier."},
            "variables": {
                "type": "object",
                "description": "Variables to declare for the 'declare' action.",
                "additionalProperties": _VARIABLE_SPEC_SCHEMA,
            },
            "constraints": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Constraints to assert for the 'assert' action.",
            },
            "count": {
                "type": "integer",
                "description": "Optional number of scopes to pop for the 'pop' action.",
            },
        },
        ["action", "session_id"],
        z3_session,
    ),
)


def create_server() -> Server[object, object]:
    """Create the low-level MCP server with registered LogicBrain tools."""
    server: Server[object, object] = Server(
        name="logic-brain",
        instructions="LogicBrain exposes deterministic reasoning tools backed by Z3.",
    )

    list_tools_decorator = cast(
        Callable[[Callable[[], object]], Callable[[], object]],
        server.list_tools(),  # type: ignore[no-untyped-call]
    )

    @list_tools_decorator
    async def list_tools() -> list[mcp_types.Tool]:
        return [
            mcp_types.Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema,
            )
            for tool in _TOOLS
        ]

    call_tool_decorator = cast(
        Callable[[Callable[[str, dict[str, object]], object]], Callable[[str, dict[str, object]], object]],
        server.call_tool(),
    )

    @call_tool_decorator
    async def call_tool(name: str, arguments: dict[str, object]) -> dict[str, object]:
        for tool in _TOOLS:
            if tool.name == name:
                return tool.handler(arguments)
        raise ValueError(f"Unknown tool '{name}'")

    return server


async def _serve_stdio() -> None:
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(
                notification_options=NotificationOptions(),
            ),
        )


def main() -> None:
    """Run the LogicBrain MCP server over stdio."""
    anyio.run(_serve_stdio)


if __name__ == "__main__":
    main()
