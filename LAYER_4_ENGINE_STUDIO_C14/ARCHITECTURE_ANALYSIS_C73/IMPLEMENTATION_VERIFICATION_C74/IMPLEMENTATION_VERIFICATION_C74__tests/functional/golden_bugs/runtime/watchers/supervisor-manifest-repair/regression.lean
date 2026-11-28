-- Initial selection raises ValueError, with a running supervisor
-- and working diagnostics.
def failSoft (survives retries diagnostics : Bool) : Bool :=
  survives && retries && diagnostics
example : failSoft false false false = false := by decide
example : failSoft true true true = true := by decide
