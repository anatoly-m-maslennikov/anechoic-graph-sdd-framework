-- Labels recorded by replay.mjs; this does not prove TypeScript semantics.
def accepted (sameQuery : Bool) : Bool := sameQuery
example : accepted false = false ∧ accepted true = true := by decide
