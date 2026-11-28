"""Build Lean checks for a normalized executable shape claim."""

_PARAMETER_CHECKS = """
  let rec params (expr : Lean.Expr) (count : Nat) (mode : Lean.BinderInfo)\
 : Option Lean.Expr :=
    match count, expr with
    | 0, _ => some expr
    | n + 1, .forallE _ (.sort (.succ .zero)) body binder =>
      if binder == mode then params body n mode else none
    | _, _ => none
  let rec fields (expr : Lean.Expr) (count : Nat) : Bool :=
    match count, expr with
    | 0, .forallE .. => false
    | 0, _ => true
    | n + 1, .forallE _ _ body .default => fields body n
    | _, _ => false
  let validDecl (d : Lean.InductiveVal) :=
    params d.type d.numParams .default == some (.sort (.succ .zero)) &&\
 match d.ctors with
      | [name] => match env.find? name with
        | some (.ctorInfo ctor) => match params ctor.type d.numParams\
 .implicit with
          | some tail => fields tail ctor.numFields
          | none => false
        | _ => false
      | _ => false
"""


def shape_checks(claim, role):
    """Print shape metadata and exact projection type checks as JSON."""
    record = f"Shape_{role}.«R_{claim['record']}»"
    subtype = f"Shape_{role}.«S_{claim['subtype']}»"
    fields = ", ".join(f"`«f_{name}»" for name in claim["fields"])
    parents = f"#[`{record}]" if claim["base"] == claim["record"] else "#[]"
    subfields = 1 if claim["base"] == claim["record"] else 0
    types = sorted(set(claim["fields"].values()))
    checks = f"""
run_cmd do
  let env ← Lean.getEnv
{_PARAMETER_CHECKS}
  let metadata := match Lean.getStructureInfo? env `{record},\
 Lean.getStructureInfo? env `{subtype},
      env.find? `{record}, env.find? `{subtype} with
    | some r, some s, some (.inductInfo rd), some (.inductInfo sd) =>
      rd.numParams == {len(types)} && sd.numParams ==\
 {len(types) if subfields else 0} &&\
 validDecl rd && validDecl sd &&
      r.parentInfo.isEmpty && r.fieldNames == #[{fields}] &&
      s.parentInfo.map (fun (p : Lean.StructureParentInfo) => p.structName)\
 == {parents} && s.fieldNames.size == {subfields}
    | _, _, _, _ => false
  let results ← Lean.Elab.Command.liftTermElabM do
    let mut results := #[metadata]
"""
    for name, typ in claim["fields"].items():
        checks += f"""
    let field := match env.find? `{record}.«f_{name}» with
      | some info => info.type
      | none => Lean.mkConst ``False
    let same ← Lean.Meta.forallTelescope field fun args result => do
      if args.size != {len(types) + 1} then return false
      Lean.Meta.isDefEq result args[{types.index(typ)}]!
    results := results.push same
"""
    if claim["base"] == claim["record"]:
        checks += _parent_check(record, subtype, claim["record"], len(types))
    return (
        checks
        + """
    return results
  liftM <| IO.print ((Lean.toJson results).compress ++ ",")
"""
    )


def _parent_check(record, subtype, name, count):
    return f"""
    let parent := match env.find? `{subtype}.«toR_{name}» with
      | some info => info.type
      | none => Lean.mkConst ``False
    let same ← Lean.Meta.forallTelescope parent fun args result => do
      if args.size != {count + 1} then return false
      let expected := Lean.mkAppN (Lean.mkConst `{record}) (args.extract 0\
 {count})
      Lean.Meta.isDefEq result expected
    results := results.push same
"""
