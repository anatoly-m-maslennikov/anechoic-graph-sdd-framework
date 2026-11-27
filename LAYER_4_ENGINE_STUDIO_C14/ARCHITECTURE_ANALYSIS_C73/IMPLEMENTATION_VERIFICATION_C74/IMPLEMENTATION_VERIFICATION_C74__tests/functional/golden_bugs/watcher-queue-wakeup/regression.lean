-- The guard controls service when a lifecycle job is pending,
-- with no batch or retry.
def before (batch due lifecycle : Bool) : Bool := batch || due
def fixed (batch due lifecycle : Bool) : Bool := batch || due || lifecycle
example : before false false true = false := by decide
example : fixed false false true = true := by decide
