-- Facts extracted from the recognized Python AST, not runtime observations.
def backendImport : Bool := true
def directMcpInit : Bool := false
def contract : Bool := !backendImport && directMcpInit
theorem checked : contract = false := by decide
#eval contract
