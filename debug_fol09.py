from check_predicate import ast_builders, verifier
import z3

arg = ast_builders["FOL-09"]()
verifier._reset_cache()
solver = z3.Solver()

z3_p1 = verifier._convert(arg.premises[0], {})
z3_p2 = verifier._convert(arg.premises[1], {})
z3_conc = verifier._convert(arg.conclusion, {})

print("P1:", z3_p1)
print("P2:", z3_p2)
print("Conc:", z3_conc)

solver.add(z3_p1)
solver.add(z3_p2)
solver.add(z3.Not(z3_conc))

print("Z3 Check:", solver.check())
