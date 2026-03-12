"""Hard-mode generator — avoids trivial problems (contradictions, identities).

Generates problems where:
1. Premises are consistent (no contradictions → no ex falso escape)
2. Conclusion is never a direct premise
3. Balanced valid/invalid ratio
4. High variable count and deep nesting
"""

import json
import time
import random
from pathlib import Path
from logic_brain.models import Proposition, LogicalExpression, Connective, Argument
from logic_brain.verifier import PropositionalVerifier

v = PropositionalVerifier()

ALL_NAMES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def rand_expr(rng, variables, depth=0, max_d=3):
    if depth >= max_d or rng.random() < 0.35:
        return rng.choice(variables)
    conn = rng.choice(list(Connective))
    if conn is Connective.NOT:
        return LogicalExpression(conn, rand_expr(rng, variables, depth+1, max_d))
    return LogicalExpression(conn,
        rand_expr(rng, variables, depth+1, max_d),
        rand_expr(rng, variables, depth+1, max_d))

def expr_str(e):
    if isinstance(e, Proposition):
        return e.label
    if e.connective is Connective.NOT:
        inner = expr_str(e.left)
        return f"¬({inner})" if len(inner) > 1 else f"¬{inner}"
    sym = {"AND":"∧","OR":"∨","IMPLIES":"→","IFF":"↔"}[e.connective.value]
    return f"({expr_str(e.left)} {sym} {expr_str(e.right)})"

def premises_are_consistent(premises, variables):
    """Check that the premises don't form a contradiction."""
    import z3
    z3_vars = {v.label: z3.Bool(v.label) for v in variables}
    solver = z3.Solver()
    for p in premises:
        solver.add(to_z3(p, z3_vars))
    return solver.check() == z3.sat

def to_z3(expr, z3_vars):
    import z3
    if isinstance(expr, Proposition):
        return z3_vars[expr.label]
    if expr.connective is Connective.NOT:
        return z3.Not(to_z3(expr.left, z3_vars))
    left = to_z3(expr.left, z3_vars)
    right = to_z3(expr.right, z3_vars)
    if expr.connective is Connective.AND:   return z3.And(left, right)
    if expr.connective is Connective.OR:    return z3.Or(left, right)
    if expr.connective is Connective.IMPLIES: return z3.Implies(left, right)
    if expr.connective is Connective.IFF:   return left == right

def exprs_structurally_equal(a, b):
    if type(a) != type(b): return False
    if isinstance(a, Proposition): return a.label == b.label
    if a.connective != b.connective: return False
    if not exprs_structurally_equal(a.left, b.left): return False
    if a.right is None and b.right is None: return True
    if a.right is None or b.right is None: return False
    return exprs_structurally_equal(a.right, b.right)

import sys
num_vars = int(sys.argv[1]) if len(sys.argv) > 1 else 8
num_prems = int(sys.argv[2]) if len(sys.argv) > 2 else 8
num_problems = int(sys.argv[3]) if len(sys.argv) > 3 else 5
max_depth = int(sys.argv[4]) if len(sys.argv) > 4 else 3

rng = random.Random(time.time_ns())
variables = [Proposition(n) for n in ALL_NAMES[:num_vars]]

exam = {
    "config": {"vars": num_vars, "premises": num_prems, "depth": max_depth},
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "problems": [],
    "answer_key": {},
}

generated = 0
attempts = 0
target_valid = num_problems // 2  # Try to balance
valid_count = 0

while generated < num_problems and attempts < 500:
    attempts += 1

    # Generate consistent premises
    for _ in range(50):
        premises = [rand_expr(rng, variables, 0, max_depth) for _ in range(num_prems)]
        if premises_are_consistent(premises, variables):
            break
    else:
        continue

    # Generate conclusion (not identical to any premise)
    conclusion = rand_expr(rng, variables, 0, max_depth)
    is_dup = any(exprs_structurally_equal(conclusion, p) for p in premises)
    if is_dup:
        continue

    arg = Argument(premises=premises, conclusion=conclusion)
    result = v.verify(arg)

    # Balance valid/invalid
    if result.valid and valid_count >= target_valid + 1:
        continue
    if not result.valid and (generated - valid_count) >= (num_problems - target_valid + 1):
        continue

    if result.valid:
        valid_count += 1

    generated += 1
    pid = f"HARD-{generated:02d}"

    exam["problems"].append({
        "id": pid,
        "premises_formal": [expr_str(p) for p in premises],
        "conclusion_formal": expr_str(conclusion),
        "full_formal": ", ".join(expr_str(p) for p in premises) + f" ⊢ {expr_str(conclusion)}",
    })
    exam["answer_key"][pid] = {
        "valid": result.valid,
        "rule": result.rule,
        "counterexample": result.counterexample,
    }

out = Path(f"results/hardmode_{num_vars}v_{num_prems}p.json")
out.write_text(json.dumps(exam, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"=== HARD MODE ===")
print(f"Variables: {num_vars} | Premises: {num_prems} | Depth: {max_depth}")
print(f"Generated: {generated} problems in {attempts} attempts\n")

for p in exam["problems"]:
    print(f"## {p['id']}")
    print(f"Premises:")
    for j, prem in enumerate(p["premises_formal"], 1):
        print(f"  {j}. {prem}")
    print(f"Conclusion: {p['conclusion_formal']}")
    print()

n_valid = sum(1 for a in exam["answer_key"].values() if a["valid"])
print(f"[Key: {n_valid} valid, {generated-n_valid} invalid]")
