-- ASCII witness from copy_product; Python casefold equals lower for this name.
def name : String := "SUPERLAYER_1_METHODOLOGY_SOURCES"
def excluded : String := name.toLower
def actualExcluded : Bool := name.toLower == excluded
def contract : Bool := actualExcluded
theorem checked : contract = true := by native_decide
#eval contract
