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
    | "bind" | "same_as" =>
      for (_, name) in (← value.getObj?).toList do
        let _ ← name.getStr?
        pure ()
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

abbrev Bindings := List (String × Json)

def matchEvent (t : Transition) (e : Event) (bindings : Bindings) : Option Bindings := do
  guard (t.event == e.name)
  let fields ← t.expect.getObj?.toOption
  let observed ← e.detail.getObj?.toOption
  let mut updated := bindings
  for (key, value) in fields.toList do
    match key with
    | "kind" => guard (value == toJson e.kind)
    | "target" => guard (value == toJson e.target)
    | "outcome" => guard (value == toJson e.outcome)
    | "detail" =>
      let expected ← value.getObj?.toOption
      guard (expected.all fun k v => (observed.get? k).any (detailMatches v))
    | "same_as" =>
      for (detail, alias) in (← value.getObj?.toOption).toList do
        let expected ← bindings.lookup (← alias.getStr?.toOption)
        guard (observed.get? detail == some expected)
    | "bind" =>
      for (alias, detail) in (← value.getObj?.toOption).toList do
        let actual ← observed.get? (← detail.getStr?.toOption)
        match bindings.lookup alias with
        | none => updated := (alias, actual) :: updated
        | some expected => guard (actual == expected)
    | _ => failure
  return updated

def mismatchReason (transitions : List Transition) (event : Event) : String :=
  if !(transitions.any (fun t => t.event == event.name)) then
    "no transition for event name"
  else "event kind, target, outcome, or detail does not match transition expectations"

def check (model : Model) : String → List Event → Nat → Bindings → Result
  | stateName, events, index, bindings =>
    match model.states.find? (fun s => s.name == stateName) with
    | none => ⟨"unresolved", none⟩
    | some state =>
      match events with
      | [] => if state.final then ⟨"matched", none⟩
              else ⟨"different", some ⟨stateName, index, "trace ended before a final state"⟩⟩
      | event :: rest =>
        if state.final then ⟨"different", some ⟨stateName, index, "event after final state"⟩⟩
        else
          match state.transitions.filterMap (fun t => (matchEvent t event bindings).map ((t.target, ·))) with
          | [] => ⟨"different", some ⟨stateName, index, mismatchReason state.transitions event⟩⟩
          | [(target, updated)] => check model target rest (index + 1) updated
          | _ => ⟨"unresolved", none⟩

def run (text : String) : Except String Json := do
  let json ← Json.parse text
  let input : Input ← fromJson? json
  validate input
  pure <| toJson (if input.complete then check input.model input.model.initial input.events 0 [] else ⟨"unresolved", none⟩)
end WorkflowTrace

def main : IO UInt32 := do
  let input ← (← IO.getStdin).readToEnd
  match WorkflowTrace.run input with
  | .ok json => (← IO.getStdout).putStrLn json.compress; pure 0
  | .error error => (← IO.getStderr).putStrLn error; pure 1
