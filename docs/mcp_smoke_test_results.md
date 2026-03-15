# MCP Smoke Test Results

Date: 2026-03-15

Validated with:
- Claude Code CLI `2.1.42`
- Model `claude-opus-4-6`
- LogicBrain MCP server via `python -m logic_brain.mcp_server`

## Setup

- Project config present at `.claude/mcp.json`
- Claude was run in print mode with permission bypass for repeatable local validation
- Debug logging was enabled for the combined scenario to confirm actual MCP tool execution order

Representative invocation pattern:

```powershell
claude -p --model opus --permission-mode bypassPermissions
```

## Scenario 1 - Argument Verification

Prompt goal: ask Claude Code to verify two arguments with the MCP tool.

Observed tool:
- `mcp__logic-brain__verify_argument`

Observed payloads:

```json
{ "argument": "P -> Q, P |- Q" }
{ "argument": "P -> Q, Q |- P" }
```

Observed responses:

```json
{
  "valid": true,
  "rule": "Modus Ponens",
  "certificate_id": "1e645a47...",
  "explanation": "The conclusion follows necessarily from the premises. No truth-value assignment can make all premises true while making the conclusion false."
}
```

```json
{
  "valid": false,
  "rule": "Affirming the Consequent (fallacy)",
  "certificate_id": "9f2c70f5...",
  "explanation": "The conclusion does NOT follow from the premises. Counterexample: when P=F, Q=T, all premises are true but the conclusion is false."
}
```

Result:
- Worked as expected
- Claude correctly reported valid vs invalid and used the counterexample in its explanation
- End-to-end latency from Claude CLI output: about `15.3s`

## Scenario 2 - Assumption Consistency Check

Prompt goal: provide business-rule assumptions and ask Claude Code to identify contradictions.

Observed tool:
- `mcp__logic-brain__check_assumptions`

Observed payload:

```json
{
  "assumptions": [
    { "id": "a1", "statement": "budget > 0", "kind": "assumption" },
    { "id": "a2", "statement": "budget < 0", "kind": "fact" },
    { "id": "a3", "statement": "headcount >= 1", "kind": "hypothesis" }
  ],
  "variables": {
    "budget": "Int",
    "headcount": "Int"
  }
}
```

Observed response:

```json
{
  "consistent": false,
  "conflict_ids": ["a1", "a2"],
  "explanation": "The active assumptions contain a contradiction under the supplied variable declarations."
}
```

Result:
- Worked as expected
- Claude correctly identified `a1` and `a2` as the conflicting pair and ignored unrelated `a3`
- End-to-end latency from Claude CLI output: about `12.8s`

## Scenario 3 - Counterfactual Analysis

Prompt goal: ask Claude Code which branches are feasible under shared base constraints.

Observed tool:
- `mcp__logic-brain__counterfactual_branch`

Observed payload:

```json
{
  "variables": { "x": "Int" },
  "base_constraints": ["x > 0"],
  "branches": {
    "safe": ["x < 10"],
    "stretch": ["x > 100"],
    "impossible": ["x < 0"]
  }
}
```

Observed response:

```json
{
  "branches": {
    "safe": { "satisfiable": true, "status": "sat" },
    "stretch": { "satisfiable": true, "status": "sat" },
    "impossible": { "satisfiable": false, "status": "unsat" }
  }
}
```

Result:
- Worked as expected
- Claude correctly translated `sat`/`unsat` into feasible/infeasible narrative language
- End-to-end latency from Claude CLI output: about `13.5s`

## Scenario 4 - Combined Reasoning

Prompt goal: ask Claude Code to chain assumption checking, branch evaluation, and argument verification in one task.

Prompt inputs:
- Assumptions:
  - `a1 = capacity >= 10`
  - `a2 = demand > capacity`
  - `a3 = demand < 8`
- Branches:
  - `hire = ["capacity >= 20"]`
  - `discount = ["demand < 8"]`
  - `hold = ["demand == 12"]`
- Argument:
  - `P -> Q, P |- Q`

Debug-log confirmed tool execution order:
- `mcp__logic-brain__check_assumptions`
- `mcp__logic-brain__counterfactual_branch`
- `mcp__logic-brain__verify_argument`

Server-side timings from `claude_mcp_debug.log`:
- `check_assumptions`: `55ms`
- `counterfactual_branch`: `21ms`
- `verify_argument`: `13ms`

Observed tool responses:

```json
{
  "consistent": false,
  "conflict_ids": ["a1", "a2", "a3"],
  "explanation": "The active assumptions contain a contradiction under the supplied variable declarations."
}
```

```json
{
  "branches": {
    "hire": { "satisfiable": true, "status": "sat" },
    "discount": { "satisfiable": false, "status": "unsat" },
    "hold": { "satisfiable": true, "status": "sat" }
  }
}
```

```json
{
  "valid": true,
  "rule": "Modus Ponens",
  "certificate_id": "1e645a47...",
  "explanation": "The conclusion follows necessarily from the premises. No truth-value assignment can make all premises true while making the conclusion false."
}
```

Result:
- Worked as expected
- Claude used the contradiction result from step 1 to explain why the `discount` branch was unsatisfiable in step 2
- Claude then separately used `verify_argument` correctly for the final deductive check
- End-to-end latency from Claude CLI output: about `16.7s`

## What Worked

- Tool discovery worked: Claude saw and invoked all 5 LogicBrain MCP tools
- Structured dict outputs were easy for Claude to interpret and summarize
- Combined-tool reasoning worked: Claude successfully chained multiple LogicBrain tools in one answer
- Server reliability was good: no crashes, no malformed MCP responses, no blocking failures
- Tool runtimes were low; almost all delay came from model turn time rather than server execution

## What Was Awkward Or Confusing

- `claude --mcp-config ".claude/mcp.json"` was interpreted by this Claude CLI version as inline JSON, not a file path; debug log showed `SyntaxError: Unexpected token '.', ".claude/mcp.json" is not valid JSON`
- Despite that, the project MCP config still loaded, so the test passed; this behavior is confusing and should be documented carefully
- In print mode, Claude first asked for approval to use MCP tools unless `--permission-mode bypassPermissions` was supplied
- In one combined run, Claude summarized the chained reasoning well but did not always echo every tool payload/result unless explicitly instructed

## Unhelpful Error Messages

- The `--mcp-config` parse error is not very helpful because it does not explain whether the flag expects JSON content, a JSON string, or a path in this CLI version
- Permission prompts are clear enough interactively, but in `-p` automation they require either manual approval or explicit permission-mode flags

## API Changes Needed

- No blocking API changes required for LogicBrain MCP itself
- Possible future improvement: include a little more semantic detail in `counterfactual_branch` responses, such as an optional model for satisfiable branches
- Possible future improvement: document `certificate_id` as an opaque stable identifier; Claude treated it correctly, but its meaning is not obvious from the field alone

## Performance Observations

- MCP server execution was fast; measured tool runtimes were `13ms` to `55ms` in the combined scenario
- End-to-end latency was dominated by Claude model turn time rather than LogicBrain computation
- No observable instability occurred across repeated runs

## Conclusion

All 4 smoke-test scenarios completed successfully with Claude Code as the agent consumer. Claude discovered the LogicBrain MCP server, invoked the expected tools, received useful structured results, and incorporated those results into its reasoning. No blocking failures were found.
