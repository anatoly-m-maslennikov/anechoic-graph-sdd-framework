import Lean

open Lean

namespace ActionEffects

structure Event where
  kind : String
  target : String
  name : String
  line : Nat
  forward : Option Bool := none
  deriving Repr

def optionalField [FromJson α] (j : Json) (key : String) : Except String
  (Option α) :=
  match j.getObjVal? key with
  | .error _ => pure none
  | .ok value => some <$> fromJson? value

instance : FromJson Event where
  fromJson? j := do
    pure ⟨← j.getObjValAs? String "kind", ← j.getObjValAs? String "target",
      ← j.getObjValAs? String "name", ← j.getObjValAs? Nat "line",
      ← optionalField j "forward"⟩

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
  unit : Option String := none

instance : FromJson Case where
  fromJson? j := do
    pure ⟨← j.getObjValAs? String "sourcePath", ← j.getObjValAs? Nat "line",
      ← j.getObjVal? "input", ← j.getObjValAs? Bool "reachable",
      ← j.getObjValAs? Bool "complete", ← j.getObjValAs? Bool "declaredNoOp",
      ← j.getObjValAs? (List Event) "events", ← j.getObjValAs? Policy "policy",
      ← optionalField j "unit"⟩

structure PublicEvent where
  kind : String
  target : String
  name : String
  line : Nat
  sourcePath : Option String := none
  deriving ToJson, Repr

structure Violation where
  index : Nat
  kind : String
  target : String
  name : String
  line : Nat
  sourcePath : Option String := none
  deriving ToJson, Repr

structure Result where
  sourcePath : String
  line : Nat
  input : Json
  status : String
  deadEnd : Bool
  violations : List Violation
  events : List PublicEvent
  deriving ToJson

def validEvent (e : Event) : Bool :=
  e.line > 0 && (if e.kind == "call" then e.target == "" && e.name != ""
    else if e.kind == "output" || e.kind == "return" || e.kind == "raise"
      then e.target == "" && e.name == ""
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
    (g.mode == "rw" || (if e.kind == "read" then g.mode == "r" else g.mode ==
      "w")))

structure Emitted where
  event : PublicEvent
  allowed : Bool

-- The remaining budget is threaded through calls and continuations.
partial def expand (units : Std.HashMap String Case) (rootPath : String)
    (c : Case) (stack : List String) (pureAncestor observe : Bool)
    (events : List Event) (budget : Nat) : Except String (List Emitted × Bool
      × Nat) := do
  match events, budget with
  | [], _ => pure ([], false, budget)
  | _, 0 => throw "budget"
  | e :: rest, n + 1 =>
    if e.kind == "call" then
      let target ← match units[e.name]? with
        | some target => pure target
        | none => throw "missing target"
      if !target.reachable || !target.complete || stack.length >= 32 ||
        stack.contains e.name then
        throw "unresolved target"
      let (called, raised, left) ← expand units rootPath target (e.name ::
        stack)
        (pureAncestor || c.policy.kind == "pure") (observe && e.forward ==
          some true) target.events n
      if raised then pure (called, true, left)
      else
        let (tail, terminated, left) ← expand units rootPath c stack
          pureAncestor observe rest left
        pure (called ++ tail, terminated, left)
    else if e.kind == "return" then
      let out : PublicEvent := ⟨"output", "", "", e.line,
        if c.sourcePath == rootPath then none else some c.sourcePath⟩
      pure (if observe then [⟨out, true⟩] else [], false, n)
    else if e.kind == "raise" then
      let out : PublicEvent := ⟨"output", "", "", e.line,
        if c.sourcePath == rootPath then none else some c.sourcePath⟩
      pure ([⟨out, true⟩], true, n)
    else
      let out : PublicEvent := ⟨e.kind, e.target, e.name, e.line,
        if c.sourcePath == rootPath then none else some c.sourcePath⟩
      let allowed := permitted c.policy e && !(pureAncestor && (e.kind ==
        "read" || e.kind == "write"))
      let (tail, terminated, left) ← expand units rootPath c stack
        pureAncestor observe rest n
      pure (⟨out, allowed⟩ :: tail, terminated, left)

def classifyWith (units : Std.HashMap String Case)
    (c : Case) : Result := Id.run do
  let expanded := if c.reachable && c.complete then
    expand units c.sourcePath c (c.unit.toList) false true c.events 10000
    else .ok ([], false, 0)
  let unresolved := !c.complete || (match expanded with
    | .error _ => true
    | .ok _ => false)
  let emitted := match expanded with | .ok (es, _, _) => es | .error _ => []
  let dead := c.reachable && !unresolved &&
    !(emitted.any fun e => e.event.kind == "write" || e.event.kind == "output")
  let status := if unresolved then "unresolved" else if !c.reachable then
    "unreachable"
    else if dead && c.declaredNoOp then "declaredNoOp"
    else if dead then "deadEnd" else "hasEffects"
  let findings := emitted.zipIdx.filterMap fun (e, i) =>
    if e.allowed then none else some ⟨i, e.event.kind, e.event.target,
      e.event.name,
      e.event.line, e.event.sourcePath⟩
  return ⟨c.sourcePath, c.line, c.input, status, dead && !c.declaredNoOp,
    findings, emitted.map (·.event)⟩

def classify (c : Case) : Result := classifyWith {} c

def run (input : String) : Except String Json := do
  let json ← Json.parse input
  let cases : List Case ← fromJson? json
  if cases.any (fun c => c.sourcePath == "" || c.line == 0 ||
      !validPolicy c.policy || !c.events.all validEvent || c.unit == some "")
        then
    throw "Invalid source location, policy, grant, or event"
  let mut units : Std.HashMap String Case := {}
  for c in cases do
    if let some unit := c.unit then
      if units.contains unit then throw "Duplicate unit"
      units := units.insert unit c
  pure (toJson (cases.map (classifyWith units)))

private def silent : Case :=
  ⟨"action.py", 1, Json.null, true, true, false, [], ⟨"pure", "", []⟩, none⟩

example : (classify silent).deadEnd = true := by native_decide
example : (classify { silent with complete := false }).status = "unresolved"
  := rfl
example : (classify { silent with events := [⟨"write", "local", "x", 2, none⟩,
    ⟨"write", "local", "x", 3, none⟩] }).deadEnd = false := by native_decide
example : permitted ⟨"local", "x", [⟨"net", "r"⟩]⟩
    ⟨"write", "ambient", "net", 2, none⟩ = false := rfl

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
