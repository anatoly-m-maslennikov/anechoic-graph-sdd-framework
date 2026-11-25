-- Native Project selection and Compose property consumption are checked in source ASTs.
-- Startup requires the selected native Project to supply the backend property.
def contract (nativeSelected backendRequiresProperty propertyAvailable : Bool) : Bool :=
  !nativeSelected || !backendRequiresProperty || propertyAvailable
example : contract true true false = false := by decide
example : contract true true true = true := by decide
