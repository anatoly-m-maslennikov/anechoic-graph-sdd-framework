-- AST-extracted successful full-generation path; no claim about elapsed time.
def oldCaptureCheck : Nat := 1
def oldFinalCheck : Nat := 1
example : oldCaptureCheck + oldFinalCheck = 2 := by decide
def fixedCaptureCheck : Nat := 0
def fixedFinalCheck : Nat := 1
example : fixedCaptureCheck + fixedFinalCheck = 1 := by decide
example : fixedFinalCheck = 1 := by decide
