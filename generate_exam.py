"""Generate a fresh logic exam — standalone script."""

import json
import time
import random
from pathlib import Path
from logic_brain.models import Proposition, LogicalExpression, Connective, Argument
from logic_brain.verifier import PropositionalVerifier

v = PropositionalVerifier()
rng = random.Random(time.time_ns())

VARS = [Proposition(c) for c in "ABCDE"]

def rand_expr(depth=0, max_d=2):
    if depth >= max_d or rng.random() < 0.45:
        return rng.choice(VARS)
    conn = rng.choice(list(Connective))
    if conn is Connective.NOT:
        return LogicalExpression(conn, rand_expr(depth+1, max_d))
    return LogicalExpression(conn, rand_expr(depth+1, max_d), rand_expr(depth+1, max_d))

def expr_str(e):
    if isinstance(e, Proposition):
        return e.label
    if e.connective is Connective.NOT:
        return f"¬{expr_str(e.left)}"
    sym = {"AND":"∧","OR":"∨","IMPLIES":"→","IFF":"↔"}[e.connective.value]
    return f"({expr_str(e.left)} {sym} {expr_str(e.right)})"

def expr_nl(e):
    if isinstance(e, Proposition):
        return f"{e.label} is true"
    if e.connective is Connective.NOT:
        inner = expr_nl(e.left)
        if inner.endswith(" is true"):
            return inner[:-8] + " is false"
        return f"NOT ({inner})"
    left, right = expr_nl(e.left), expr_nl(e.right)
    if e.connective is Connective.AND:
        return f"({left}) AND ({right})"
    if e.connective is Connective.OR:
        return f"({left}) OR ({right})"
    if e.connective is Connective.IMPLIES:
        return f"IF ({left}) THEN ({right})"
    if e.connective is Connective.IFF:
        return f"({left}) IFF ({right})"
    return str(e)

problems = []
answer_key = {}

for i in range(10):
    # Generate 4-6 random premises
    n_prems = rng.randint(4, 6)
    premises = [rand_expr(0, 2) for _ in range(n_prems)]

    # Generate a random conclusion
    conclusion = rand_expr(0, 2)

    arg = Argument(premises=premises, conclusion=conclusion)
    result = v.verify(arg)

    pid = f"GEN-{i+1:03d}"

    nl_parts = [f"Given:"]
    for j, p in enumerate(premises, 1):
        nl_parts.append(f"  {j}. {expr_nl(p)}")
    nl_parts.append(f"Conclusion: {expr_nl(conclusion)}")

    formal_parts = [expr_str(p) for p in premises]
    formal = ", ".join(formal_parts) + f" ⊢ {expr_str(conclusion)}"

    problems.append({
        "id": pid,
        "natural_language": "\n".join(nl_parts),
        "formal": formal,
    })

    answer_key[pid] = {
        "valid": result.valid,
        "rule": result.rule,
        "counterexample": result.counterexample,
    }

exam = {
    "exam_id": f"{time.time_ns() % 10**12:012x}",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "problems": problems,
    "answer_key": answer_key,
}

out = Path("results/exam_fresh_001.json")
out.write_text(json.dumps(exam, indent=2, ensure_ascii=False), encoding="utf-8")

# Print problems (NOT the answer key)
print(f"Exam ID: {exam['exam_id']}")
print(f"Generated: {exam['generated_at']}")
print(f"Problems: {len(problems)}\n")
print("="*60)

for p in problems:
    print(f"\n## {p['id']}")
    print(p["natural_language"])
    print(f"Formal: {p['formal']}")
    print("-"*40)

# Summary of answer key (valid/invalid counts only)
n_valid = sum(1 for a in answer_key.values() if a["valid"])
print(f"\n[Answer key: {n_valid} valid, {10-n_valid} invalid]")
