open Autoform.Core Autoform.Generated.Implementation

def record (fields : List (String × Val)) : Val :=
  .dict (fields.map fun (key, value) => (.str key, value))

def client : Val := record [
  ("component", .str "C84"), ("interface", .str "run_lean_json"),
  ("transport", .str "in_process")]

def carrier (parent component : String) (boundaries : Val) : Val := record [
  ("component_id", .str component),
  ("manifest", record [
    ("source", record [("container_component", .str parent)]),
    ("boundaries", boundaries)])]

def checkSibling (parent provider interface transport : String)
    (clients : Val) : EResult :=
  let caller := carrier "C94" "C86"
    (record [("io", record [("client", clients)])])
  let provider := carrier parent provider (record [])
  let (heap, globals) := initGlobals program 700 (moduleInits.take 1)
  let heap := heap.setField globals "dict" (.fn "dict")
  let heap := heap.setField globals "list" (.fn "list")
  let ctx : Ctx := {
    dialect := program.dialect, table := program.table, globals := globals,
    builtinBases := program.builtinBases, properties := program.properties,
    excClasses := program.excClasses, classDecls := program.classDecls }
  let entry := f_sibling_delegation__pub_py__module___require_sibling
  (applyFunc ctx 700 heap entry none
    [caller, provider, .str interface, .unit]
    [("transport", .str transport)]).2

def outcome : EResult → String
  | .val .unit => "accepted"
  | .exn (.str "ValueError") => "ValueError"
  | _ => "unresolved"

def clientList := Val.list [client]
def clientMap := record [("lean_evaluation", client)]

def probe (parent provider interface transport : String) (clients : Val) :
    Lean.Json :=
  .str (outcome (checkSibling parent provider interface transport clients))

#eval IO.println (Lean.Json.mkObj [
  ("matching_list", probe "C94" "C84" "run_lean_json" "in_process" clientList),
  ("wrong_parent", probe "C75" "C84" "run_lean_json" "in_process" clientList),
  ("wrong_provider",
    probe "C94" "C86" "run_lean_json" "in_process" clientList),
  ("wrong_interface",
    probe "C94" "C84" "compile_lean" "in_process" clientList),
  ("wrong_transport", probe "C94" "C84" "run_lean_json" "http" clientList),
  ("matching_map", probe "C94" "C84" "run_lean_json" "in_process" clientMap)
]).compress
