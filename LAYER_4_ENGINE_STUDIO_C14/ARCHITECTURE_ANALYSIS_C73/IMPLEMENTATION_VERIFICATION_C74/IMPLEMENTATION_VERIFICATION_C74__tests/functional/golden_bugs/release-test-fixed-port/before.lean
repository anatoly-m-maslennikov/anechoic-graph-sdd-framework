set_option linter.unusedVariables false
def accepts (port : Int) (isInt : Bool) : Bool := port == 56317
def violates : Bool := !(accepts 51487 true)
#eval violates
