"""Check LLM answers against fresh exam answer key."""
import json

with open("results/exam_fresh_001.json", encoding="utf-8") as f:
    exam = json.load(f)

with open("results/llm_answers_fresh.json", encoding="utf-8") as f:
    llm = json.load(f)

answers = llm["answers"]
key = exam["answer_key"]

correct = 0
total = 0

for pid in sorted(key.keys()):
    total += 1
    truth = key[pid]["valid"]
    if pid in answers:
        llm_ans = answers[pid]["valid"]
        ok = llm_ans == truth
        if ok:
            correct += 1
        status = "OK" if ok else "WRONG"
        reasoning = answers[pid].get("reasoning", "")[:80]
        print(f"{status:5s} {pid} | LLM={'valid' if llm_ans else 'invalid':7s} truth={'valid' if truth else 'invalid':7s} | {reasoning}")
    else:
        print(f"MISS  {pid} | no answer")

print(f"\n{'='*60}")
print(f"Score: {correct}/{total} ({100*correct//total}%)")
if correct < total:
    wrong = [pid for pid in sorted(key.keys()) if pid in answers and answers[pid]["valid"] != key[pid]["valid"]]
    print(f"Failed: {', '.join(wrong)}")
    for pid in wrong:
        print(f"\n  {pid}:")
        print(f"    LLM said: {'valid' if answers[pid]['valid'] else 'invalid'}")
        print(f"    Truth:    {'valid' if key[pid]['valid'] else 'invalid'}")
        print(f"    LLM reasoning: {answers[pid].get('reasoning','')}")
        if key[pid].get("counterexample"):
            print(f"    Counterexample: {key[pid]['counterexample']}")
