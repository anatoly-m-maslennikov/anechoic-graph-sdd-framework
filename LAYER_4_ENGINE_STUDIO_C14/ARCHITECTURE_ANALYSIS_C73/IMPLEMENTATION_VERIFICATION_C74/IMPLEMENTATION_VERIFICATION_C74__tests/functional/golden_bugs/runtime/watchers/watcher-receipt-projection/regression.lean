-- Concrete valid ordinary directory creation with one valid carrier witness.
def handled (recordsOrdinary acceptsOrdinary : Bool) : Bool :=
  recordsOrdinary && acceptsOrdinary
example : handled false false = false := by decide
example : handled true true = true := by decide
