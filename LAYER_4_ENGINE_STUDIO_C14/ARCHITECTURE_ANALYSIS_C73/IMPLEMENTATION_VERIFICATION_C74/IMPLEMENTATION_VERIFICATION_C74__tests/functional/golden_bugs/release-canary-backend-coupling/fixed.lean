-- Facts extracted from the recognized Python AST, not runtime observations.
def backendImport : Bool := false
def directMcpInit : Bool := true
def contract : Bool := !backendImport && directMcpInit
theorem checked : contract = true := by decide
#eval contract
