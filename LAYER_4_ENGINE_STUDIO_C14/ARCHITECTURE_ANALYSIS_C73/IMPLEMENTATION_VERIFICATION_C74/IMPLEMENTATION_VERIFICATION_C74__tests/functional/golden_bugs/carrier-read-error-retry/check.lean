-- Generated from checked Python ASTs; domain: prior read_error, unchanged signature, unrelated nonempty change.
def oldAttempt : Bool := false
example : oldAttempt = false := by decide
def fixedAttempt : Bool := true
example : fixedAttempt = true := by decide
-- Independent obligation: a previously failed source is re-read on the next capture.
def contract (attempt : Bool) : Bool := attempt
example : contract oldAttempt = false := by decide
example : contract fixedAttempt = true := by decide
