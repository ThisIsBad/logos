"""Quick evaluation of LLM answers against stress-test benchmarks."""
import json
from logic_brain.loader import parse_problem
from logic_brain.verifier import PropositionalVerifier

v = PropositionalVerifier()

with open("benchmarks/stress_test.json", encoding="utf-8") as f:
    problems = json.load(f)["problems"]

with open("results/llm_answers_stress.json", encoding="utf-8") as f:
    answers = json.load(f)["answers"]

correct = 0
total = 0
for p in problems:
    pid = p["id"]
    if pid not in answers:
        continue
    total += 1
    llm_valid = answers[pid]["valid"]
    ground_truth = p["expected_valid"]
    ok = llm_valid == ground_truth
    if ok:
        correct += 1
    status = "OK" if ok else "WRONG"
    print(f"{status:5s} {pid:8s} LLM={'valid' if llm_valid else 'invalid':7s} truth={'valid' if ground_truth else 'invalid':7s} | {answers[pid]['reasoning'][:80]}")

print(f"\n{'='*60}")
print(f"Score: {correct}/{total} ({100*correct//total}%)")
if correct == total:
    print("ALL CORRECT - need harder problems!")
else:
    wrong = [p["id"] for p in problems if p["id"] in answers and answers[p["id"]]["valid"] != p["expected_valid"]]
    print(f"Failed: {', '.join(wrong)}")
