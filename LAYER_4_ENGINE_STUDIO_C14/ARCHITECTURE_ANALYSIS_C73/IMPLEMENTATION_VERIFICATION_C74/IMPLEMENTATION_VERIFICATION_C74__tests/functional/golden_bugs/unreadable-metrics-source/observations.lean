-- Labels recorded by test_replay.py; this is not a proof of Python semantics.
inductive Outcome where
  | omitted | namedError
  deriving DecidableEq

def acceptable : Outcome → Bool
  | .omitted => false
  | .namedError => true

example : acceptable .omitted = false ∧ acceptable .namedError = true := by
  decide
