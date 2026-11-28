-- Outcome labels from test_replay.py, not a proof of Python semantics.
inductive Outcome where
  | compiled | rejected
  deriving DecidableEq
example : Outcome.compiled ≠ Outcome.rejected := by decide
