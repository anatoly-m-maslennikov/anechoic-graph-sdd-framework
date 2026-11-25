import Lean
open Lean
namespace WorkflowTrace

structure Event where
  kind : String
  name : String
  target : Option String
  outcome : Option String
  detail : Json
  deriving FromJson
structure Transition where
  event : String
  target : String
  expect : Json
  deriving FromJson
structure State where
  name : String
  final : Bool
  transitions : List Transition
  deriving FromJson
structure Model where
  initial : String
  states : List State
  deriving FromJson
structure Input where
  model : Model
  complete : Bool
  events : List Event
  deriving FromJson
structure Difference where
  state : String
  index : Nat
  reason : String
  deriving ToJson
structure Result where
  status : String
  firstDifference : Option Difference
  deriving ToJson

def validateExpect (j : Json) : Except String Unit := do
  let fields ← j.getObj?
  let _ ← j.getObjValAs? String "kind"
  for (key, value) in fields.toList do
    match key with
    | "kind" => pure ()
    | "target" | "outcome" =>
      let _ : Option String ← fromJson? value
      pure ()
    | "detail" => let _ ← value.getObj?; pure ()
    | _ => throw s!"unknown expect field: {key}"

def validate (input : Input) : Except String Unit := do
  let states := input.model.states
  if (states.map (·.name)).eraseDups.length != states.length then
    throw "duplicate state name"
  if !(states.any (fun s => s.name == input.model.initial)) then
    throw "initial state does not exist"
  for state in states do
    for t in state.transitions do
      if !(states.any (fun s => s.name == t.target)) then
        throw s!"unknown transition target: {t.target}"
      validateExpect t.expect
  for event in input.events do
    let _ ← event.detail.getObj?

def upperBound (value : Json) : Option Nat := do
  let .obj fields := value | none
  if fields.toList.length != 1 then none else do
    let bound ← fields.get? "at_most"
    bound.getNat?.toOption

def detailMatches (expected actual : Json) : Bool :=
  if expected == actual then true else
  match upperBound expected with
  | none => false
  | some bound =>
    let actualBound := upperBound actual <|> actual.getNat?.toOption
    actualBound.any (fun n => n <= bound)

def eventMatches (t : Transition) (e : Event) : Bool := Id.run do
  if t.event != e.name then return false
  let .ok fields := t.expect.getObj? | return false
  for (key, value) in fields.toList do
    let actual := match key with
      | "kind" => toJson e.kind
      | "target" => toJson e.target
      | "outcome" => toJson e.outcome
      | "detail" => e.detail
      | _ => Json.null
    if key == "detail" then
      let .ok expected := value.getObj? | return false
      let .ok observed := actual.getObj? | return false
      if !(expected.all fun k v => (observed.get? k).any (detailMatches v)) then return false
    else if value != actual then return false
  return true

def mismatchReason (transitions : List Transition) (event : Event) : String :=
  if !(transitions.any (fun t => t.event == event.name)) then
    "no transition for event name"
  else "event kind, target, outcome, or detail does not match transition expectations"

def check (model : Model) : String → List Event → Nat → Result
  | stateName, events, index =>
    match model.states.find? (fun s => s.name == stateName) with
    | none => ⟨"unresolved", none⟩
    | some state =>
      match events with
      | [] => if state.final then ⟨"matched", none⟩
              else ⟨"different", some ⟨stateName, index, "trace ended before a final state"⟩⟩
      | event :: rest =>
        if state.final then ⟨"different", some ⟨stateName, index, "event after final state"⟩⟩
        else
          match state.transitions.filter (fun t => eventMatches t event) with
          | [] => ⟨"different", some ⟨stateName, index, mismatchReason state.transitions event⟩⟩
          | [t] => check model t.target rest (index + 1)
          | _ => ⟨"unresolved", none⟩

def run (text : String) : Except String Json := do
  let json ← Json.parse text
  let input : Input ← fromJson? json
  validate input
  pure <| toJson (if input.complete then check input.model input.model.initial input.events 0 else ⟨"unresolved", none⟩)
end WorkflowTrace

def main : IO UInt32 := do
  let input ← (← IO.getStdin).readToEnd
  match WorkflowTrace.run input with
  | .ok json => (← IO.getStdout).putStrLn json.compress; pure 0
  | .error error => (← IO.getStderr).putStrLn error; pure 1
