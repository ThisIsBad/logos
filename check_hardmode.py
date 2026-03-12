"""Check hard mode round answers."""
import json, sys

round_name = sys.argv[1] if len(sys.argv) > 1 else "hardmode_8v_8p"

with open(f"results/{round_name}.json", encoding="utf-8") as f:
    exam = json.load(f)
with open(f"results/{round_name}_answers.json", encoding="utf-8") as f:
    llm = json.load(f)

answers = llm["answers"]
key = exam["answer_key"]
correct = total = 0

for pid in sorted(key.keys()):
    total += 1
    truth = key[pid]["valid"]
    llm_ans = answers.get(pid, {}).get("valid")
    if llm_ans is None:
        print(f"MISS  {pid}")
        continue
    ok = llm_ans == truth
    if ok: correct += 1
    status = "OK" if ok else "!! WRONG !!"
    print(f"{status:12s} {pid} | LLM={'valid' if llm_ans else 'invalid':7s} truth={'valid' if truth else 'invalid':7s}")
    if not ok:
        print(f"             LLM reasoning: {answers[pid].get('reasoning','')[:120]}")
        ce = key[pid].get("counterexample")
        if ce: print(f"             Counterexample: {ce}")

print(f"\nScore: {correct}/{total} ({100*correct//total if total else 0}%)")
