-- Direct-update, ordinary non-workflow result; `artifact` means key present.
-- These branch expressions were translated from NativeLifecycleProvider.call.
-- The earlier response contract follows the pre-regression provider's shape.
def before (completed artifact : Bool) : Bool := completed && artifact
def fixed (_completed _artifact : Bool) : Bool := false
def contract (artifactReturned : Bool) : Bool := !artifactReturned

-- A successful native direct update can return an artifact to the provider.
example : contract (before true true) = false := by decide
-- For all modeled inputs the fixed branch preserves the prior response shape.
theorem fixed_satisfies_contract (completed artifact : Bool) :
    contract (fixed completed artifact) = true := by
  cases completed <;> cases artifact <;> decide
