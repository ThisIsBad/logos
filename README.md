# LogicBrain

[![CI](https://github.com/ThisIsBad/LogicBrain/actions/workflows/ci.yml/badge.svg)](https://github.com/ThisIsBad/LogicBrain/actions/workflows/ci.yml)

A Z3-backed deterministic verifier for propositional and predicate logic. Designed to be used directly by AI coding agents (Claude Code, OpenCode, Aider, etc.) via Python execution.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Local Test Quickstart

```powershell
pip install -e ".[dev]"
pytest -q
```

## Usage

```python
from logic_brain import verify, is_tautology, is_contradiction, are_equivalent

# Verify logical arguments
result = verify("P -> Q, P |- Q")
print(result.valid)  # True
print(result.rule)   # "Modus Ponens"

# Detect fallacies
result = verify("P -> Q, Q |- P")
print(result.valid)          # False
print(result.rule)           # "Affirming the Consequent (fallacy)"
print(result.counterexample) # {'P': False, 'Q': True}

# Check tautologies and contradictions
is_tautology("P | ~P")       # True (Law of Excluded Middle)
is_contradiction("P & ~P")   # True

# Check logical equivalence
are_equivalent("~(P & Q)", "~P | ~Q")  # True (De Morgan's Law)
are_equivalent("P -> Q", "~Q -> ~P")   # True (Contraposition)
```

## CLI

```powershell
python -m logic_brain "P -> Q, P |- Q"
python -m logic_brain "P -> Q, Q |- P" --explain
python -m logic_brain "P -> Q, P |- Q" --json
```

## Syntax

| Symbol | Meaning | Alternatives |
|--------|---------|--------------|
| `->` | Implication | `=>` |
| `<->` | Biconditional | `<=>` |
| `&` | Conjunction (AND) | `^` |
| `\|` | Disjunction (OR) | |
| `~` | Negation (NOT) | `!` |
| `\|-` | Turnstile (therefore) | |
| `A-Z` | Atomic propositions | |
| `()` | Grouping | |

## Examples

```python
# Valid inference rules
verify("P -> Q, P |- Q")           # Modus Ponens
verify("P -> Q, ~Q |- ~P")         # Modus Tollens
verify("P -> Q, Q -> R |- P -> R") # Hypothetical Syllogism
verify("P | Q, ~P |- Q")           # Disjunctive Syllogism
verify("P, Q |- P & Q")            # Conjunction Introduction
verify("P & Q |- P")               # Conjunction Elimination
verify("P -> Q |- ~Q -> ~P")       # Contraposition

# Common fallacies (all return valid=False)
verify("P -> Q, Q |- P")           # Affirming the Consequent
verify("P -> Q, ~P |- ~Q")         # Denying the Antecedent
```

## For AI Agents

This library is designed to be called directly via Python execution. No MCP server or API wrapper needed.

```python
# Agent writes this code, executes it, reads the result
from logic_brain import verify
result = verify("P -> Q, P |- Q")
# Agent sees: valid=True, rule="Modus Ponens"
# Agent can now use this information to verify its reasoning
```

## First-Order Logic (Predicate Logic)

For predicate logic with quantifiers, use the `PredicateVerifier`:

```python
from logic_brain import (
    PredicateVerifier, Variable, Constant, Predicate,
    QuantifiedExpression, Quantifier, PredicateExpression,
    PredicateConnective, FOLArgument
)

v = PredicateVerifier()

# "All humans are mortal. Socrates is human. Therefore, Socrates is mortal."
x = Variable("x")
socrates = Constant("socrates")

Human = lambda t: Predicate("Human", [t])
Mortal = lambda t: Predicate("Mortal", [t])

premise1 = QuantifiedExpression(
    Quantifier.FORALL, x,
    PredicateExpression(PredicateConnective.IMPLIES, Human(x), Mortal(x))
)
premise2 = Human(socrates)
conclusion = Mortal(socrates)

arg = FOLArgument(premises=[premise1, premise2], conclusion=conclusion)
result = v.verify(arg)
print(result.valid)  # True
```

## Lean 4 Interactive Proving

For tactic-by-tactic theorem proving with Lean 4:

```python
from logic_brain import LeanSession, is_lean_available

if is_lean_available():
    session = LeanSession()
    session.start("theorem test : 1 + 1 = 2 := by")
    
    result = session.apply("rfl")
    print(result.success)      # True
    print(session.is_complete) # True
    print(session.proof)       # "theorem test : 1 + 1 = 2 := by\n  rfl"

    bad = session.apply("reflexivity")
    if not bad.success:
        print(bad.error_type)    # e.g. "unknown_tactic"
        print(bad.suggestions)   # structured recovery hints
```

Features:
- Tactic-by-tactic proof construction with immediate feedback
- Automatic rollback on failed tactics
- Undo support
- Goal state tracking
- Automatic Lean 4 detection via elan
- Structured diagnostics (`result.diagnostic`, `result.error_type`, `result.suggestions`)

## Z3 Incremental Solving

For incremental constraint solving with backtracking:

```python
from logic_brain import Z3Session

session = Z3Session()
session.declare("x", "Int")
session.declare("y", "Int")

session.assert_constraint("x > 0")
session.assert_constraint("y > x")
session.assert_constraint("x + y < 100")

result = session.check()
print(result.satisfiable)  # True
print(result.model)        # {'x': 1, 'y': 2}

# Backtracking with push/pop
session.push()
session.assert_constraint("x > 50")
result = session.check()  # Still satisfiable

session.assert_constraint("y < 10")
result = session.check()  # Unsatisfiable (x > 50, y > x, y < 10)

if not result.satisfiable:
    print(result.error_type)   # "unsatisfiable"
    print(result.suggestions)  # conflicting constraints / next actions

session.pop()  # Remove last two constraints
result = session.check()  # Satisfiable again
```

Features:
- Variable declaration (Int, Real, Bool, BitVec)
- Incremental constraint assertion
- Push/pop for backtracking
- Model extraction for satisfiable results
- Unsat core extraction for debugging
- Structured diagnostics for unsat/unknown/parse failures

## Project Structure

```
logic_brain/
├── parser.py         # String-based parser ("P -> Q, P |- Q")
├── verifier.py       # Z3-backed propositional logic verifier
├── predicate.py      # Z3-backed predicate logic verifier
├── lean_session.py   # Lean 4 interactive session wrapper
├── z3_session.py     # Z3 incremental solving session
├── models.py         # Core data types
├── predicate_models.py # FOL data types
├── loader.py         # Benchmark loader
└── runner.py         # Benchmark runner
benchmarks/
└── problems.json     # 25 graded logic problems
tests/
├── test_parser.py    # Parser tests (45 tests)
├── test_verifier.py  # Verifier tests
├── test_predicate.py # FOL tests
├── test_lean_session.py # Lean session tests (18 tests)
└── test_z3_session.py   # Z3 session tests (31 tests)
```

## Running Tests

```powershell
pytest -q              # Run full suite (CI default)
pytest -v              # Verbose run
pytest tests/ -v       # Test-directory run
```

## Running Benchmarks

```powershell
python -m logic_brain.runner

# Generate fresh benchmark files
python tools/generate_exam.py --count 10
python tools/generate_hardmode.py --vars 8 --premises 8 --count 5 --depth 3
python tools/generate_escalation.py round2 --count 5

# Check result files
python tools/check_results.py exam
python tools/check_results.py hardmode hardmode_10v_10p
python tools/check_results.py escalation round2
python tools/check_stress_results.py

# Or provide explicit files
python tools/check_results.py --benchmarks results/hardmode_8v_8p.json --answers results/hardmode_8v_8p_answers.json

# Lean and FOL answer checkers
python tools/check_lean_results.py
python tools/check_fol_results.py
```

FOL checker schema expectations:
- Benchmark file contains `problems` with `id` and `expected_valid`.
- Answers file contains `answers` keyed by problem id, each with a `valid` boolean.

Legacy compatibility wrappers (deprecated):

```powershell
python check_lean.py
python check_predicate.py
python generate_exam.py
python hardmode.py
python escalate.py
python verify_stress.py
```

## Examples

```powershell
python examples/quick_verify.py
python examples/interactive_sessions.py
```

Notebook demo:
- `examples/logic_brain_demo.ipynb`

Roadmap assessment:
- `docs/logic_extensions_assessment.md`

## Releases

- Follow semantic versioning (`MAJOR.MINOR.PATCH`).
- Check `CHANGELOG.md` for release notes and upgrade context.
- Follow `docs/release_playbook.md` for the release checklist and smoke tests.
- GitHub releases are published at:
  - `https://github.com/ThisIsBad/LogicBrain/releases`

## License

MIT
