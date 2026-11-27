"""Compare C87 renderer output against pinned renderer and shape Specs."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from .diagnostic_compare import _execute
from .export_binding import export_check, export_pin

RENDERER_SOURCE_NAMES = ('solution_diagram__pub.py', 'shape_diagram__pub.py')
_SOURCE_DIR = Path(
    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/'
    'LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_3_MERMAID_RENDERER_C87'
)
_TRANSLATOR = Path(__file__).with_name('code_to_lean.py')
_ORDERS = (('header', 'content'), ('content', 'header'))
_CHECK = r'''
open Autoform.Core Autoform.Generated.Implementation

def invokeRenderer (claim : Val) (keywords : List (String × Val)) : EResult :=
  let (heap, globals) := initGlobals program 4000 moduleInits
  let ctx : Ctx := {
    dialect := program.dialect, table := program.table, globals := globals,
    builtinBases := program.builtinBases, properties := program.properties,
    excClasses := program.excClasses, classDecls := program.classDecls }
  let model : Val := .dict [(.str "solution", .dict [
    (.str "claims", .list [.tuple [.str "python shape", .unit]])])]
  match readExport heap globals "render_solution" >>= ctx.resolve with
  | some entry => (applyFunc ctx 4000 heap entry none [model, claim] keywords).2
  | none => .hole "C87 render_solution missing"

def rendererClaim (spec : Except String Lean.Json) : Except String Lean.Json :=
  spec >>= (fun program => program.getObjVal? "claim")

def renderDetail : Lean.Json := Lean.Json.mkObj [("model", .str "request_normalized_model")]

def renderingDeclared : Bool :=
  (rendererClaim AnechoicSpec.contract >>= (fun claim => claim.getObjVal? "must_effect")).toOption ==
    some (Lean.Json.arr #[.arr #[.str "C87.mermaid_diagram", .str "rendered",
      renderDetail]])

def rendererState (states : Array Lean.Json) (name : String) : Except String Lean.Json :=
  match states.find? (fun state => (state.getObjValAs? String "name").toOption == some name) with
  | some state => .ok state
  | none => .error ("Missing renderer Solution state " ++ name)

def rendererStep (states : Array Lean.Json) (name : String) (guard : Lean.Json) : Except String String := do
  let edges ← (← rendererState states name).getObjValAs? (List Lean.Json) "transitions"
  let [edge] := edges | throw ("Unobserved renderer Solution transitions at " ++ name)
  let expected ← edge.getObjVal? "expect"
  if expected != guard then
    throw ("Unobserved renderer Solution guard at " ++ name ++ ": " ++ expected.compress)
  edge.getObjValAs? String "target"

def checkRendererWorkflow : Except String Unit := do
  let claim ← rendererClaim AnechoicSpec.solution
  if (← claim.getObjValAs? String "action") != "render_solution" then
    throw "Expected the render_solution Action"
  let states ← (← claim.getObjVal? "states").getArr?
  let first ← rendererStep states (← claim.getObjValAs? String "initial")
    (Lean.Json.mkObj [("kind", .str "trigger")])
  let output ← rendererStep states first (Lean.Json.mkObj [("kind", .str "effect"),
    ("target", .str "C87.mermaid_diagram"), ("outcome", .str "rendered"), ("detail", renderDetail)])
  let final ← rendererStep states output
    (Lean.Json.mkObj [("kind", .str "output"), ("outcome", .str "rendered")])
  if !(← (← rendererState states final).getObjValAs? Bool "final") then
    throw "Renderer Solution output does not end the observed path"

def shapeInput (raw : Lean.Json) (names : List String) : Except String Val := do
  let fields ← raw.getObjVal? "fields"
  if (← fields.getObj?).size != names.length then throw "Expected the complete configured shape"
  let pairs ← names.mapM fun name => do
    pure (.str name, .str (← fields.getObjValAs? String name))
  let record ← raw.getObjValAs? String "record"
  let subtype ← raw.getObjValAs? String "subtype"
  let base ← raw.getObjValAs? String "base"
  return .dict [(.str "record", .str record), (.str "subtype", .str subtype),
    (.str "base", .str base), (.str "fields", .dict pairs)]

def expectedDiagram (raw : Lean.Json) (names : List String) : Except String String := do
  let record ← raw.getObjValAs? String "record"
  let subtype ← raw.getObjValAs? String "subtype"
  let base ← raw.getObjValAs? String "base"
  let fields ← raw.getObjVal? "fields"
  if (← fields.getObj?).size != names.length then throw "Expected the complete configured shape"
  let declarations ← names.mapM fun name => do
    pure s!"        {← fields.getObjValAs? String name} {name}"
  if base != record then throw "Expected inheritance from the record"
  pure (String.intercalate "\n" (["classDiagram", "    class ShapeRecord[\"" ++ record ++ "\"] {"] ++
    declarations ++ ["    }", "    class ShapeSubtype[\"" ++ subtype ++ "\"]",
      "    ShapeRecord <|-- ShapeSubtype"]))

def rendererResult (result : EResult) (expected : String) : Lean.Json :=
  match result with
  | .val (.str output) =>
    if output == expected then .str "matched"
      else Lean.Json.mkObj [("diagram", .str output)]
  | .hole reason => .str ("unresolved: " ++ reason)
  | .outOfFuel => .str "unresolved: fuel"
  | _ => .str "conflicting"

def diagramStatus (names : List String) : Except String Lean.Json := do
  let claim ← rendererClaim ShapeWitness.solution >>= (shapeInput · names)
  let expected ← rendererClaim ShapeWitness.contract >>= (expectedDiagram · names)
  if !renderingDeclared then throw "Renderer effect is outside the checked claim"
  return .arr #[rendererResult (invokeRenderer claim []) expected,
                rendererResult (invokeRenderer claim [("action", .unit)]) expected]

def rendererCases : Lean.Json := Lean.toJson ([["header", "content"], ["content", "header"]].map
    (fun names => match diagramStatus names with
      | .ok status => status
      | .error reason => .arr #[.str ("unresolved: " ++ reason), .str ("unresolved: " ++ reason)]))

#eval IO.println (Lean.Json.mkObj [("cases", rendererCases), ("solution_gap",
  match checkRendererWorkflow with | .ok _ => .null | .error reason => .str reason)]).compress
'''


def _observe(root, digests, export, authored, lean):
    sources = [*(root / _SOURCE_DIR / name for name in RENDERER_SOURCE_NAMES), root / export['path']]
    for path in sources:
        if path.resolve(strict=True) != path or not path.is_file():
            raise ValueError('Renderer source must be a regular file at its Project path')
    with TemporaryDirectory(prefix='anechoic-renderer-lean-') as folder:
        model = Path(folder) / 'Implementation.lean'
        hashes = [item for name in RENDERER_SOURCE_NAMES for item in ('--sha256', digests[name])]
        hashes.extend(('--sha256', export['sha256']))
        _execute([sys.executable, '-B', str(_TRANSLATOR), *map(str, sources),
                  *hashes, '--output', str(model)], 1800)
        program = Path(folder) / 'Comparison.lean'
        program.write_text('import Lean\n' + model.read_text(encoding='utf-8') + '\n'
                           + authored + export_check('render_solution', RENDERER_SOURCE_NAMES[0]) + _CHECK,
                           encoding='utf-8')
        return json.loads(_execute([lean, str(program)], 120))


def _case_status(value):
    if isinstance(value, dict) and value.keys() == {'diagram'} and isinstance(value['diagram'], str):
        return 'unresolved: different diagram text' if value['diagram'].strip() else 'conflicting'
    if isinstance(value, str) and (value in ('matched', 'conflicting', 'unresolved')
                                  or value.startswith('unresolved: ')):
        return value
    raise ValueError('Lean returned an unknown comparison status')


def _shape_case(order, row):
    if not isinstance(row, list) or len(row) != 2:
        raise ValueError('Lean did not return both renderer call results')
    positional, keyword = map(_case_status, row)
    statuses = (positional, keyword)
    status = ('conflicting' if 'conflicting' in statuses else
              next((value for value in statuses if value != 'matched'), 'matched'))
    return {'field_order': list(order), 'status': status,
            'calls': {'positional': positional, 'action_none': keyword}}


def _renderer_results(observed):
    if not isinstance(observed, dict) or observed.keys() != {'cases', 'solution_gap'}:
        raise ValueError('Lean did not return renderer cases and Solution coverage')
    values, gap = observed['cases'], observed['solution_gap']
    if not isinstance(values, list) or len(values) != len(_ORDERS):
        raise ValueError('Lean did not return both configured shape cases')
    if gap is not None and (not isinstance(gap, str) or not gap.strip()):
        raise ValueError('Lean returned an invalid Solution coverage gap')
    return [_shape_case(order, row) for order, row in zip(_ORDERS, values, strict=True)], gap


def compare_renderer(root, request, formal_verifier, lean):
    """Check the two configured shape orders; other behavior is unmeasured."""
    pins = {role: request[role] for role in ('manifest', 'solution')}
    witness = request['witness']
    digests = request['implementation_sha256']
    report = {'status': 'unresolved', 'sources': pins, 'witness': witness,
              'formal': {}, 'cases': [],
              'implementation': {(_SOURCE_DIR / name).as_posix(): digests[name]
                                 for name in RENDERER_SOURCE_NAMES},
              'unresolved': ['Other shapes, diagram layouts, and effects require separate evidence.']}
    try:
        for component, source_pins in (('C87', pins), ('C52', witness)):
            formal = formal_verifier(root, component, **source_pins, lean=lean)
            report['formal'][component] = formal
            if formal.get('sources') != source_pins or formal.get('outcome') != 'compared':
                raise ValueError(f'{component} Specs were not compared against their requested pins')
            if formal.get('translation', {}).get('status') != 'matched':
                raise ValueError(f'{component} Spec translation is unresolved')
            directions = formal.get('directions', {})
            if not directions or any(row.get('status') != 'matched' for row in directions.values()):
                raise ValueError(f'{component} Spec comparison is not matched')
        shape = report['formal']['C52']['lean'].removeprefix('import Lean\n')
        shape = shape.replace('namespace AnechoicSpec', 'namespace ShapeWitness').replace('end AnechoicSpec', 'end ShapeWitness')
        authored = shape + '\n' + report['formal']['C87']['lean'].removeprefix('import Lean\n')
        root = Path(root).resolve(strict=True)
        export = report['public_export'] = export_pin(root / _SOURCE_DIR, 'render_solution', root, request.get('export_sha256'))
        cases, gap = _renderer_results(_observe(root, digests, export, authored, lean))
    except (OSError, ValueError, SyntaxError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        report['unresolved'].append(str(error))
        return report
    export['status'] = 'matched'
    report['cases'] = cases
    report['solution_gap'] = gap
    if gap is not None:
        report['unresolved'].append(gap)
    values = [case['status'] for case in cases]
    if any(value.startswith('unresolved') for value in values):
        report['unresolved'].append('Renderer execution is unresolved in at least one case.')
    if 'conflicting' in values:
        report['status'] = 'mismatch'
    elif gap is None and values == ['matched'] * len(_ORDERS):
        report['status'] = 'no_mismatch_in_cases'
    return report
