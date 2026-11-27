private theorem getFresh (heap : Heap) (item : Obj) :
    Heap.get (heap ++ [item]) heap.length = some item := by
  simp [Heap.get]

private theorem setFresh (heap : Heap) (item : Obj) (payload : Payload) :
    Heap.setPayload (heap ++ [item]) heap.length payload =
      heap ++ [{item with payload := payload, version := item.version + 1}]
        := by
  unfold Heap.setPayload
  rw [List.mapIdx_append]
  have unchanged : List.mapIdx
      (fun i (o : Obj) => if i = heap.length then
        {o with payload := payload, version := o.version + 1} else o)
      heap = heap := by
    apply List.ext_getElem
    · simp
    · intro n hleft hright
      simp [List.getElem_mapIdx, Nat.ne_of_lt hright]
  simp [unchanged]

set_option maxHeartbeats 1200000
set_option pp.deepTerms false
set_option linter.unusedSimpArgs false

def returnedField (result : Heap × EResult) (name : String) : Option Val :=
  match result with
  | (heap, .val (.ref address)) =>
    match heap.payload address with
    | .dict fields => (fields.find? (fun pair => pair.1 == .str name)).map
      Prod.snd
    | _ => none
  | _ => none

theorem findingPreservesValues (heap : Heap) (globals : Ref) (source field
  message : Val) :
    let result := invokeFinding "diagnostics__pub.py:<module>.finding" heap
      globals [source, field, message]
    result.2 = .val (.ref heap.length) ∧ heap.length < result.1.length ∧
      returnedField result "source" = some source ∧
      returnedField result "field" = some field ∧
      returnedField result "message" = some message := by
  have resolved : (findingContext globals).resolve
    "diagnostics__pub.py:<module>.finding" =
      some f_diagnostics__pub_py__module__finding := rfl
  have boxed : (findingContext globals).dialect.boxesContainers = true := rfl
  simp only [invokeFinding, resolved]
  simp (config := {decide := true}) [returnedField, applyFunc,
        f_diagnostics__pub_py__module__finding, Func.posParams,
          Func.keywordParams,
        kwargsRejected, posRejected, signatureRejected, seedClassAttrDefaults,
        selfEnv, boxKwargs, bindParams, Env.get, Env.set, execStmt, evalExpr,
          evalPairs, Func.literalDefaults,
        boxed, Lit.toVal, Heap.alloc, Heap.payload, getFresh, setFresh,
          Stdlib.dictOfPairs, Stdlib.dictSet,
        Val.beq, Val.truthy]
