"""Escalation ladder — generate progressively harder exams until LLM fails.

Each round increases the number of variables, premises, and nesting depth.
The goal: find the exact point where the LLM breaks down.
"""

import json
import time
import random
from pathlib import Path
from logic_brain.models import Proposition, LogicalExpression, Connective, Argument
from logic_brain.verifier import PropositionalVerifier

v = PropositionalVerifier()

# ---------------------------------------------------------------
# Escalation levels
# ---------------------------------------------------------------
LEVELS = {
    "round1": {"vars": 6, "premises": 7,  "depth": 3, "problems": 5},
    "round2": {"vars": 8, "premises": 9,  "depth": 3, "problems": 5},
    "round3": {"vars": 10, "premises": 12, "depth": 3, "problems": 5},
}

ALL_NAMES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def rand_expr(rng, variables, depth=0, max_d=2):
    if depth >= max_d or rng.random() < 0.4:
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

def expr_nl(e):
    if isinstance(e, Proposition):
        return f"{e.label}"
    if e.connective is Connective.NOT:
        return f"¬{expr_nl(e.left)}"
    sym = {"AND":"∧","OR":"∨","IMPLIES":"→","IFF":"↔"}[e.connective.value]
    return f"({expr_nl(e.left)} {sym} {expr_nl(e.right)})"


import sys
round_name = sys.argv[1] if len(sys.argv) > 1 else "round1"
cfg = LEVELS[round_name]

rng = random.Random(time.time_ns())
variables = [Proposition(n) for n in ALL_NAMES[:cfg["vars"]]]

exam = {"round": round_name, "config": cfg, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "problems": [], "answer_key": {}}

for i in range(cfg["problems"]):
    premises = [rand_expr(rng, variables, 0, cfg["depth"]) for _ in range(cfg["premises"])]
    conclusion = rand_expr(rng, variables, 0, cfg["depth"])
    arg = Argument(premises=premises, conclusion=conclusion)
    result = v.verify(arg)

    pid = f"ESC-{round_name[-1]}-{i+1:02d}"
    formal_prems = [expr_str(p) for p in premises]
    conc_str = expr_str(conclusion)

    exam["problems"].append({
        "id": pid,
        "premises_formal": formal_prems,
        "conclusion_formal": conc_str,
        "full_formal": ", ".join(formal_prems) + f" ⊢ {conc_str}",
    })
    exam["answer_key"][pid] = {
        "valid": result.valid,
        "rule": result.rule,
        "counterexample": result.counterexample,
    }

out = Path(f"results/escalation_{round_name}.json")
out.write_text(json.dumps(exam, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"=== ESCALATION {round_name.upper()} ===")
print(f"Variables: {cfg['vars']} | Premises: {cfg['premises']} | Depth: {cfg['depth']}")
print(f"Generated: {exam['generated_at']}\n")

for p in exam["problems"]:
    print(f"## {p['id']}")
    print(f"Premises:")
    for j, prem in enumerate(p["premises_formal"], 1):
        print(f"  {j}. {prem}")
    print(f"Conclusion: {p['conclusion_formal']}")
    print(f"Valid? ___")
    print()

n_valid = sum(1 for a in exam["answer_key"].values() if a["valid"])
print(f"[Key: {n_valid} valid, {cfg['problems']-n_valid} invalid]")
