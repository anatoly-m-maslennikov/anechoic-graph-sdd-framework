inductive Event where | lock | git | version deriving DecidableEq, Repr
def trace : List Event := [.lock, .git, .version]
def lockedBeforeEffects : List Event → Bool
  | [] => true
  | .lock :: _ => true
  | _ :: _ => false
def contract : Bool := lockedBeforeEffects trace
theorem checked : contract = true := by decide
#eval contract
