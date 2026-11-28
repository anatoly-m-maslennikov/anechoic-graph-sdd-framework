-- Translation of the SPEC branch in the adjacent historical Python fixture.
-- Target syntax, status, and migration-reference validation already passed.
inductive Route where
  | rejectPinned | ambiguous | missing | firstPinned | firstUnpinned | revision
  deriving DecidableEq, Repr

def select (pinned : Bool) (chosen predecessors : Nat) : Route :=
  if pinned then
    if chosen == 1 && predecessors == 0 then .firstPinned else .rejectPinned
  else if chosen != 1 || predecessors > 1 then .ambiguous
  else if predecessors == 0 then .firstUnpinned else .revision

-- Same input and independently expected route as in before.lean.
example : select false 1 0 = .firstUnpinned := by decide
example : select false 2 0 = .ambiguous := by decide
