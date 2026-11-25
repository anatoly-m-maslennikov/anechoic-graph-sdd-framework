-- ASCII witness from copy_product; Python casefold equals lower for this name.
def name : String := "SUPERLAYER_1_METHODOLOGY_SOURCES"
def excluded : String := name
def actualExcluded : Bool := name.toLower == excluded
def contract : Bool := actualExcluded
theorem checked : contract = false := by native_decide
#eval contract
