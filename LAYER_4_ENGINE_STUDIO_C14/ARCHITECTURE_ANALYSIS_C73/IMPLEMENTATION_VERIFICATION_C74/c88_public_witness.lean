open Autoform.Core Autoform.Generated.Implementation

namespace C88PublicWitness

def moduleName := "<module>LAYER_4_SPEC_COMPARISON_C88/top_down__pub.py"
def gen := f_LAYER_4_SPEC_COMPARISON_C88_top_down__pub_py__module___program
def publicEntry :=
  f_LAYER_4_SPEC_COMPARISON_C88_top_down__pub_py__module__compare_obligations

def fresh (g : Ref) : Ctx := {
  dialect := program.dialect, table := program.table, globals := g,
  builtinBases := program.builtinBases, properties := program.properties,
  excClasses := program.excClasses, classDecls := program.classDecls }

def obligations : Val := .dict [
  (.str "manifest", .dict [
    (.str "z", .int 1), (.str "m", .int 8), (.str "a", .int 2)]),
  (.str "contract", .dict [(.str "z", .int 1), (.str "a", .int 2)]),
  (.str "solution", .dict [(.str "z", .int 3), (.str "a", .int 2)])]

def expectedDecls := String.intercalate "" [
  "def manifest : List (String × String) :=",
  " [(\"a\", \"2\"), (\"m\", \"8\"), (\"z\", \"1\")]\nde",
  "f contract : List (String × String) := [",
  "(\"a\", \"2\"), (\"z\", \"1\")]\ndef solution : L",
  "ist (String × String) := [(\"a\", \"2\"), (\"",
  "z\", \"3\")]"]
def expectedCalls :=
  "compare manifest contract, compare manifest solution, " ++
  "compare contract solution"
def expectedRows : List (List String) :=
  [["matched", "unresolved", "matched"],
   ["matched", "unresolved", "conflicting"],
   ["matched", "conflicting"]]
def expectedPairs : Expr := .tupleE [
  .tupleE [.lit (.str "manifest"), .lit (.str "contract")],
  .tupleE [.lit (.str "manifest"), .lit (.str "solution")],
  .tupleE [.lit (.str "contract"), .lit (.str "solution")]]
def expectedRoles : Expr := .tupleE [
  .lit (.str "manifest"), .lit (.str "contract"), .lit (.str "solution")]

def fact (key : String) (left right : Val) (status : String) : Val := .dict [
  (.str "key", .str key), (.str "left", left), (.str "right", right),
  (.str "status", .str status)]
def direction (status : String) (facts : List Val) : Val := .dict [
  (.str "status", .str status), (.str "facts", .list facts)]
def expectedReport : Val := .dict [
  (.str "status", .str "conflicting"), (.str "sources", c88ObservedSources),
  (.str "directions", .dict [
    (.str "manifest_contract", direction "unresolved" [
      fact "a" (.int 2) (.int 2) "matched",
      fact "m" (.int 8) .unit "unresolved",
      fact "z" (.int 1) (.int 1) "matched"]),
    (.str "manifest_solution", direction "conflicting" [
      fact "a" (.int 2) (.int 2) "matched",
      fact "m" (.int 8) .unit "unresolved",
      fact "z" (.int 1) (.int 3) "conflicting"]),
    (.str "contract_solution", direction "conflicting" [
      fact "a" (.int 2) (.int 2) "matched",
      fact "z" (.int 1) (.int 3) "conflicting"])])]

def guarded (name : String) (test : Expr) (body : Stmt) : Stmt :=
  .ifte test body (.expr (.hole ("unmatched observation: " ++ name)))

def rewriteJoins : Stmt → Stmt × Nat × Nat
  | .seq (.assign "tmp2" (.lit (.str "\n")))
      (.assign "declarations"
        (.mcall (.name "tmp2") "join" [.hole "expr:genExp"])) =>
    (.seq (.assign "tmp2" (.lit (.str "\n")))
      (.assign "declarations" (.lit (.str c88ObservedDeclarations))), 1, 0)
  | .seq (.assign "tmp6" (.lit (.str ", ")))
      (.assign "calls"
        (.mcall (.name "tmp6") "join" [.hole "expr:genExp"])) =>
    (.seq (.assign "tmp6" (.lit (.str ", ")))
      (.assign "calls" (.lit (.str c88ObservedCalls))), 0, 1)
  | .seq a b =>
    let (a', ad, ac) := rewriteJoins a
    let (b', bd, bc) := rewriteJoins b
    (.seq a' b', ad + bd, ac + bc)
  | other => (other, 0, 0)

def bridgedBody : Stmt :=
  let (body, declarations, calls) := rewriteJoins gen.body
  if declarations == 1 && calls == 1 then body
  else .expr (.hole "unexpected join statements")

def renderWorker : EResult :=
  let (h, g) := initGlobals program 2000 moduleInits
  let worker := {gen with body := bridgedBody}
  let pairs := Val.tuple [
    .tuple [.str "manifest", .str "contract"],
    .tuple [.str "manifest", .str "solution"],
    .tuple [.str "contract", .str "solution"]]
  let roles := Val.dict [(.str "manifest", .unit), (.str "contract", .unit),
    (.str "solution", .unit)]
  (applyFunc (fresh g) 2000 h worker none [obligations, pairs, roles] []).2

def withJoins : Func :=
  let guardedBody := guarded "obligations"
    (.binop "==" (.name "obligations") (.name "observedObligations"))
    (guarded "pairs" (.binop "==" (.name "directions") expectedPairs)
      (guarded "roles"
        (.binop "==" (.call "tuple" [(.mcall (.name "roles") "keys" [])])
        expectedRoles) bridgedBody))
  {gen with body := guardedBody}
def externalRunner : Func :=
  {name := "observedRunner", params := ["text", "lean"],
   body := guarded "lean"
     (.binop "==" (.name "lean") (.lit (.str c88ObservedRunner)))
     (guarded "program"
       (.binop "==" (.name "text") (.lit (.str c88ObservedWorker)))
       (.ret (.name "observedRows")))}
def execute : Heap × EResult :=
  let (h, g) := initGlobals program 2000 moduleInits
  let h := ((h.setField g "dict" (.fn "dict")).setField g "str" (.fn "str"))
    |>.setField g "list" (.fn "list")
  let rows : Val := .list (c88ObservedRows.map fun row =>
    .list (row.map Val.str))
  let h := (h.setField g "observedObligations" obligations)
    |>.setField g "observedRows" rows
  match h.getField g moduleName with
  | .ref r =>
    let h := h.setField r "run_lean_json" (.fn "observedRunner")
    let ctx := {(fresh g) with table :=
      [(withJoins.name, withJoins), (externalRunner.name, externalRunner)] ++
        program.table}
    applyFunc ctx 2000 h publicEntry none [c88ObservedSources, obligations]
      [("lean", .str c88ObservedRunner)]
  | _ => (h, .hole "module object missing")

def freeze : Nat → Heap → Val → Val
  | 0, _, v => v
  | n+1, h, .ref addr => match h.payload addr with
    | .dict rows => .dict (rows.map fun (k, v) => (freeze n h k, freeze n h v))
    | .list items => .list (items.map (freeze n h))
    | _ => .ref addr
  | n+1, h, .dict rows => .dict (rows.map fun (k, v) =>
      (freeze n h k, freeze n h v))
  | n+1, h, .list items => .list (items.map (freeze n h))
  | _, _, v => v

partial def valueJson : Val → Lean.Json
  | .unit => .null
  | .str s => .str s
  | .int i => Lean.toJson i
  | .list xs => Lean.toJson (xs.map valueJson)
  | .dict xs => Lean.Json.mkObj (xs.filterMap fun pair => match pair with
      | (.str key, value) => some (key, valueJson value)
      | _ => none)
  | _ => .str "unsupported model value"

partial def typedEqual : Val → Val → Bool
  | .unit, .unit => true
  | .str a, .str b => a == b
  | .int a, .int b => a == b
  | .bool a, .bool b => a == b
  | .list a, .list b =>
    a.length == b.length && (a.zip b).all (fun p => typedEqual p.1 p.2)
  | .dict a, .dict b =>
    a.length == b.length && (a.zip b).all (fun p =>
      typedEqual p.1.1 p.2.1 && typedEqual p.1.2 p.2.2)
  | _, _ => false

def directionOrder (actual : Val) : List String :=
  match actual with
  | .dict fields => match Stdlib.dictGet fields (.str "directions") with
    | some (.dict directions) => directions.filterMap fun pair =>
      match pair.1 with | .str name => some name | _ => none
    | _ => []
  | _ => []

def onlyFields (value : Lean.Json) (names : List String) : Bool :=
  match value.getObj? with
  | .ok fields => fields.size == names.length &&
      names.all (fun name => (value.getObjVal? name).isOk)
  | .error _ => false

def stateAt (states : Array Lean.Json) (name : String) :
    Except String Lean.Json := do
  match states.find? (fun s =>
      (s.getObjValAs? String "name").toOption == some name) with
  | some state => pure state
  | none => throw "Solution state missing"

def nextState (states : Array Lean.Json) (name event : String)
    (guard : Lean.Json) : Except String String := do
  let state ← stateAt states name
  if !onlyFields state ["name", "final", "transitions"] then
    throw "Unsupported Solution state fields"
  if (← state.getObjValAs? Bool "final") then
    throw "Solution reached final state early"
  let edges ← state.getObjValAs? (List Lean.Json) "transitions"
  let [edge] := edges | throw "Solution path is not single-valued"
  if !onlyFields edge ["event", "target", "expect"] ||
     (← edge.getObjValAs? String "event") != event ||
     (← edge.getObjVal? "expect") != guard then
    throw "Solution guard differs from observed path"
  edge.getObjValAs? String "target"

def effectGuard (name : String) : Lean.Json := Lean.Json.mkObj [
  ("kind", .str "effect"), ("target", .str ("C88." ++ name)),
  ("outcome", .str "compared")]

def followEffects (states : Array Lean.Json) :
    Nat → String → List String → Except String String
  | _, name, [] => pure name
  | index, name, direction :: rest => do
    let next ← nextState states name s!"effect{index}"
      (effectGuard direction)
    followEffects states (index + 1) next rest

def checkFormal (directions : List String) : Except String Unit := do
  let manifest ← (← AnechoicSpec.manifest).getObjVal? "claim"
  let contract ← (← AnechoicSpec.contract).getObjVal? "claim"
  let solution ← (← AnechoicSpec.solution).getObjVal? "claim"
  let boundaries ← manifest.getObjVal? "boundaries"
  let io ← boundaries.getObjVal? "io"
  let server ← io.getObjVal? "server"
  let action ← server.getObjVal? "compare_obligations"
  let outcomes ← action.getObjVal? "outcomes"
  let compared ← outcomes.getObjVal? "compared"
  if !onlyFields action ["outcomes"] || !onlyFields outcomes ["compared"] ||
     !onlyFields compared ["must_effect"] ||
     !onlyFields contract ["action", "output", "must_effect"] ||
     !onlyFields solution ["action", "initial", "states"] then
    throw "Unsupported authored claim fields"
  let manifestEffects ← compared.getObjValAs? (List Lean.Json) "must_effect"
  let contractEffects ← contract.getObjValAs? (List Lean.Json) "must_effect"
  let expected := directions.map fun name =>
    Lean.Json.arr #[.str ("C88." ++ name), .str "compared"]
  if manifestEffects != expected || contractEffects != expected ||
     (← contract.getObjValAs? String "action") != "compare_obligations" ||
     (← contract.getObjValAs? String "output") != "compared" ||
     (← solution.getObjValAs? String "action") != "compare_obligations" then
    throw "Manifest or Contract differs from the public directions"
  let states ← (← solution.getObjVal? "states").getArr?
  if states.size != directions.length + 3 then
    throw "Unsupported Solution states"
  let initial ← solution.getObjValAs? String "initial"
  let first ← nextState states initial "request"
    (Lean.Json.mkObj [("kind", .str "trigger")])
  let output ← followEffects states 0 first directions
  let final ← nextState states output "return" (Lean.Json.mkObj [
    ("kind", .str "output"), ("outcome", .str "compared")])
  let state ← stateAt states final
  if !onlyFields state ["name", "final", "transitions"] ||
     !(← state.getObjValAs? Bool "final") ||
     !(← state.getObjValAs? (List Lean.Json) "transitions").isEmpty then
    throw "Solution output is not final"

def workerMatches : Bool :=
  match renderWorker with
  | .val (.str worker) => worker == c88ObservedWorker
  | _ => false

def result : Lean.Json :=
  if c88ObservedDeclarations != expectedDecls ||
     c88ObservedCalls != expectedCalls ||
     c88ObservedRows != expectedRows then
    Lean.Json.mkObj [("status", .str "unresolved"),
      ("reason", .str "unmatched fixture observation")]
  else if !workerMatches then
    Lean.Json.mkObj [("status", .str "unresolved"),
      ("reason", .str "rendered worker differs from observation")]
  else match execute with
    | (h, .val value) =>
      let actual := freeze 20 h value
      let formal := checkFormal (directionOrder actual)
      let status := if !typedEqual actual expectedReport then "conflicting"
                    else if formal.isOk then "matched" else "unresolved"
      Lean.Json.mkObj [("status", .str status),
        ("report", valueJson actual),
        ("direction_order", Lean.toJson (directionOrder actual)),
        ("formal_path", .str (if formal.isOk then "matched"
          else "unresolved")),
        ("unresolved", Lean.toJson (["Python facade initialization",
          "runtime effect events", "other inputs and effects"] : List String)),
        ("observations", Lean.toJson (["native join strings",
          "real Lean worker rows"] : List String))]
    | (_, .hole reason) => Lean.Json.mkObj [("status", .str "unresolved"),
        ("reason", .str reason)]
    | (_, other) => Lean.Json.mkObj [("status", .str "unresolved"),
        ("reason", .str (reprStr other))]

#eval IO.println result.compress

end C88PublicWitness
