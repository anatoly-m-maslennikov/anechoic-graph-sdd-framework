-- Translation of the SPEC branch in the adjacent historical Python fixture.
-- Target syntax, status, and migration-reference validation already passed.
inductive Route where
  | rejectPinned | ambiguous | missing | firstPinned | firstUnpinned | revision
  deriving DecidableEq, Repr

def select (pinned : Bool) (chosen predecessors : Nat) : Route :=
  if pinned then .rejectPinned
  else if chosen != 1 || predecessors > 1 then .ambiguous
  else if predecessors == 0 then .missing else .revision

-- A valid pinned SPEC Draft has one selection and no predecessor.
-- Independent expected route is firstPinned; the old guard rejects it.
example : select true 1 0 ≠ .firstPinned := by decide
example : select true 1 0 = .rejectPinned := by decide
