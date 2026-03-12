import z3

U = z3.DeclareSort('U')
Loves = z3.Function('Loves', U, U, z3.BoolSort())
Happy = z3.Function('Happy', U, z3.BoolSort())
John = z3.Const('John', U)
Mary = z3.Const('Mary', U)
x = z3.Const('x', U)
y = z3.Const('y', U)

# ∀x ((∃y Loves(x, y)) → Happy(x))
ex_y = z3.Exists([y], Loves(x, y))
impl = z3.Implies(ex_y, Happy(x))
p1 = z3.ForAll([x], impl)

p2 = Loves(John, Mary)
conc = Happy(John)

s = z3.Solver()
s.add(p1)
s.add(p2)
s.add(z3.Not(conc))

res = s.check()
print("Z3 result:", res)
if res == z3.sat:
    print(s.model())
