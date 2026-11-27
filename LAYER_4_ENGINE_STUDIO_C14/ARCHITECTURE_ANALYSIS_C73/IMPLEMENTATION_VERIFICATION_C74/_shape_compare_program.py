"""Lean comparison of verified Spec and implementation shapes."""

CHECK = (
    "\n"
    "def checkShape (spec actual : Lean.Json) (solution : Bool) : "
    "Except String (List (String × Bool)) := do\n"
    '  let .obj fields ← spec.getObjVal? "fields" | throw "expected '
    'declared fields"\n'
    '  let observed ← actual.getObjVal? "fields"\n'
    '  let identity := ["record", "subtype", "base"].map\n'
    "    (fun key => (key, (spec.getObjVal? key).toOption == "
    "(actual.getObjVal? key).toOption))\n"
    "  let required := fields.toList.map\n"
    '    (fun (key, value) => ("field." ++ key, (observed.getObjVal? '
    "key).toOption == some value))\n"
    "  let subtype := if solution then\n"
    '    [("subtype_fields", (actual.getObjVal? '
    '"subtype_fields").toOption == some (Lean.Json.mkObj []))]\n'
    "    else []\n"
    "  pure (identity ++ required ++ subtype)\n"
    "\n"
    "def compareImplementation : Except String (List (List (String × "
    "Bool))) := do\n"
    "  let actual ← ImplementationShape.claim\n"
    "  let contract ← AnechoicSpec.contract >>= fun pin => "
    'pin.getObjVal? "claim"\n'
    "  let solution ← AnechoicSpec.solution >>= fun pin => "
    'pin.getObjVal? "claim"\n'
    "  pure [← checkShape contract actual false, ← checkShape solution "
    "actual true]\n"
    "\n"
    "#eval IO.println (Lean.toJson "
    "compareImplementation.toOption).compress\n"
)
