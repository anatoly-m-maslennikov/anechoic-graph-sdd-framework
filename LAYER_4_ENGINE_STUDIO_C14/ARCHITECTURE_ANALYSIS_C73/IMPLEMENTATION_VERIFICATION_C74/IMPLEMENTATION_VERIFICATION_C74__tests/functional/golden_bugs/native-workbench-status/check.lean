-- Membership expressions translated from the checked gateway and binding ASTs.
-- The dispatch and owner facts are checked against their source ASTs.
def beforeAdmitted : Bool := ((false || false || false || false) || ((false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false) || false || false || false))
def beforeDispatches : Bool := false
def beforeOwnerStatus : Bool := false
def beforeContract : Bool := beforeAdmitted && beforeDispatches && beforeOwnerStatus
def fixedAdmitted : Bool := ((false || false || false || false) || ((false || false || false || false || false || false || false || false || false || false || false || false || false || false || false || false) || false || false || false || true))
def fixedDispatches : Bool := true
def fixedOwnerStatus : Bool := true
def fixedContract : Bool := fixedAdmitted && fixedDispatches && fixedOwnerStatus
example : beforeAdmitted = false := by decide
example : beforeDispatches = false := by decide
example : beforeOwnerStatus = false := by decide
example : beforeContract = false := by decide
example : fixedAdmitted = true := by decide
example : fixedDispatches = true := by decide
example : fixedOwnerStatus = true := by decide
example : fixedContract = true := by decide
