"""Check the LLM answers for First-Order Logic benchmarks."""

import json
from logic_brain.predicate_models import (
    Variable, Constant, Predicate, PredicateConnective, 
    PredicateExpression, QuantifiedExpression, Quantifier, FOLArgument
)
from logic_brain.predicate import PredicateVerifier

def build_ast_01():
    x = Variable("x"); socrates = Constant("Socrates")
    p1 = QuantifiedExpression(Quantifier.FORALL, x, PredicateExpression(PredicateConnective.IMPLIES, Predicate("Human", (x,)), Predicate("Mortal", (x,))))
    return FOLArgument((p1, Predicate("Human", (socrates,))), Predicate("Mortal", (socrates,)))

def build_ast_02():
    x = Variable("x"); socrates = Constant("Socrates")
    p1 = QuantifiedExpression(Quantifier.FORALL, x, PredicateExpression(PredicateConnective.IMPLIES, Predicate("Human", (x,)), Predicate("Mortal", (x,))))
    return FOLArgument((p1, Predicate("Mortal", (socrates,))), Predicate("Human", (socrates,)))

def build_ast_03():
    x = Variable("x"); y = Variable("y")
    p1 = QuantifiedExpression(Quantifier.EXISTS, y, QuantifiedExpression(Quantifier.FORALL, x, Predicate("Loves", (y, x))))
    conc = QuantifiedExpression(Quantifier.FORALL, x, QuantifiedExpression(Quantifier.EXISTS, y, Predicate("Loves", (y, x))))
    return FOLArgument((p1,), conc)

def build_ast_04():
    x = Variable("x"); y = Variable("y")
    p1 = QuantifiedExpression(Quantifier.FORALL, x, QuantifiedExpression(Quantifier.EXISTS, y, Predicate("Loves", (y, x))))
    conc = QuantifiedExpression(Quantifier.EXISTS, y, QuantifiedExpression(Quantifier.FORALL, x, Predicate("Loves", (y, x))))
    return FOLArgument((p1,), conc)

def build_ast_05():
    x = Variable("x")
    inside = PredicateExpression(PredicateConnective.IMPLIES, Predicate("Bird", (x,)), Predicate("CanFly", (x,)))
    p1 = PredicateExpression(PredicateConnective.NOT, QuantifiedExpression(Quantifier.FORALL, x, inside))
    conc = QuantifiedExpression(Quantifier.EXISTS, x, PredicateExpression(PredicateConnective.AND, Predicate("Bird", (x,)), PredicateExpression(PredicateConnective.NOT, Predicate("CanFly", (x,)))))
    return FOLArgument((p1,), conc)

def build_ast_06():
    x = Variable("x"); barber = Constant("Barber")
    # ∀x (Shaves(Barber, x) ↔ ¬Shaves(x, x))
    inside = PredicateExpression(PredicateConnective.IFF, Predicate("Shaves", (barber, x)), PredicateExpression(PredicateConnective.NOT, Predicate("Shaves", (x, x))))
    p1 = QuantifiedExpression(Quantifier.FORALL, x, inside)
    conc = Predicate("Shaves", (barber, barber))
    return FOLArgument((p1,), conc)

def build_ast_07():
    x = Variable("x"); y = Variable("y"); z = Variable("z")
    alice = Constant("Alice"); bob = Constant("Bob"); charlie = Constant("Charlie")
    # ∀x ∀y ∀z ((Taller(x, y) ∧ Taller(y, z)) → Taller(x, z))
    inside = PredicateExpression(PredicateConnective.IMPLIES, PredicateExpression(PredicateConnective.AND, Predicate("Taller", (x, y)), Predicate("Taller", (y, z))), Predicate("Taller", (x, z)))
    p1 = QuantifiedExpression(Quantifier.FORALL, x, QuantifiedExpression(Quantifier.FORALL, y, QuantifiedExpression(Quantifier.FORALL, z, inside)))
    p2 = Predicate("Taller", (alice, bob))
    p3 = Predicate("Taller", (bob, charlie))
    conc = Predicate("Taller", (alice, charlie))
    return FOLArgument((p1, p2, p3), conc)

def build_ast_08():
    x = Variable("x"); y = Variable("y"); z = Variable("z")
    p1 = QuantifiedExpression(Quantifier.EXISTS, x, Predicate("P", (x,)))
    p2 = QuantifiedExpression(Quantifier.EXISTS, y, Predicate("Q", (y,)))
    conc = QuantifiedExpression(Quantifier.EXISTS, z, PredicateExpression(PredicateConnective.AND, Predicate("P", (z,)), Predicate("Q", (z,))))
    return FOLArgument((p1, p2), conc)

def build_ast_09():
    x = Variable("x"); y = Variable("y")
    john = Constant("John"); mary = Constant("Mary")
    # ∀x ((∃y Loves(x, y)) → Happy(x))
    ex_y = QuantifiedExpression(Quantifier.EXISTS, y, Predicate("Loves", (x, y)))
    inside = PredicateExpression(PredicateConnective.IMPLIES, ex_y, Predicate("Happy", (x,)))
    p1 = QuantifiedExpression(Quantifier.FORALL, x, inside)
    p2 = Predicate("Loves", (john, mary))
    conc = Predicate("Happy", (john,))
    return FOLArgument((p1, p2), conc)

def build_ast_10():
    x = Variable("x"); y = Variable("y"); z = Variable("z"); w = Variable("w")
    # (∀x TakesExam(x)) → (∀y WillPass(y))
    p1_ant = QuantifiedExpression(Quantifier.FORALL, x, Predicate("TakesExam", (x,)))
    p1_cons = QuantifiedExpression(Quantifier.FORALL, y, Predicate("WillPass", (y,)))
    p1 = PredicateExpression(PredicateConnective.IMPLIES, p1_ant, p1_cons)
    
    # ∀z (Student(z) → TakesExam(z))
    p2 = QuantifiedExpression(Quantifier.FORALL, z, PredicateExpression(PredicateConnective.IMPLIES, Predicate("Student", (z,)), Predicate("TakesExam", (z,))))
    
    # ∀w (Student(w) → WillPass(w))
    conc = QuantifiedExpression(Quantifier.FORALL, w, PredicateExpression(PredicateConnective.IMPLIES, Predicate("Student", (w,)), Predicate("WillPass", (w,))))
    
    return FOLArgument((p1, p2), conc)

ast_builders = {
    "FOL-01": build_ast_01, "FOL-02": build_ast_02, "FOL-03": build_ast_03, "FOL-04": build_ast_04,
    "FOL-05": build_ast_05, "FOL-06": build_ast_06, "FOL-07": build_ast_07, "FOL-08": build_ast_08,
    "FOL-09": build_ast_09, "FOL-10": build_ast_10
}

verifier = PredicateVerifier()

# Load ground truth from Z3
ground_truth = {}
for pid, builder in ast_builders.items():
    arg = builder()
    res = verifier.verify(arg)
    ground_truth[pid] = res.valid

# Load LLM answers
with open("results/predicate_answers.json", "r") as f:
    llm_data = json.load(f)

answers = llm_data["answers"]

correct = 0
total = len(ast_builders)

print(f"{'ID':>8s} | {'LLM':>7s} | {'Truth':>7s} | {'Status'}")
print("-" * 40)

for pid in sorted(ast_builders.keys()):
    if pid not in answers:
        print(f"{pid:>8s} | MISSING")
        continue
        
    llm_ans = answers[pid]["valid"]
    truth = ground_truth[pid]
    ok = llm_ans == truth
    
    if ok: 
        correct += 1
        status = "OK"
    else: 
        status = "!! WRONG !!"
        
    print(f"{pid:>8s} | {'valid' if llm_ans else 'invalid':>7s} | {'valid' if truth else 'invalid':>7s} | {status}")
    if not ok:
        print(f"         > Reasoning: {answers[pid].get('reasoning', '')}")

print(f"\nScore: {correct}/{total} ({100*correct//total}%)")
