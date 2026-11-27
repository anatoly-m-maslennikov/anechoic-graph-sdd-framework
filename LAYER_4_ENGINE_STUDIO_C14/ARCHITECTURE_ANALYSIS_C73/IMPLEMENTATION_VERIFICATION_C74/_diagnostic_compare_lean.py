"""Lean checks used by the comparison."""

_VERDICT_STATEMENT = (
    "\nexample (xs : List String) : ∃ output : Stri"
    'ng,\n    (declaredVerdict (decide ("conflictin'
    'g" ∈ xs))\n      (xs.isEmpty || ("unresolved" '
    "∈ xs : Bool))).toOption = some output ∧\n    ("
    'solutionVerdict (decide ("conflicting" ∈ xs))'
    '\n      (xs.isEmpty || ("unresolved" ∈ xs : Bo'
    "ol))).toOption = some output ∧\n    invokePubl"
    "icVerdict xs = .val (.str output) :=\n  public"
    "VerdictMatchesContract xs\n"
)

_CHECK = (
    "\nopen Autoform.Core Autoform.Generated.Implem"
    "entation\n\nabbrev Field := String × String\nabb"
    "rev Obligation := Field × Field\n\ndef findingI"
    'nputs : List (String × Val) :=\n  [("source", '
    '.str "AN-S-4937@2"), ("field", .str "relation'
    's.ANSWERS"), ("message", .str "Missing relati'
    'on")]\n\ndef findingContext (globals : Ref) : C'
    "tx := {\n    dialect := program.dialect, table"
    " := program.table, globals := globals,\n    bu"
    "iltinBases := program.builtinBases, propertie"
    "s := program.properties,\n    excClasses := pr"
    "ogram.excClasses, classDecls := program.class"
    "Decls }\n\ndef invokeFinding (target : String) "
    "(heap : Heap) (globals : Ref) (inputs : List "
    "Val) : Heap × EResult :=\n  let ctx := finding"
    "Context globals\n  match ctx.resolve target wi"
    'th\n  | none => (heap, .hole "C90 finding was '
    'not translated")\n  | some entry => applyFunc '
    "ctx 200 heap entry none inputs []\n\ndef findin"
    "gResult : String × List (Val × Val) :=\n  let "
    "(heap, globals) := initGlobals program 200 mo"
    'duleInits\n  match readExport heap globals "fi'
    'nding" with\n  | none => ("unresolved", [])\n  '
    "| some target =>\n    match invokeFinding targ"
    "et heap globals (findingInputs.map Prod.snd) "
    "with\n    | (finalHeap, .val (.ref ref)) =>\n  "
    "    match finalHeap.payload ref with\n      | "
    '.dict rows => ("observed", rows)\n      | _ =>'
    ' ("conflicting", [])\n    | (_, .hole _) | (_,'
    ' .outOfFuel) => ("unresolved", [])\n    | _ =>'
    ' ("conflicting", [])\n\ndef stateAt (states : A'
    "rray Lean.Json) (name : String) : Except Stri"
    "ng Lean.Json :=\n  match states.find? (fun sta"
    'te => (state.getObjValAs? String "name").toOp'
    "tion == some name) with\n  | some state => .ok"
    ' state\n  | none => .error "Missing Solution s'
    'tate"\n\ndef soleEdge (states : Array Lean.Json'
    ") (name : String) : Except String Lean.Json :"
    "= do\n  let edges ← (← stateAt states name).ge"
    'tObjValAs? (List Lean.Json) "transitions"\n  m'
    "atch edges with\n  | [edge] => pure edge\n  | _"
    ' => throw "Expected a single Solution transit'
    'ion"\n\ndef guardFor (edge : Lean.Json) (kind :'
    " String) (fields : List String) : Except Stri"
    "ng Lean.Json := do\n  let guard ← edge.getObjV"
    'al? "expect"\n  let .obj keys := guard | throw'
    ' "Expected Solution guard"\n  if (← guard.getO'
    'bjValAs? String "kind") == kind &&\n     keys.'
    'all (fun key _ => key == "kind" || fields.con'
    'tains key)\n  then pure guard else throw "Unsu'
    'pported Solution guard"\n\ndef findingPath (wor'
    "kflow : Lean.Json) (output : String) :\n    Ex"
    "cept String (Lean.Json × Lean.Json × Lean.Jso"
    "n) := do\n  if (← workflow.getObjValAs? String"
    ' "action") != "finding" then throw "Expected '
    'the finding Action"\n  let states ← (← workflo'
    'w.getObjVal? "states").getArr?\n  let request '
    "← soleEdge states (← workflow.getObjValAs? St"
    'ring "initial")\n  let effect ← soleEdge state'
    's (← request.getObjValAs? String "target")\n  '
    "let result ← soleEdge states (← effect.getObj"
    'ValAs? String "target")\n  let final ← stateAt'
    ' states (← result.getObjValAs? String "target'
    '")\n  let effectGuard ← guardFor effect "effec'
    't" ["target", "outcome"]\n  let outputGuard ← '
    'guardFor result "output" ["outcome", "same_as'
    '"]\n  if !(← final.getObjValAs? Bool "final") '
    '|| (← outputGuard.getObjValAs? String "outcom'
    'e") != output\n  then throw "Solution path doe'
    's not reach the selected output"\n  pure (requ'
    "est, effectGuard, result)\n\ndef solutionCheck "
    "(path : Except String (Lean.Json × Lean.Json "
    "× Lean.Json)) (left right : Field) : String :"
    "=\n  let mapping : Except String String := do\n"
    "    let (request, _, result) ← path\n    if (←"
    ' request.getObjValAs? String "event") != left'
    '.1 ||\n       (← result.getObjValAs? String "e'
    'vent") != right.1 then throw "Events are outs'
    'ide the verified path"\n    let bind ← (← guar'
    'dFor request "trigger" ["bind"]).getObjVal? "'
    'bind"\n    let sameAs ← (← result.getObjVal? "'
    'expect").getObjVal? "same_as"\n    let alias ←'
    " sameAs.getObjValAs? String right.2\n    bind."
    "getObjValAs? String alias\n  match mapping wit"
    'h\n  | .ok key => if key == left.2 then "match'
    'ed" else "conflicting"\n  | .error _ => "unres'
    'olved"\n\ndef implementationCheck (observed : S'
    "tring × List (Val × Val)) (left right : Field"
    ') : String :=\n  if left.1 != "requested" || r'
    'ight.1 != "result_returned" then "unresolved"'
    '\n  else if observed.1 != "observed" then obse'
    "rved.1\n  else\n    match (findingInputs.find? "
    "(fun pair => pair.1 == left.2)).map Prod.snd "
    'with\n    | none => "unresolved"\n    | some wa'
    "nted => if (observed.2.find? (fun pair => pai"
    "r.1 == .str right.2)).map Prod.snd == some wa"
    'nted\n                     then "matched" else'
    ' "conflicting"\n\ndef formationCheck (contract '
    ": Lean.Json) (path : Except String (Lean.Json"
    " × Lean.Json × Lean.Json)) : String :=\n  let "
    "checked : Except String String := do\n    let "
    'wanted := Lean.Json.arr #[.str "C90.source_di'
    'agnostic", .str "formed"]\n    let effects ← c'
    'ontract.getObjValAs? (List Lean.Json) "must_e'
    'ffect"\n    if (← contract.getObjValAs? String'
    ' "output") != "reported" || !effects.contains'
    ' wanted then\n      return "unresolved"\n    le'
    "t (request, effect, result) ← path\n    let tr"
    'igger ← guardFor request "trigger" ["bind"]\n '
    '   if (← request.getObjValAs? String "event")'
    ' != "requested" ||\n       (← result.getObjVal'
    'As? String "event") != "result_returned" then'
    ' return "unresolved"\n    let actual := Lean.J'
    'son.arr #[← effect.getObjVal? "target", ← eff'
    'ect.getObjVal? "outcome"]\n    if actual != wa'
    'nted then return "conflicting"\n    let inputs'
    ' ← (← trigger.getObjVal? "bind").getObj?\n    '
    'let outputs ← (← (← result.getObjVal? "expect'
    '").getObjVal? "same_as").getObj?\n    return i'
    "f inputs.size == 3 && outputs.size == 3 then "
    '"matched" else "unresolved"\n  checked.toOptio'
    'n.getD "unresolved"\n\ndef findingClaim (declar'
    "ation : Lean.Json) : Except String Lean.Json "
    ':= do\n  let claim ← declaration.getObjVal? "c'
    'laim"\n  match claim.getObjVal? "operations" w'
    "ith\n  | .ok operations => operations.getObjVa"
    'l? "finding"\n  | .error _ => pure claim\n\ndef '
    "compareFinding : Except String (List Lean.Jso"
    "n × String) := do\n  let contract ← findingCla"
    "im (← AnechoicSpec.contract)\n  let solution ←"
    " findingClaim (← AnechoicSpec.solution)\n  let"
    " obligations ← contract.getObjValAs? (List Ob"
    'ligation) "same_values"\n  if obligations.isEm'
    'pty then throw "C90 finding declares no equal'
    'ity obligations"\n  let path := findingPath so'
    'lution (← contract.getObjValAs? String "outpu'
    't")\n  let observed := findingResult\n  let fac'
    "ts := obligations.map fun (left, right) => Le"
    'an.Json.mkObj [\n      ("left", Lean.toJson le'
    'ft), ("right", Lean.toJson right),\n      ("so'
    'lution", Lean.toJson (solutionCheck path left'
    ' right)),\n      ("implementation", Lean.toJso'
    "n (implementationCheck observed left right))]"
    "\n  return (facts, formationCheck contract pat"
    "h)\n\n#eval IO.println (Lean.toJson compareFind"
    "ing.toOption).compress\n"
)
