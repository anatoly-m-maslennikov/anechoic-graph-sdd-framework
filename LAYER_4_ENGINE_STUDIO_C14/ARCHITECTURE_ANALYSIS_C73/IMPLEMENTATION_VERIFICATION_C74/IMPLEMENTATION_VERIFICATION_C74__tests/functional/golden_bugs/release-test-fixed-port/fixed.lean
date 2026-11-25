set_option linter.unusedVariables false
def accepts (port : Int) (isInt : Bool) : Bool := isInt && (1 ≤ port) && (port ≤ 65535)
def violates : Bool := !(accepts 51487 true)
example : accepts 0 true = false := by decide
example : accepts 65536 true = false := by decide
example : accepts 51487 false = false := by decide
#eval violates
