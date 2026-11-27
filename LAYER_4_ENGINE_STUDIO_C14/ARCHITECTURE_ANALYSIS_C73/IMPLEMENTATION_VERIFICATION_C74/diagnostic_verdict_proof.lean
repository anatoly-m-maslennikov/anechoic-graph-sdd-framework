
open Autoform.Core Autoform.Generated.Implementation
set_option maxHeartbeats 180000
set_option pp.deepTerms false
set_option linter.unusedSimpArgs false

def verdictOracle (xs : List String) : String :=
  if "conflicting" ∈ xs then "conflicting"
  else if xs.isEmpty || ("unresolved" ∈ xs : Bool) then "unresolved" else "matched"

def verdictCtx (g : Ref) : Ctx := {
  dialect := program.dialect, table := program.table, globals := g,
  builtinBases := program.builtinBases, properties := program.properties,
  excClasses := program.excClasses, classDecls := program.classDecls }

private theorem strContains (s : String) (xs : List String) :
    (xs.map Val.str).any (Val.beq (.str s)) = decide (s ∈ xs) := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    have one : Val.beq (.str s) (.str x) = decide (s = x) := by
      change (s == x) = _
      by_cases h : s = x <;> simp [h]
    simp only [List.map_cons, List.any_cons, one, ih, List.mem_cons]
    by_cases h : s = x <;> by_cases y : s ∈ xs <;> simp [h, y]

theorem verdictDialect (g : Ref) : (verdictCtx g).dialect = .python := rfl

def statusListObject (xs : List String) : Obj :=
  {cls := "list", fields := [], payload := .list (xs.map Val.str)}

private theorem getStatusListObject (heap : Heap) (o : Obj) :
    Heap.get (heap ++ [o]) heap.length = some o := by
  simp [Heap.get]

private theorem verdictListBool (g : Ref) :
    (verdictCtx g).classDefines "list" "__bool__" = false := rfl

private theorem verdictListLen (g : Ref) :
    (verdictCtx g).classDefines "list" "__len__" = false := rfl

theorem boxedVerdictExact (h : Heap) (g : Ref) (xs : List String) :
    (applyFunc (verdictCtx g) 12 (h ++ [statusListObject xs])
      f_diagnostics__pub_py__module__verdict none [.ref h.length] []).2 =
      .val (.str (verdictOracle xs)) := by
  by_cases c : "conflicting" ∈ xs
  · have hit : (xs.map Val.str).any (Val.beq (.str "conflicting")) = true := by
      rw [strContains]; exact decide_eq_true c
    simp (config := {decide := true}) [applyFunc, f_diagnostics__pub_py__module__verdict,
        Func.posParams, Func.keywordParams, kwargsRejected, posRejected, signatureRejected, seedClassAttrDefaults,
        selfEnv, boxKwargs, bindParams, Env.get, Env.set, execStmt, evalExpr, Func.literalDefaults,
        Lit.toVal, Val.truthy, Ctx.dunderOn, Val.unbox, valIn, Val.unbuiltin,
        hit, c, verdictOracle, -List.any_map, verdictDialect, getStatusListObject, statusListObject,
        Heap.payload, Payload.toVal, evalTruthWith, builtinDunderTarget, verdictListBool,
        verdictListLen, Iteration.truthValue, Iteration.pureTruth, Iteration.truthConsumer]
  · by_cases emp : xs = []
    · subst xs
      simp (config := {decide := true}) [applyFunc, f_diagnostics__pub_py__module__verdict,
          Func.posParams, Func.keywordParams, kwargsRejected, posRejected, signatureRejected, seedClassAttrDefaults,
          selfEnv, boxKwargs, bindParams, Env.get, Env.set, execStmt, evalExpr, Func.literalDefaults,
          Lit.toVal, Val.truthy, Ctx.dunderOn, Val.unbox, valIn, Val.unbuiltin,
          binopNeedsHeap, applyBinop, verdictOracle, -List.any_map, verdictDialect,
          getStatusListObject, statusListObject, Heap.payload, Payload.toVal,
          evalTruthWith, builtinDunderTarget, verdictListBool, verdictListLen,
          Iteration.truthValue, Iteration.pureTruth, Iteration.truthConsumer]
    · have ne : xs.isEmpty = false := by simpa using emp
      have miss : (xs.map Val.str).any (Val.beq (.str "conflicting")) = false := by
        rw [strContains]; exact decide_eq_false c
      by_cases u : "unresolved" ∈ xs
      · have hit : (xs.map Val.str).any (Val.beq (.str "unresolved")) = true := by
          rw [strContains]; exact decide_eq_true u
        simp (config := {decide := true}) [applyFunc, f_diagnostics__pub_py__module__verdict,
          Func.posParams, Func.keywordParams, kwargsRejected, posRejected, signatureRejected,
          seedClassAttrDefaults, selfEnv, boxKwargs, bindParams, Env.get, Env.set, execStmt,
          evalExpr, Func.literalDefaults, Lit.toVal, Val.truthy, Ctx.dunderOn, Val.unbox, valIn,
          Val.unbuiltin, -List.any_map, c, u, ne, miss, hit, verdictOracle, binopNeedsHeap,
          applyBinop, -List.isEmpty_iff, verdictDialect, getStatusListObject, statusListObject,
          Heap.payload, Payload.toVal, evalTruthWith, builtinDunderTarget, verdictListBool,
          verdictListLen, Iteration.truthValue, Iteration.pureTruth, Iteration.truthConsumer]
      · have no : (xs.map Val.str).any (Val.beq (.str "unresolved")) = false := by
          rw [strContains]; exact decide_eq_false u
        simp (config := {decide := true}) [applyFunc, f_diagnostics__pub_py__module__verdict,
          Func.posParams, Func.keywordParams, kwargsRejected, posRejected, signatureRejected,
          seedClassAttrDefaults, selfEnv, boxKwargs, bindParams, Env.get, Env.set, execStmt,
          evalExpr, Func.literalDefaults, Lit.toVal, Val.truthy, Ctx.dunderOn, Val.unbox, valIn,
          Val.unbuiltin, -List.any_map, c, u, ne, miss, no, verdictOracle, binopNeedsHeap,
          applyBinop, -List.isEmpty_iff, verdictDialect, getStatusListObject, statusListObject,
          Heap.payload, Payload.toVal, evalTruthWith, builtinDunderTarget, verdictListBool,
          verdictListLen, Iteration.truthValue, Iteration.pureTruth, Iteration.truthConsumer]

def invokePublicVerdict (xs : List String) : EResult :=
  let state := initGlobals program 20 moduleInits
  let (heap, items) := state.1.alloc (statusListObject xs)
  let ctx := verdictCtx state.2
  match readExport state.1 state.2 "verdict" >>= ctx.resolve with
  | none => .hole "Missing verdict export"
  | some fn => (applyFunc ctx 12 heap fn none [.ref items] []).2

private theorem publicBinding :
    let state := initGlobals program 20 moduleInits
    (readExport state.1 state.2 "verdict" >>= (verdictCtx state.2).resolve) =
      some f_diagnostics__pub_py__module__verdict := by rfl

theorem publicVerdictExact (xs : List String) :
    invokePublicVerdict xs = .val (.str (verdictOracle xs)) := by
  unfold invokePublicVerdict
  simp only [publicBinding, Heap.alloc]
  exact boxedVerdictExact _ _ xs

private def verdictDetail (hasConflict unresolvedOrEmpty : Bool) : Lean.Json :=
  Lean.Json.mkObj (if hasConflict then [("has_conflict", .bool true)]
    else [("has_conflict", .bool false),
          ("unresolved_or_empty", .bool unresolvedOrEmpty)])

private def verdictEffect (hasConflict unresolvedOrEmpty : Bool) : Lean.Json :=
  .arr #[.arr #[.str "C90.verdict_input", .str "observed",
                verdictDetail hasConflict unresolvedOrEmpty]]

private def verdictClaim (source : Except String Lean.Json) :
    Except String Lean.Json := do
  let authored ← (← source).getObjVal? "claim"
  match authored.getObjVal? "operations" with
  | .ok operations => operations.getObjVal? "verdict"
  | .error _ => pure authored

private def readVerdictCase (entry : Lean.Json) :
    Except String (Lean.Json × String) := do
  let output ← entry.getObjValAs? String "output"
  let effects ← entry.getObjVal? "must_effect"
  let supported := [verdictEffect true false, verdictEffect false true,
                    verdictEffect false false]
  if entry != Lean.Json.mkObj [("action", .str "verdict"),
      ("output", .str output), ("must_effect", effects)] ||
     !supported.contains effects ||
     !(["conflicting", "unresolved", "matched"].contains output) then
    throw "Unsupported C90 verdict case"
  pure (effects, output)

def declaredVerdict (hasConflict unresolvedOrEmpty : Bool) :
    Except String String := do
  let claim ← verdictClaim AnechoicSpec.contract
  let cases ← claim.getObjVal? "cases"
  if claim != Lean.Json.mkObj [
      ("action", .str "verdict"), ("cases", cases)] then
    throw "Unsupported C90 verdict Contract"
  let entries ← (← cases.getArr?).toList.mapM readVerdictCase
  let expected := verdictEffect hasConflict unresolvedOrEmpty
  let selected := entries.filterMap fun (effects, output) =>
    if effects == expected then some output else none
  let [output] := selected | throw "Missing or ambiguous C90 verdict case"
  pure output

private def verdictTransitions (states : List Lean.Json) (name : String)
    (final : Bool) : Except String (List Lean.Json) := do
  let [state] := states.filter (fun state =>
      (state.getObjValAs? String "name").toOption == some name) |
    throw "Missing or ambiguous C90 verdict Solution state"
  let edges ← state.getObjVal? "transitions"
  if state != Lean.Json.mkObj [("name", .str name), ("final", .bool final),
      ("transitions", edges)] then
    throw "Unsupported C90 verdict Solution state"
  return (← edges.getArr?).toList

private def verdictTransition (edge : Lean.Json) :
    Except String (String × Lean.Json) := do
  let event ← edge.getObjValAs? String "event"
  let target ← edge.getObjValAs? String "target"
  let guard ← edge.getObjVal? "expect"
  if edge != Lean.Json.mkObj [("event", .str event), ("target", .str target),
      ("expect", guard)] then
    throw "Unsupported C90 verdict Solution transition"
  pure (target, guard)

def solutionVerdict (hasConflict unresolvedOrEmpty : Bool) :
    Except String String := do
  let claim ← verdictClaim AnechoicSpec.solution
  let initial ← claim.getObjValAs? String "initial"
  let states ← claim.getObjVal? "states"
  if claim != Lean.Json.mkObj [("action", .str "verdict"),
      ("initial", .str initial), ("states", states)] then
    throw "Unsupported C90 verdict Solution"
  let states := (← states.getArr?).toList
  let edges ← verdictTransitions states initial false
  if states.length != 5 || edges.length != 3 then
    throw "Unsupported C90 verdict Solution shape"
  let detail := verdictDetail hasConflict unresolvedOrEmpty
  let guard := Lean.Json.mkObj [("kind", .str "effect"),
    ("target", .str "C90.verdict_input"), ("outcome", .str "observed"),
    ("detail", detail)]
  let edges ← edges.mapM verdictTransition
  let [target] := edges.filterMap (fun (target, expected) =>
    if expected == guard then some target else none) |
    throw "Missing or ambiguous C90 verdict Solution effect guard"
  let returns ← verdictTransitions states target false
  let [edge] := returns | throw "Unsupported C90 verdict Solution return"
  let (terminal, guard) ← verdictTransition edge
  let output ← guard.getObjValAs? String "outcome"
  if guard != Lean.Json.mkObj [("kind", .str "output"),
      ("outcome", .str output)] then
    throw "Unsupported C90 verdict Solution output guard"
  if !(← verdictTransitions states terminal true).isEmpty then
    throw "C90 verdict Solution has transitions after its output"
  pure output

theorem publicVerdictMatchesContract (xs : List String) :
    ∃ output : String,
      (declaredVerdict (decide ("conflicting" ∈ xs))
        (xs.isEmpty || ("unresolved" ∈ xs : Bool))).toOption =
          some output ∧
      (solutionVerdict (decide ("conflicting" ∈ xs))
        (xs.isEmpty || ("unresolved" ∈ xs : Bool))).toOption =
          some output ∧
      invokePublicVerdict xs = .val (.str output) := by
  refine ⟨verdictOracle xs, and_assoc.mp ⟨?_, publicVerdictExact xs⟩⟩
  -- The generated claims use Lean's partial JSON parser.
  by_cases c : "conflicting" ∈ xs
  · simp only [verdictOracle, c, if_true, decide_true]
    change (declaredVerdict true false).toOption = some "conflicting" ∧
      (solutionVerdict true false).toOption = some "conflicting"
    native_decide
  · simp only [verdictOracle, c, if_false, decide_false]
    cases xs.isEmpty || ("unresolved" ∈ xs : Bool) <;> native_decide
