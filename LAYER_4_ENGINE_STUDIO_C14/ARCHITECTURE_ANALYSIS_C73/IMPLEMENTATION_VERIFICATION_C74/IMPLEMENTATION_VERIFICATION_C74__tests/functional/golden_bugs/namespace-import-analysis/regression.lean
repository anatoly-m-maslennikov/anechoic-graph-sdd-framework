import Lean
-- The import clause has no default name and contains a namespace import.
-- Reading the absent name without a guard crashes before traversal completes.
inductive Outcome where
  | crashed | survived
  deriving BEq, Repr, DecidableEq

def scanner (guardsName : Bool) : Outcome :=
  if guardsName then .survived else .crashed

def required : Outcome := .survived

example : scanner false ≠ required := by decide
example : scanner true = required := by decide
