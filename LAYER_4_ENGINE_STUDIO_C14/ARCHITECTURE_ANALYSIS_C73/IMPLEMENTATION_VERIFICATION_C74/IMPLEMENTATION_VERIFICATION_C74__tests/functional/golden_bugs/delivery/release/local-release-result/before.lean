-- Finite abstraction of the recognized before.py.txt branch.
def implementation (inputHasId inputHasRoot : Bool) : Bool × Bool × Bool :=
  (inputHasId, inputHasRoot, true)
def invariant (r : Bool × Bool × Bool) : Bool := r.1 && r.2.1 && r.2.2
theorem observed : invariant (implementation false false) = false := by decide
#eval invariant (implementation false false)
