"""Lean export binding check for the C88 witness."""

_EXPORT_CHECK = """
#eval show IO Unit from do
  let declared := AnechoicSpec.manifest >>= (·.getObjVal? "claim")
    >>= (·.getObjVal? "boundaries") >>= (·.getObjVal? "code")
    >>= (·.getObjVal? "exports")
    >>= (·.getObjVal? "_package__shared.compare_obligations")
  if !declared.isOk then
    throw (IO.userError "C88 public export missing from the Manifest")
  let (heap, globals) := initGlobals program 4000 moduleInits
  let name := "<module>LAYER_4_SPEC_COMPARISON_C88/_package__shared.py"
  let .ref facade := heap.getField globals name |
    throw (IO.userError "C88 public facade missing from translated model")
  let target := "LAYER_4_SPEC_COMPARISON_C88/top_down__pub.py:<module>." ++
    "compare_obligations"
  if heap.getField facade "compare_obligations" != .fn target then
    throw (IO.userError "C88 public facade does not bind the compared entry")
"""
