from logic_brain.lean_verifier import LeanVerifier

# The path where elan installs lean
lean_bin = r"C:\Users\Stefan\.elan\bin\lean.exe"
v = LeanVerifier(lean_bin)

# Test 1: A valid, very simple proof
print("Test 1: Valid proof")
valid_code = """
theorem pluss_zero (n : Nat) : n + 0 = n := by
  rfl
"""
res = v.verify_raw(valid_code)
print("Valid:", res.valid)
print("Error:", res.error)
print("Output:", res.output)


# Test 2: Invalid proof (unsolved goal)
print("\nTest 2: Invalid proof")
invalid_code = """
theorem pluss_one (n : Nat) : n + 1 = n := by
  rfl
"""
res2 = v.verify_raw(invalid_code)
print("Valid:", res2.valid)
print("Error:", res2.error)
print("Output:", res2.output)
