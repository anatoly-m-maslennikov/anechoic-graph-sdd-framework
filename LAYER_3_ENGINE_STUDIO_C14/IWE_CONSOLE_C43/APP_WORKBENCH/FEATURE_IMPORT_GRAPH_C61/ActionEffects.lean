import Lean

open Lean

namespace ActionEffects

structure Event where
  kind : String
  target : String
  name : String
  line : Nat
  deriving FromJson, ToJson, Repr

structure Grant where
  channel : String
  mode : String
  deriving FromJson, ToJson, Repr

structure Policy where
  kind : String
  owner : String
  grants : List Grant
  deriving FromJson, ToJson, Repr

structure Case where
  sourcePath : String
  line : Nat
  input : Json
  reachable : Bool
  complete : Bool
  declaredNoOp : Bool
  events : List Event
  policy : Policy
  deriving FromJson

structure Violation where
  index : Nat
  kind : String
  target : String
  name : String
  line : Nat
  deriving ToJson, Repr

structure Result where
  sourcePath : String
  line : Nat
  input : Json
  status : String
  deadEnd : Bool
  violations : List Violation
  deriving ToJson

def validEvent (e : Event) : Bool :=
  e.line > 0 && (if e.kind == "output" then e.target == "" && e.name == ""
    else (e.kind == "read" || e.kind == "write") &&
      (e.target == "local" || e.target == "ambient") && e.name != "")

def validPolicy (p : Policy) : Bool :=
  (p.kind == "pure" || (p.kind == "local" && p.owner != "")) &&
  p.grants.all (fun g => g.channel != "" &&
    (g.mode == "r" || g.mode == "w" || g.mode == "rw"))

def permitted (p : Policy) (e : Event) : Bool :=
  if e.kind == "output" then true
  else if p.kind == "pure" then false
  else if e.target == "local" then e.name == p.owner
  else p.grants.any (fun g => g.channel == e.name &&
    (g.mode == "rw" || (if e.kind == "read" then g.mode == "r" else g.mode == "w")))

def violations (p : Policy) (events : List Event) : List Violation :=
  (events.zipIdx.filterMap fun (e, i) =>
    if permitted p e then none else some ⟨i, e.kind, e.target, e.name, e.line⟩)

def isDeadEnd (c : Case) : Bool :=
  c.reachable && c.complete &&
    !(c.events.any fun e => e.kind == "write" || e.kind == "output")

def classify (c : Case) : Result :=
  let dead := isDeadEnd c
  let status := if !c.complete then "unresolved"
    else if !c.reachable then "unreachable"
    else if dead && c.declaredNoOp then "declaredNoOp"
    else if dead then "deadEnd" else "hasEffects"
  ⟨c.sourcePath, c.line, c.input, status, dead && !c.declaredNoOp,
    violations c.policy c.events⟩

def run (input : String) : Except String Json := do
  let json ← Json.parse input
  let cases : List Case ← fromJson? json
  if cases.any (fun c => c.sourcePath == "" || c.line == 0 ||
      !validPolicy c.policy || !c.events.all validEvent) then
    throw "Invalid source location, policy, grant, or event"
  pure (toJson (cases.map classify))

private def silent : Case :=
  ⟨"action.py", 1, Json.null, true, true, false, [], ⟨"pure", "", []⟩⟩

example : isDeadEnd silent = true := rfl
example : (classify { silent with complete := false }).status = "unresolved" := rfl
example : isDeadEnd { silent with events := [⟨"write", "local", "x", 2⟩,
    ⟨"write", "local", "x", 3⟩] } = false := rfl
example : permitted ⟨"local", "x", [⟨"net", "r"⟩]⟩
    ⟨"write", "ambient", "net", 2⟩ = false := rfl

end ActionEffects

def main : IO UInt32 := do
  let input ← (← IO.getStdin).readToEnd
  match ActionEffects.run input with
  | .ok json =>
    (← IO.getStdout).putStrLn json.compress
    pure 0
  | .error error =>
    (← IO.getStderr).putStrLn error
    pure 1
