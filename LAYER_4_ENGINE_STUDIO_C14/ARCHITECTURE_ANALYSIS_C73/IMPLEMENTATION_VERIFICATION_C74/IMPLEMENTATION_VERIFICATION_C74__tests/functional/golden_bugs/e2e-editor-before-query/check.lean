def checkedBeforeDispatch (input : Nat × List Nat)
    (checks : List (Nat × List Nat)) (dispatch : Nat) : Bool :=
  checks.any fun check =>
    input.1 < check.1 && check.1 < dispatch && input.2 == check.2

example : checkedBeforeDispatch (1, [7]) [] 2 = false := by decide
example : checkedBeforeDispatch (1, [7]) [(2, [8])] 3 = false := by decide
example : checkedBeforeDispatch (1, [7]) [(2, [7])] 3 = true := by decide
