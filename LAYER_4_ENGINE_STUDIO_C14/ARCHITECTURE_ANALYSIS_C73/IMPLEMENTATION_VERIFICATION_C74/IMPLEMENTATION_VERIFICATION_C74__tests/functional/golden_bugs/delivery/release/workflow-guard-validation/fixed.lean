def overlapCheck : Bool := true
def finishCheck : Bool := true
-- Two output guards: one has no outcome restriction, one requires success.
def guardMatches (restrictOutcome success : Bool) : Bool := !restrictOutcome || success
def overlap : Bool := guardMatches false true && guardMatches true true
-- start has an exit to done and a branch to stuck; stuck loops to itself.
def reachesFinal : Nat → Nat → Bool
  | 0, state => state == 2
  | fuel + 1, state => state == 2 ||
      (state == 0 && (reachesFinal fuel 1 || reachesFinal fuel 2)) ||
      (state == 1 && reachesFinal fuel 1)
#eval !overlapCheck && overlap
#eval !finishCheck && !(reachesFinal 3 1)
