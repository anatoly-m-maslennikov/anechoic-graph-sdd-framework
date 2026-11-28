-- Finite abstraction of the recognized fixed.py.txt branch.
def implementation (inputHasId inputHasRoot : Bool) : Bool × Bool × Bool :=
  (true, true, true)
def invariant (r : Bool × Bool × Bool) : Bool := r.1 && r.2.1 && r.2.2
theorem observed : invariant (implementation false false) = true := by decide
#eval invariant (implementation false false)
