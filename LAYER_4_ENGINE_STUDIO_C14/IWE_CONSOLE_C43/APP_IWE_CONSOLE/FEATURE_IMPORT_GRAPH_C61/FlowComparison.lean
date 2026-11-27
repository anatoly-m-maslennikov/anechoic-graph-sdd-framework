import Lean

open Lean

namespace FlowComparison

-- Each event is one observable occurrence; detail must be a JSON object.
structure Event where
  kind : String
  name : String
  target : Option String
  outcome : Option String
  detail : Json
  deriving ToJson, BEq

instance : FromJson Event where
  fromJson? j := do
    let target ← j.getObjVal? "target"
    let outcome ← j.getObjVal? "outcome"
    let detail ← j.getObjVal? "detail"
    match detail with
    | .obj _ => pure ⟨← j.getObjValAs? String "kind", ← j.getObjValAs? String "name",
        ← fromJson? target, ← fromJson? outcome, detail⟩
    | _ => throw "detail must be an object"

structure Trace where
  complete : Bool
  events : List Event
  deriving FromJson

structure Input where
  inputsAligned : Bool
  left : Trace
  right : Trace
  deriving FromJson

structure Difference where
  index : Nat
  left : Option Event
  right : Option Event
  deriving ToJson

structure Result where
  status : String
  firstDifference : Option Difference
  deriving ToJson

def firstDifference : List Event → List Event → Nat → Option Difference
  | [], [], _ => none
  | [], r :: _, i => some ⟨i, none, some r⟩
  | l :: _, [], i => some ⟨i, some l, none⟩
  | l :: ls, r :: rs, i =>
    if l == r then firstDifference ls rs (i + 1)
    else some ⟨i, some l, some r⟩

def compare (input : Input) : Result :=
  if !input.inputsAligned || !input.left.complete || !input.right.complete then
    ⟨"unresolved", none⟩
  else match firstDifference input.left.events input.right.events 0 with
    | none => ⟨"matched", none⟩
    | some difference => ⟨"different", some difference⟩

def run (input : String) : Except String Json := do
  let json ← Json.parse input
  let value : Input ← fromJson? json
  pure (toJson (compare value))

end FlowComparison

def main : IO UInt32 := do
  let input ← (← IO.getStdin).readToEnd
  match FlowComparison.run input with
  | .ok json =>
    (← IO.getStdout).putStrLn json.compress
    pure 0
  | .error error =>
    (← IO.getStderr).putStrLn error
    pure 1
