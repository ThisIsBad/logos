"""Check LLM answers against the Lean 4 compiler."""

import json
from logic_brain.lean_verifier import LeanVerifier

# The path where elan installs lean
lean_bin = r"C:\Users\Stefan\.elan\bin\lean.exe"
verifier = LeanVerifier(lean_bin)

with open("benchmarks/lean_problems.json", "r", encoding="utf-8") as f:
    benchmarks = json.load(f)["problems"]

with open("results/lean_answers.json", "r", encoding="utf-8") as f:
    answers = json.load(f)["answers"]

correct = 0
total = len(benchmarks)

print(f"{'ID':>8s} | {'Status':>12s} | {'Tactic'}")
print("-" * 50)

for prob in benchmarks:
    pid = prob["id"]
    if pid not in answers:
        print(f"{pid:>8s} | {'MISSING':>12s} | ")
        continue
        
    tactic = answers[pid]["tactic_proof"]
    header = prob["lean_header"]
    res = verifier.verify(header, tactic)
    
    if res.valid:
        correct += 1
        status = "OK"
    else:
        status = "!! ERROR !!"
        
    print(f"{pid:>8s} | {status:>12s} | {tactic}")
    if not res.valid:
        print(f"         > Compiler Error:\n{res.output}")

print(f"\nScore: {correct}/{total} ({100*correct//total}%)")
