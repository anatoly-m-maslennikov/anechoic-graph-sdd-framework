"""Compare the C90 finding trace against freshly translated implementation Lean."""

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from .export_binding import export_check, export_pin

_SOURCE = Path(
    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/'
    'LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_1_DIAGNOSTICS_C90/diagnostics__pub.py'
)
_TRANSLATOR = 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.code_to_lean'
_CHECK = '''
open Autoform.Core Autoform.Generated.Implementation

abbrev Field := String × String
abbrev Obligation := Field × Field

def findingInputs : List (String × Val) :=
  [("source", .str "AN-S-4937@2"), ("field", .str "relations.ANSWERS"), ("message", .str "Missing relation")]

def findingContext (globals : Ref) : Ctx := {
    dialect := program.dialect, table := program.table, globals := globals,
    builtinBases := program.builtinBases, properties := program.properties,
    excClasses := program.excClasses, classDecls := program.classDecls }

def invokeFinding (target : String) (heap : Heap) (globals : Ref) (inputs : List Val) : Heap × EResult :=
  let ctx := findingContext globals
  match ctx.resolve target with
  | none => (heap, .hole "C90 finding was not translated")
  | some entry => applyFunc ctx 200 heap entry none inputs []

def findingResult : String × List (Val × Val) :=
  let (heap, globals) := initGlobals program 200 moduleInits
  match readExport heap globals "finding" with
  | none => ("unresolved", [])
  | some target =>
    match invokeFinding target heap globals (findingInputs.map Prod.snd) with
    | (finalHeap, .val (.ref ref)) =>
      match finalHeap.payload ref with
      | .dict rows => ("observed", rows)
      | _ => ("conflicting", [])
    | (_, .hole _) | (_, .outOfFuel) => ("unresolved", [])
    | _ => ("conflicting", [])

def stateAt (states : Array Lean.Json) (name : String) : Except String Lean.Json :=
  match states.find? (fun state => (state.getObjValAs? String "name").toOption == some name) with
  | some state => .ok state
  | none => .error "Missing Solution state"

def soleEdge (states : Array Lean.Json) (name : String) : Except String Lean.Json := do
  let edges ← (← stateAt states name).getObjValAs? (List Lean.Json) "transitions"
  match edges with
  | [edge] => pure edge
  | _ => throw "Expected a single Solution transition"

def guardFor (edge : Lean.Json) (kind : String) (fields : List String) : Except String Lean.Json := do
  let guard ← edge.getObjVal? "expect"
  let .obj keys := guard | throw "Expected Solution guard"
  if (← guard.getObjValAs? String "kind") == kind &&
     keys.all (fun key _ => key == "kind" || fields.contains key)
  then pure guard else throw "Unsupported Solution guard"

def findingPath (workflow : Lean.Json) (output : String) :
    Except String (Lean.Json × Lean.Json × Lean.Json) := do
  if (← workflow.getObjValAs? String "action") != "finding" then throw "Expected the finding Action"
  let states ← (← workflow.getObjVal? "states").getArr?
  let request ← soleEdge states (← workflow.getObjValAs? String "initial")
  let effect ← soleEdge states (← request.getObjValAs? String "target")
  let result ← soleEdge states (← effect.getObjValAs? String "target")
  let final ← stateAt states (← result.getObjValAs? String "target")
  let effectGuard ← guardFor effect "effect" ["target", "outcome"]
  let outputGuard ← guardFor result "output" ["outcome", "same_as"]
  if !(← final.getObjValAs? Bool "final") || (← outputGuard.getObjValAs? String "outcome") != output
  then throw "Solution path does not reach the selected output"
  pure (request, effectGuard, result)

def solutionCheck (path : Except String (Lean.Json × Lean.Json × Lean.Json)) (left right : Field) : String :=
  let mapping : Except String String := do
    let (request, _, result) ← path
    if (← request.getObjValAs? String "event") != left.1 ||
       (← result.getObjValAs? String "event") != right.1 then throw "Events are outside the verified path"
    let bind ← (← guardFor request "trigger" ["bind"]).getObjVal? "bind"
    let sameAs ← (← result.getObjVal? "expect").getObjVal? "same_as"
    let alias ← sameAs.getObjValAs? String right.2
    bind.getObjValAs? String alias
  match mapping with
  | .ok key => if key == left.2 then "matched" else "conflicting"
  | .error _ => "unresolved"

def implementationCheck (observed : String × List (Val × Val)) (left right : Field) : String :=
  if left.1 != "requested" || right.1 != "result_returned" then "unresolved"
  else if observed.1 != "observed" then observed.1
  else
    match (findingInputs.find? (fun pair => pair.1 == left.2)).map Prod.snd with
    | none => "unresolved"
    | some wanted => if (observed.2.find? (fun pair => pair.1 == .str right.2)).map Prod.snd == some wanted
                     then "matched" else "conflicting"

def formationCheck (contract : Lean.Json) (path : Except String (Lean.Json × Lean.Json × Lean.Json)) : String :=
  let checked : Except String String := do
    let wanted := Lean.Json.arr #[.str "C90.source_diagnostic", .str "formed"]
    let effects ← contract.getObjValAs? (List Lean.Json) "must_effect"
    if (← contract.getObjValAs? String "output") != "reported" || !effects.contains wanted then
      return "unresolved"
    let (request, effect, result) ← path
    let trigger ← guardFor request "trigger" ["bind"]
    if (← request.getObjValAs? String "event") != "requested" ||
       (← result.getObjValAs? String "event") != "result_returned" then return "unresolved"
    let actual := Lean.Json.arr #[← effect.getObjVal? "target", ← effect.getObjVal? "outcome"]
    if actual != wanted then return "conflicting"
    let inputs ← (← trigger.getObjVal? "bind").getObj?
    let outputs ← (← (← result.getObjVal? "expect").getObjVal? "same_as").getObj?
    return if inputs.size == 3 && outputs.size == 3 then "matched" else "unresolved"
  checked.toOption.getD "unresolved"

def compareFinding : Except String (List Lean.Json × String) := do
  let contract ← (← AnechoicSpec.contract).getObjVal? "claim"
  let solution ← (← AnechoicSpec.solution).getObjVal? "claim"
  let obligations ← contract.getObjValAs? (List Obligation) "same_values"
  if obligations.isEmpty then throw "C90 finding declares no equality obligations"
  let path := findingPath solution (← contract.getObjValAs? String "output")
  let observed := findingResult
  let facts := obligations.map fun (left, right) => Lean.Json.mkObj [
      ("left", Lean.toJson left), ("right", Lean.toJson right),
      ("solution", Lean.toJson (solutionCheck path left right)),
      ("implementation", Lean.toJson (implementationCheck observed left right))]
  return (facts, formationCheck contract path)

#eval IO.println (Lean.toJson compareFinding.toOption).compress
'''
_FINDING_PROOF = '''
private theorem getFresh (heap : Heap) (item : Obj) :
    Heap.get (heap ++ [item]) heap.length = some item := by
  simp [Heap.get]

private theorem setFresh (heap : Heap) (item : Obj) (payload : Payload) :
    Heap.setPayload (heap ++ [item]) heap.length payload =
      heap ++ [{item with payload := payload, version := item.version + 1}] := by
  unfold Heap.setPayload
  rw [List.mapIdx_append]
  have unchanged : List.mapIdx
      (fun i (o : Obj) => if i = heap.length then {o with payload := payload, version := o.version + 1} else o)
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
    | .dict fields => (fields.find? (fun pair => pair.1 == .str name)).map Prod.snd
    | _ => none
  | _ => none

theorem findingPreservesValues (heap : Heap) (globals : Ref) (source field message : Val) :
    let result := invokeFinding "diagnostics__pub.py:<module>.finding" heap globals [source, field, message]
    result.2 = .val (.ref heap.length) ∧ heap.length < result.1.length ∧
      returnedField result "source" = some source ∧
      returnedField result "field" = some field ∧
      returnedField result "message" = some message := by
  have resolved : (findingContext globals).resolve "diagnostics__pub.py:<module>.finding" =
      some f_diagnostics__pub_py__module__finding := rfl
  have boxed : (findingContext globals).dialect.boxesContainers = true := rfl
  simp only [invokeFinding, resolved]
  simp (config := {decide := true}) [returnedField, applyFunc,
        f_diagnostics__pub_py__module__finding, Func.posParams, Func.keywordParams,
        kwargsRejected, posRejected, signatureRejected, seedClassAttrDefaults,
        selfEnv, boxKwargs, bindParams, Env.get, Env.set, execStmt, evalExpr, evalPairs, Func.literalDefaults,
        boxed, Lit.toVal, Heap.alloc, Heap.payload, getFresh, setFresh, Stdlib.dictOfPairs, Stdlib.dictSet,
        Val.beq, Val.truthy]
'''


def _execute(command, timeout):
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode:
        raise ValueError((result.stderr + result.stdout).strip()[-2000:])
    return result.stdout


def _prove_finding(program, facts, lean):
    expected = {(('requested', field), ('result_returned', field))
                for field in ('source', 'field', 'message')}
    if (not isinstance(facts, list) or len(facts) != len(expected)
            or {(tuple(row['left']), tuple(row['right'])) for row in facts
                if row['solution'] == row['implementation'] == 'matched'} != expected):
        return {'status': 'unresolved', 'reason': 'Finding proof requires all three matching identity bindings.'}
    with program.open('a', encoding='utf-8') as file:
        file.write(_FINDING_PROOF)
    try:
        _execute([lean, '-DwarningAsError=true', str(program)], 120)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        return {'status': 'unresolved', 'reason': str(error)}
    return {'status': 'proved', 'theorem': 'findingPreservesValues',
            'quantified_over': ['heap', 'globals', 'source', 'field', 'message']}


def _observe(root, digest, export, authored, lean):
    path = root / _SOURCE
    if path.resolve(strict=True) != path:
        raise ValueError('Diagnostics source must be a regular file at its Project path')
    with TemporaryDirectory(prefix='anechoic-diagnostic-lean-') as folder:
        model = Path(folder) / 'Implementation.lean'
        _execute([sys.executable, '-B', '-m', _TRANSLATOR, str(path), str(root / export['path']),
                  '--sha256', digest, '--sha256', export['sha256'], '--output', str(model)], 1800)
        program = Path(folder) / 'Comparison.lean'
        program.write_text('import Lean\n' + model.read_text(encoding='utf-8') + '\n'
                           + authored.removeprefix('import Lean\n')
                           + export_check('finding', path.name) + _CHECK, encoding='utf-8')
        facts, formation = json.loads(_execute([lean, str(program)], 120))
        if formation not in ('matched', 'conflicting', 'unresolved'):
            raise ValueError('Lean returned an invalid finding effect check')
        proof = _prove_finding(program, facts, lean)
        if formation == 'matched':
            formation = proof['status']
        return facts, proof, {'target': 'C90.source_diagnostic', 'outcome': 'formed', 'status': formation}


def _checked_finding_obligation(fact):
    if (fact.get('action'), fact.get('output')) != ('finding', 'reported'):
        return False
    if fact['key'] == 'must_effect':
        return tuple(fact['left']) == ('C90.source_diagnostic', 'formed')
    return fact['key'] in ('action', 'terminal_output', 'same_values')


def _unresolved_obligations(evidence):
    pending = [fact for fact in evidence['coverage'] if not _checked_finding_obligation(fact)]
    pending.extend({'key': 'terminal_output', **row} for row in evidence.get('uncovered_outcomes', ()))
    return [{**fact, 'status': 'unresolved'} for fact in pending]


def _finding_verdict(report, facts, proof, effect):
    states = {fact[role] for fact in facts for role in ('solution', 'implementation')}
    if states - {'matched', 'conflicting', 'unresolved'}:
        raise ValueError('Lean returned unknown comparison status')
    if any(fact['solution'] == 'unresolved' for fact in facts):
        report['unresolved'].append('C90 Solution binding is outside the supported finding path.')
    if 'conflicting' in states or effect['status'] == 'conflicting':
        return 'mismatch'
    if effect['status'] != 'proved':
        report['unresolved'].append('C90 finding value preservation remains unproved.'
                                    if proof['status'] != 'proved' else 'C90 diagnostic formation remains unresolved.')
    elif not report['unresolved_obligations']:
        return 'no_mismatch_in_cases'
    return 'unresolved'


def compare_diagnostic(root, request, formal_verifier, lean):
    """Check the finding witness and prove the three declared identity bindings."""
    pins = {role: request[role] for role in ('manifest', 'solution')}
    formal = formal_verifier(root, 'C90', **pins, action='finding', lean=lean)
    report = {'status': 'unresolved', 'facts': [], 'formal': formal,
              'unresolved': ['C90 verdict and unobserved effects require separate evidence.']}
    if formal.get('outcome') != 'compared' or formal.get('translation', {}).get('status') != 'matched':
        return report
    if formal.get('sources') != pins:
        report['unresolved'].append('C90 Specs differ from their requested pins')
        return report
    if formal.get('status') == 'conflicting':
        report['status'] = 'mismatch'
        return report
    evidence = formal['evidence']
    pending = report['unresolved_obligations'] = _unresolved_obligations(evidence)
    if pending:
        report['unresolved'].append('Declared finding obligations lack implementation evidence.')
    expected = [(list(fact['left']), list(fact['right']))
                for fact in evidence['coverage'] if fact['key'] == 'same_values']
    if not expected:
        report['unresolved'].append('C90 finding declares no equality obligations')
        return report
    digest = request['implementation_sha256']
    try:
        root = Path(root).resolve(strict=True)
        export = report['public_export'] = export_pin(root / _SOURCE.parent, 'finding', root, request.get('export_sha256'))
        facts, proof, effect = _observe(root, digest, export, formal['lean'], lean)
        if not isinstance(facts, list) or [(row['left'], row['right']) for row in facts] != expected:
            raise ValueError('Lean result did not account for the declared equality obligations')
        status = _finding_verdict(report, facts, proof, effect)
    except (OSError, ValueError, SyntaxError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        report['unresolved'].append(str(error))
        return report
    export['status'] = 'matched'
    report.update(facts=facts, proof=proof, effect=effect, status=status)
    report['implementation'] = {'path': _SOURCE.as_posix(), 'sha256': digest}
    return report
