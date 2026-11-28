def leftLower : Bool := false
def rightLower : Bool := false
def norm (s : String) (lower : Bool) : String := if lower then s.toLower else s
def rebuilds : Bool := norm "atoms" leftLower == norm "ATOMS" rightLower
#eval rebuilds
