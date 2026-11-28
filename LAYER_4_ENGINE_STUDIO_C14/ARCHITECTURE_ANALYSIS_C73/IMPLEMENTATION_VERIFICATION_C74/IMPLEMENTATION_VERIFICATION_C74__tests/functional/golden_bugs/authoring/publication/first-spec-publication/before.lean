-- Translation of the SPEC branch in the adjacent historical Python fixture.
-- Target syntax, status, and migration-reference validation already passed.
inductive Route where
  | rejectPinned | ambiguous | missing | firstPinned | firstUnpinned | revision
  deriving DecidableEq, Repr

def select (pinned : Bool) (chosen predecessors : Nat) : Route :=
  if pinned then
    if chosen == 1 && predecessors == 0 then .firstPinned else .rejectPinned
  else if chosen != 1 || predecessors > 1 then .ambiguous
  else if predecessors == 0 then .missing else .revision

-- A valid unpinned SPEC Draft has one selection and no predecessor.
-- Independent expected route is firstUnpinned; the old branch rejects it.
example : select false 1 0 ≠ .firstUnpinned := by decide
example : select false 1 0 = .missing := by decide
