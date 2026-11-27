namespace WorkflowHandoff
open Autoform.Core Autoform.Generated.Implementation Lean

private def contractShape := Json.parse r#"{
  "action": "compile_workflow",
  "cases": [{
    "action": "compile_workflow", "output": "compiled",
    "same_values": [
      [["C75.workflow_model", "model"], ["C75.workflow_diagram", "model"]],
      [["C75.workflow_model", "model"], ["result", "model"]]
    ],
    "value_types": [
      [["C75.workflow_model", "model"], "object"],
      [["result", "mermaid"], "nonempty_string"]
    ],
    "must_effect": [
      ["C75.workflow_model", "normalized"],
      ["C75.workflow_diagram", "rendered"]
    ],
    "must_precede": [
      [["C75.workflow_model", "normalized"],
       ["C75.workflow_diagram", "rendered"]]
    ]
  }, {
    "action": "compile_workflow", "output": "invalid",
    "forbid_effect": ["C75.workflow_diagram"]
  }]
}"#

private def solutionShape := Json.parse r#"{
  "action": "compile_workflow", "initial": "normalize", "states": [{
    "name": "normalize", "final": false, "transitions": [{
      "event": "model_ready", "target": "render", "expect": {
        "kind": "effect", "target": "C75.workflow_model",
        "outcome": "normalized", "bind": {"workflow": "model"}
      }
    }, {
      "event": "error", "target": "end",
      "expect": {"kind": "output", "outcome": "invalid"}
    }]
  }, {
    "name": "render", "final": false, "transitions": [{
      "event": "diagram_ready", "target": "return", "expect": {
        "kind": "effect", "target": "C75.workflow_diagram",
        "outcome": "rendered", "same_as": {"model": "workflow"}
      }
    }]
  }, {
    "name": "return", "final": false, "transitions": [{
      "event": "result", "target": "end", "expect": {
        "kind": "output", "outcome": "compiled",
        "same_as": {"model": "workflow"}
      }
    }]
  }, {"name": "end", "final": true, "transitions": []}]
}"#

private def matchesAction (spec expected : Except String Json) : Bool :=
  let action := do
    let claim ← (← spec).getObjVal? "claim"
    let operations ← claim.getObjVal? "operations"
    operations.getObjVal? "compile_workflow"
  match action, expected with
  | .ok actual, .ok shape => actual == shape
  | _, _ => false

private def config := "workflow-source"
private def invalidConfig := "invalid"
private def diagram := "stateDiagram-v2"

private def logCall (event : String) : Stmt :=
  .setGlobal "probe_calls"
    (.binop "+" (.name "probe_calls") (.lit (.str event)))

private def normalizer : Func := {
  name := "probe.normalize_workflow"
  params := ["config"]
  body := .seq (logCall "normalize")
    (.seq (.setGlobal "probe_input" (.name "config"))
      (.ifte (.binop "==" (.name "config") (.lit (.str invalidConfig)))
        (.raise (.unop "py:exception:ValueError"
          (.tupleE [.lit (.str "invalid workflow")])))
        (.seq (.assign "normalized" (.dictE
          [(.lit (.str "id"), .lit (.str "normalized-workflow"))]))
          (.seq (.setGlobal "probe_model" (.name "normalized"))
            (.ret (.name "normalized")))))) }

private def renderer : Func := {
  name := "probe.render_workflow_diagram"
  params := ["model"]
  body := .seq (logCall " render")
    (.seq (.setGlobal "probe_render_arg" (.name "model"))
      (.seq (.setGlobal "probe_prior_model" (.name "probe_model"))
        (.ret (.lit (.str diagram))))) }

private def normalizerImport := "<absent:relative>" ++ String.intercalate "/" [
  "LAYER_2_FORMAL_SPECIFICATION_C94", "LAYER_2_SPEC_READING_C83",
  "SPECIFICATION_MODEL_C85", "_package__shared"]

private def rendererImport := "<absent:relative>" ++ String.intercalate "/" [
  "LAYER_2_FORMAL_SPECIFICATION_C94", "LAYER_3_MERMAID_RENDERER_C87",
  "_package__shared"]

private def moduleObject := "<module>workflow_model__pub.py"
private def entryName := "workflow_model__pub.py:<module>.compile_workflow"
private def fuel := 128

private def invoke (cfg : String) : Option (Heap × Ref × EResult) := do
  let (heap, globals) := initGlobals program fuel moduleInits
  let .ref address := heap.getField globals moduleObject | none
  guard (heap.getField address "normalize_workflow" == .fn normalizerImport)
  guard (heap.getField address "render_workflow_diagram" == .fn rendererImport)
  guard (heap.getField address "compile_workflow" == .fn entryName)
  let linked := {
    program with funcs := program.funcs ++ [normalizer, renderer] }
  let ctx : Ctx := {
    dialect := linked.dialect, table := linked.table, globals := globals }
  let entry ← ctx.resolve entryName
  let heap := heap.setField address "normalize_workflow" (.fn normalizer.name)
  let heap := heap.setField address "render_workflow_diagram"
    (.fn renderer.name)
  let heap := heap.setField globals "probe_calls" (.str "")
  let heap := heap.setField globals "probe_model" .unit
  let (heap, result) := applyFunc ctx fuel heap entry none [.str cfg] []
  return (heap, globals, result)

private def outputFields (heap : Heap) : EResult → List (Val × Val)
  | .val (.ref address) =>
    match heap.payload address with
    | .dict fields => fields
    | _ => []
  | _ => []

private def normalizedObject (heap : Heap) : Val → Bool
  | .ref address =>
    match heap.payload address with
    | .dict _ => true
    | _ => false
  | _ => false

private def successChecks (observation : Option (Heap × Ref × EResult)) :
    List (String × Bool) :=
  let keys := ["input", "ordered", "render_model", "return_model",
    "return_diagram"]
  match observation with
  | none => keys.map (·, false)
  | some (heap, globals, result) =>
    let probe := heap.getField globals
    let model := probe "probe_model"
    let fields := outputFields heap result
    let returned key :=
      (fields.find? (fun pair => pair.1 == .str key)).map Prod.snd
    keys.zip [
      probe "probe_input" == .str config,
      probe "probe_calls" == .str "normalize render" &&
        normalizedObject heap model && probe "probe_prior_model" == model,
      normalizedObject heap model && probe "probe_render_arg" == model,
      normalizedObject heap model && returned "model" == some model,
      !diagram.isEmpty && returned "mermaid" == some (.str diagram)]

private def invalidCheck : Bool :=
  match invoke invalidConfig with
  | some (heap, globals, .exn (.str error)) =>
    error == "ValueError" &&
    heap.getField globals "probe_input" == .str invalidConfig &&
    heap.getField globals "probe_calls" == .str "normalize"
  | _ => false

private def checks : List (String × Bool) :=
  let success := invoke config
  [("spec", matchesAction AnechoicSpec.contract contractShape &&
    matchesAction AnechoicSpec.solution solutionShape),
   ("imports", success.isSome),
   ("invalid", invalidCheck)] ++ successChecks success

#eval IO.println <|
  (Json.mkObj (checks.map fun (key, value) => (key, .bool value))).compress

end WorkflowHandoff
