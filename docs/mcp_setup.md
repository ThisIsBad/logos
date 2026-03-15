# MCP Setup

This guide explains how to run LogicBrain as an MCP server for Claude Code.

Tested against Claude Code MCP support as available on 2026-03-15.

## Prerequisites

- Python 3.10+
- LogicBrain checked out locally
- MCP extra installed: `pip install -e ".[mcp]"`

## Quick Start

1. Install the MCP extra:

   ```powershell
   pip install -e ".[mcp]"
   ```

2. Add the project-level MCP config in `.claude/mcp.json`:

   ```json
   {
     "mcpServers": {
       "logic-brain": {
         "command": "python",
         "args": ["-m", "logic_brain.mcp_server"],
         "cwd": "<project-root>"
       }
     }
   }
   ```

3. Start Claude Code in this repository. The LogicBrain tools should appear.

## Project-Level vs Global Config

- Project-level: keep `.claude/mcp.json` in the repository and set `cwd` to the repo root
- Global: copy the same server block into your user-level Claude Code MCP config if you want LogicBrain available outside this repository

## Verifying the Server

- Import check: `python -c "import logic_brain.mcp_server"`
- Direct start: `python -m logic_brain.mcp_server`
- Claude Code check: open a session and confirm these tools are listed:
  - `verify_argument`
  - `check_assumptions`
  - `counterfactual_branch`
  - `z3_check`
  - `check_policy`

## Tool Reference

### `verify_argument`

- Input:

  ```json
  {"argument": "P -> Q, P |- Q"}
  ```

- Output:

  ```json
  {
    "valid": true,
    "rule": "Modus Ponens",
    "certificate_id": "<stable-id>",
    "explanation": "The conclusion follows from the premises."
  }
  ```

### `check_assumptions`

- Input:

  ```json
  {
    "assumptions": [
      {"id": "a1", "statement": "x > 0", "kind": "assumption"},
      {"id": "a2", "statement": "x < 10", "kind": "fact"}
    ],
    "variables": {"x": "Int"}
  }
  ```

- Output:

  ```json
  {
    "consistent": true,
    "conflict_ids": [],
    "explanation": "All 2 active assumptions are jointly satisfiable."
  }
  ```

### `counterfactual_branch`

- Input:

  ```json
  {
    "variables": {"x": "Int"},
    "base_constraints": ["x > 0"],
    "branches": {
      "safe": ["x < 10"],
      "impossible": ["x < 0"]
    }
  }
  ```

- Output:

  ```json
  {
    "branches": {
      "impossible": {"satisfiable": false, "status": "unsat"},
      "safe": {"satisfiable": true, "status": "sat"}
    }
  }
  ```

### `z3_check`

- Input:

  ```json
  {
    "variables": {"x": "Int"},
    "constraints": ["x > 0", "x < 10"]
  }
  ```

- Output:

  ```json
  {
    "satisfiable": true,
    "model": {"x": 1},
    "unsat_core": null
  }
  ```

### `check_policy`

- Input:

  ```json
  {
    "rules": [
      {
        "name": "needs_tests",
        "severity": "error",
        "message": "Add tests before merging",
        "when_true": ["public_api"],
        "when_false": ["has_tests"]
      }
    ],
    "action": {"public_api": true, "has_tests": false}
  }
  ```

- Output:

  ```json
  {
    "decision": "BLOCK",
    "violations": [
      {
        "policy_name": "needs_tests",
        "severity": "error",
        "message": "Add tests before merging",
        "triggered_fields": ["public_api", "has_tests"]
      }
    ],
    "remediation_hints": ["Resolve policy 'needs_tests': Add tests before merging"]
  }
  ```

## Error Format

All tools return structured validation/runtime errors instead of uncaught exceptions:

```json
{
  "error": "Invalid input",
  "details": "Field 'argument' must be a non-empty string"
}
```

## Troubleshooting

- Server will not start:
  - install the optional dependency: `pip install -e ".[mcp]"`
  - verify import: `python -c "import logic_brain.mcp_server"`
- Tools do not show up in Claude Code:
  - confirm the `cwd` points at the LogicBrain repository root
  - restart Claude Code after changing MCP config
  - run `python -m logic_brain.mcp_server` manually to catch import errors
- Tool call fails with validation error:
  - compare your payload to the examples above
  - make sure all required fields are present and spelled exactly
