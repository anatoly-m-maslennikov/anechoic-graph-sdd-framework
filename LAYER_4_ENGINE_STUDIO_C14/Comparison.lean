import Lean
def exactInteger (value : Lean.Json) : Option Int := do
  let .num number := value | none
  let scale : Int := Int.ofNat (10 ^ number.exponent)
  if number.mantissa % scale == 0 then some (number.mantissa / scale)
  else none
def exactNatural (value : Lean.Json) : Option Nat := do
  let number ← exactInteger value
  if number < 0 then none else some number.toNat
def upperBound (value : String) : Option Nat := do
  let json ← (Lean.Json.parse value).toOption
  let .obj entries := json | none
  if entries.foldl (init := 0) (fun n _ _ => n + 1) != 1 then none else do
    let bound ← (json.getObjVal? "at_most").toOption
    bound.getNat?.toOption
def detailImplies (actual required : String) : Bool :=
  if actual == required then true else
  if match (Lean.Json.parse actual).toOption, (Lean.Json.parse required).toOption with
     | some (.num a), some (.num b) => a.normalize == b.normalize
     | _, _ => false then true else
  match upperBound required with
  | none => false
  | some bound =>
    let actualBound := upperBound actual <|>
      ((Lean.Json.parse actual).toOption >>= exactNatural)
    actualBound.any (fun n => n <= bound)
structure Effect where
  observed : String
  outcome : String
  detail : List (String × String)
def implies (actual required : Effect) : Bool :=
  actual.observed == required.observed && actual.outcome == required.outcome &&
  required.detail.all (fun pair => actual.detail.any (fun found => found.1 == pair.1 && detailImplies found.2 pair.2))
#eval IO.println (Lean.toJson [if ([⟨"C90.source_diagnostic", "formed", []⟩] : List Effect).any (fun actual => implies actual ⟨"C90.source_diagnostic", "formed", []⟩) then "matched" else "conflicting"]).compress
