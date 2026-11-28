-- Outcome labels recorded by test_replay.py, not a proof of Python semantics.
inductive Status where
  | failed | blocked
  deriving DecidableEq
example : Status.failed ≠ Status.blocked := by decide
