"""Lean checks used by the comparison."""

_CHECK = (
    "\nopen Autoform.Core Autoform.Generated.Implem"
    "entation\n\ndef invokeRenderer (claim : Val) (k"
    "eywords : List (String × Val)) : EResult :=\n "
    " let (heap, globals) := initGlobals program 4"
    "000 moduleInits\n  let ctx : Ctx := {\n    dial"
    "ect := program.dialect, table := program.tabl"
    "e, globals := globals,\n    builtinBases := pr"
    "ogram.builtinBases, properties := program.pro"
    "perties,\n    excClasses := program.excClasses"
    ", classDecls := program.classDecls }\n  let mo"
    'del : Val := .dict [(.str "solution", .dict ['
    '\n    (.str "claims", .list [.tuple [.str "pyt'
    'hon shape", .unit]])])]\n  match readExport he'
    'ap globals "render_solution" >>= ctx.resolve '
    "with\n  | some entry => (applyFunc ctx 4000 he"
    "ap entry none [model, claim] keywords).2\n  | "
    'none => .hole "C87 render_solution missing"\n\n'
    "def rendererClaim (spec : Except String Lean."
    "Json) : Except String Lean.Json :=\n  spec >>="
    ' (fun program => program.getObjVal? "claim")\n'
    "\ndef renderDetail : Lean.Json := Lean.Json.mk"
    'Obj [("model", .str "request_normalized_model'
    '")]\n\ndef renderingDeclared : Bool :=\n  (rende'
    "rerClaim AnechoicSpec.contract >>= (fun claim"
    ' => claim.getObjVal? "must_effect")).toOption'
    ' ==\n    some (Lean.Json.arr #[.arr #[.str "C8'
    '7.mermaid_diagram", .str "rendered",\n      re'
    "nderDetail]])\n\ndef rendererState (states : Ar"
    "ray Lean.Json) (name : String) : Except Strin"
    "g Lean.Json :=\n  match states.find? (fun stat"
    'e => (state.getObjValAs? String "name").toOpt'
    "ion == some name) with\n  | some state => .ok "
    'state\n  | none => .error ("Missing renderer S'
    'olution state " ++ name)\n\ndef rendererStep (s'
    "tates : Array Lean.Json) (name : String) (gua"
    "rd : Lean.Json) : Except String String := do\n"
    "  let edges ← (← rendererState states name).g"
    'etObjValAs? (List Lean.Json) "transitions"\n  '
    'let [edge] := edges | throw ("Unobserved rend'
    'erer Solution transitions at " ++ name)\n  let'
    ' expected ← edge.getObjVal? "expect"\n  if exp'
    'ected != guard then\n    throw ("Unobserved re'
    'nderer Solution guard at " ++ name ++ ": " ++'
    " expected.compress)\n  edge.getObjValAs? Strin"
    'g "target"\n\ndef checkRendererWorkflow : Excep'
    "t String Unit := do\n  let claim ← rendererCla"
    "im AnechoicSpec.solution\n  if (← claim.getObj"
    'ValAs? String "action") != "render_solution" '
    'then\n    throw "Expected the render_solution '
    'Action"\n  let states ← (← claim.getObjVal? "s'
    'tates").getArr?\n  let first ← rendererStep st'
    'ates (← claim.getObjValAs? String "initial")\n'
    '    (Lean.Json.mkObj [("kind", .str "trigger"'
    ")])\n  let output ← rendererStep states first "
    '(Lean.Json.mkObj [("kind", .str "effect"),\n  '
    '  ("target", .str "C87.mermaid_diagram"), ("o'
    'utcome", .str "rendered"), ("detail", renderD'
    "etail)])\n  let final ← rendererStep states ou"
    'tput\n    (Lean.Json.mkObj [("kind", .str "out'
    'put"), ("outcome", .str "rendered")])\n  if !('
    "← (← rendererState states final).getObjValAs?"
    ' Bool "final") then\n    throw "Renderer Solut'
    'ion output does not end the observed path"\n\nd'
    "ef shapeInput (raw : Lean.Json) (names : List"
    " String) : Except String Val := do\n  let fiel"
    'ds ← raw.getObjVal? "fields"\n  if (← fields.g'
    'etObj?).size != names.length then throw "Expe'
    'cted the complete configured shape"\n  let pai'
    "rs ← names.mapM fun name => do\n    pure (.str"
    " name, .str (← fields.getObjValAs? String nam"
    'e))\n  let record ← raw.getObjValAs? String "r'
    'ecord"\n  let subtype ← raw.getObjValAs? Strin'
    'g "subtype"\n  let base ← raw.getObjValAs? Str'
    'ing "base"\n  return .dict [(.str "record", .s'
    'tr record), (.str "subtype", .str subtype),\n '
    '   (.str "base", .str base), (.str "fields", '
    ".dict pairs)]\n\ndef expectedDiagram (raw : Lea"
    "n.Json) (names : List String) : Except String"
    " String := do\n  let record ← raw.getObjValAs?"
    ' String "record"\n  let subtype ← raw.getObjVa'
    'lAs? String "subtype"\n  let base ← raw.getObj'
    'ValAs? String "base"\n  let fields ← raw.getOb'
    'jVal? "fields"\n  if (← fields.getObj?).size !'
    '= names.length then throw "Expected the compl'
    'ete configured shape"\n  let declarations ← na'
    'mes.mapM fun name => do\n    pure s!"        {'
    '← fields.getObjValAs? String name} {name}"\n  '
    'if base != record then throw "Expected inheri'
    'tance from the record"\n  pure (String.interca'
    'late "\\n" (["classDiagram", "    class ShapeR'
    'ecord[\\"" ++ record ++ "\\"] {"] ++\n    declar'
    'ations ++ ["    }", "    class ShapeSubtype[\\'
    '"" ++ subtype ++ "\\"]",\n      "    ShapeRecor'
    'd <|-- ShapeSubtype"]))\n\ndef rendererResult ('
    "result : EResult) (expected : String) : Lean."
    "Json :=\n  match result with\n  | .val (.str ou"
    "tput) =>\n    if output == expected then .str "
    '"matched"\n      else Lean.Json.mkObj [("diagr'
    'am", .str output)]\n  | .hole reason => .str ('
    '"unresolved: " ++ reason)\n  | .outOfFuel => .'
    'str "unresolved: fuel"\n  | _ => .str "conflic'
    'ting"\n\ndef diagramStatus (names : List String'
    ") : Except String Lean.Json := do\n  let claim"
    " ← rendererClaim ShapeWitness.solution >>= (s"
    "hapeInput · names)\n  let expected ← rendererC"
    "laim ShapeWitness.contract >>= (expectedDiagr"
    "am · names)\n  if !renderingDeclared then thro"
    'w "Renderer effect is outside the checked cla'
    'im"\n  return .arr #[rendererResult (invokeRen'
    "derer claim []) expected,\n                ren"
    'dererResult (invokeRenderer claim [("action",'
    " .unit)]) expected]\n\ndef rendererCases : Lean"
    '.Json := Lean.toJson ([["header", "content"],'
    ' ["content", "header"]].map\n    (fun names =>'
    " match diagramStatus names with\n      | .ok s"
    "tatus => status\n      | .error reason => .arr"
    ' #[.str ("unresolved: " ++ reason), .str ("un'
    'resolved: " ++ reason)]))\n\n#eval IO.println ('
    'Lean.Json.mkObj [("cases", rendererCases), ("'
    'solution_gap",\n  match checkRendererWorkflow '
    "with | .ok _ => .null | .error reason => .str"
    " reason)]).compress\n"
)
