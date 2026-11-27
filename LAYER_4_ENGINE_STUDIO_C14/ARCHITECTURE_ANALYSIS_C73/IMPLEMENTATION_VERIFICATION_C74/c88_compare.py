"""Compare the reviewed C88 public witness with fresh implementation Lean."""

import json
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from .c88_report import _ROWS, _result_status
from .diagnostic_compare import _execute

_REL = Path('LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/'
            'LAYER_2_FORMAL_SPECIFICATION_C94')
C88_SOURCE_PINS = {
    'LAYER_4_SPEC_COMPARISON_C88/top_down__pub.py':
        'bca25fce6afe81f6ba28525b145d5e8f44af65858accf68c2d39c66147d1086a',
    'LAYER_1_DIAGNOSTICS_C90/diagnostics__pub.py':
        '11d686c9eb26d4dcbbd329a05e2d455c02ceabf924928bf301608514825fd2df',
    'LAYER_1_DIAGNOSTICS_C90/_package__shared.py':
        '0940be82328ebe15ed38853cb06d54b803f5a93de06bd194815292f856b4991a',
    'LAYER_3_LEAN_TRANSLATOR_C84/lean_values__pub.py':
        '777358859e60b8d977390a8ea2eda3c61a1a5558b618bba1b9ba4d4f2242825c',
    'LAYER_3_LEAN_TRANSLATOR_C84/lean_check__pub.py':
        'fa8061bfb8c547608e558e2e62835b59748455b7795a0016d23819c4fddbca70',
    'LAYER_3_LEAN_TRANSLATOR_C84/_package__shared.py':
        '36708a997a3b5f8c26722e43db6398fa6ae56c4e1339025ad73df0f77c28ff61',
    'LAYER_4_SPEC_COMPARISON_C88/_package__shared.py':
        '00fc902282bb688d4abefeca45b4ef43343ecd41cc45e5d8c4480fd8335566d0',
}
_SPEC_BASE = ('_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/'
              'FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75/'
              'LAYER_2_FORMAL_SPECIFICATION_C94/')
SPEC_PINS = {
    'manifest': {'atom_id': 'AN-S-4935', 'version': 1, 'status': 'active',
                 'container_component': 'C94',
                 'path': _SPEC_BASE + '01_TIER_1_ARCHITECTURE/'
                 'AN-S-4935-SPEC-COMPONENT_MANIFEST--'
                 'declare-spec-comparison.md',
                 'sha256': '929c914afb640966de04ce2f96420b48'
                 '4a3eaaab991066c2eaf3203d10b2d9cd'},
    'solution': {'atom_id': 'AN-S-5030', 'version': 1, 'status': 'active',
                 'container_component': 'C88',
                 'path': _SPEC_BASE + 'LAYER_4_SPEC_COMPARISON_C88/'
                 'AN-S-5030-DES-SOLUTION--compare-formal-spec-obligations.md',
                 'sha256': 'ad6af299477be8d524d398f808d99acd'
                 '79b9ebc96361d7bb44a413dfe0d1822d'},
}
_DECLS = ('def manifest : List (String × String) := '
          '[("a", "2"), ("m", "8"), ("z", "1")]\n'
          'def contract : List (String × String) := '
          '[("a", "2"), ("z", "1")]\n'
          'def solution : List (String × String) := [("a", "2"), ("z", "3")]')
_CALLS = ('compare manifest contract, compare manifest solution, '
          'compare contract solution')
_WORKER_SHA = ('ecd51442045a764fe51a9bceb74f248d'
               '4b86c48b5d6d800cc8fe909e5a3276b6')
_TRANSLATOR = Path(__file__).with_name('code_to_lean.py')
_EXPORT_CHECK = '''
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
'''


def _lean_value(value):
    if value is None:
        return '.unit'
    if isinstance(value, str):
        return '(.str ' + json.dumps(value, ensure_ascii=False) + ')'
    if type(value) is int:
        return f'(.int {value})'
    if isinstance(value, dict):
        pairs = ', '.join(f'({_lean_value(k)}, {_lean_value(v)})'
                          for k, v in value.items())
        return '(.dict [' + pairs + '])'
    raise ValueError('unsupported source pin value')


def _read_pin(root, relative, digest):
    path = root / relative
    if path.resolve(strict=True) != path or not path.is_file():
        raise ValueError(f'noncanonical source: {relative}')
    if sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f'source digest changed: {relative}')
    return path


def _admit(root, request):
    pins = {role: request[role] for role in ('manifest', 'solution')}
    if (pins != SPEC_PINS or any(
            type(pin.get('version')) is not int for pin in pins.values())):
        raise ValueError('C88 witness requires the exact reviewed Spec pins')
    if request['implementation_sha256'] != C88_SOURCE_PINS:
        raise ValueError('C88 witness requires the exact reviewed source pins')
    for pin in pins.values():
        _read_pin(root, pin['path'], pin['sha256'])
    for relative, digest in C88_SOURCE_PINS.items():
        _read_pin(root, _REL / relative, digest)
    return pins


def _quoted(value):
    return json.dumps(value, ensure_ascii=False)


def _input_defs(sources, worker_path, lean):
    return ('\nopen Autoform.Core Autoform.Generated.Implementation\n'
            + 'def c88ObservedSources : Val := ' + _lean_value(sources) + '\n'
            + 'def c88ObservedDeclarations := ' + _quoted(_DECLS) + '\n'
            + 'def c88ObservedCalls := ' + _quoted(_CALLS) + '\n'
            + 'def c88WorkerPath := ' + _quoted(str(worker_path)) + '\n'
            + 'def c88ObservedRunner := ' + _quoted(lean) + '\n')


def _observed_defs(worker, rows):
    values = ', '.join('[' + ', '.join(map(_quoted, row)) + ']'
                       for row in rows)
    return ('def c88ObservedWorker := ' + _quoted(worker) + '\n'
            + 'def c88ObservedRows : List (List String) := [' + values + ']\n')


def _emit_worker(source, harness, path, lean):
    prefix, separator, _ = harness.partition('\ndef withJoins :')
    if not separator:
        raise ValueError('C88 worker harness is missing')
    path.write_text(source + prefix + '''
#eval show IO Unit from do
  match renderWorker with
  | .val (.str text) => IO.FS.writeFile c88WorkerPath text
  | other => throw (IO.userError (reprStr other))
end C88PublicWitness
''', encoding='utf-8')
    _execute([lean, str(path)], 120)


def _observe(root, pins, authored, lean):
    names = list(C88_SOURCE_PINS)
    selected = names[:3] + [names[-1]]
    paths = [root / _REL / name for name in selected]
    with TemporaryDirectory(prefix='anechoic-c88-lean-') as folder:
        folder = Path(folder)
        model, worker = folder / 'Implementation.lean', folder / 'Worker.lean'
        hashes = [part for name in selected
                  for part in ('--sha256', C88_SOURCE_PINS[name])]
        _execute([sys.executable, '-B', str(_TRANSLATOR), *map(str, paths),
                  *hashes, '--output', str(model)], 1800)
        source = model.read_text(encoding='utf-8')
        sources = {**pins, 'contract': pins['manifest']}
        data = _input_defs(sources, worker, lean)
        artifact = Path(__file__).with_name('c88_public_witness.lean')
        harness = artifact.read_text(encoding='utf-8')
        _emit_worker(source + data, harness, folder / 'Render.lean', lean)
        worker_bytes = worker.read_bytes()
        if sha256(worker_bytes).hexdigest() != _WORKER_SHA:
            raise ValueError('generated worker differs from reviewed witness')
        rows = json.loads(_execute([lean, str(worker)], 120))
        if rows != _ROWS:
            raise ValueError('worker output differs from the reviewed witness')
        program = folder / 'PublicComparison.lean'
        authored = authored.lstrip().removeprefix('import Lean\n')
        program.write_text(source + '\n' + authored + data
                           + _observed_defs(worker_bytes.decode(), rows)
                           + _EXPORT_CHECK
                           + harness, encoding='utf-8')
        result = json.loads(_execute([lean, str(program)], 120))
        evidence = {'model_sha256': sha256(source.encode()).hexdigest(),
                    'worker_sha256': _WORKER_SHA,
                    'harness_sha256': sha256(harness.encode()).hexdigest(),
                    'lean': lean,
                    'lean_sha256': sha256(Path(lean).read_bytes()).hexdigest()}
        return result, evidence


def compare_c88(root, request, formal_verifier, lean):
    """Check one pinned mixed-input public call and report its limits."""
    report = {'status': 'unresolved', 'formal': {}, 'public_report': None,
              'implementation': {}, 'unresolved': [
                  'Other inputs, serialization, importability, and process '
                  'effects are unverified.',
                  'The join and worker observations cover one fixed input.']}
    try:
        root = Path(root).resolve(strict=True)
        pins = _admit(root, request)
        report['implementation'] = {
            (_REL / name).as_posix(): digest
            for name, digest in C88_SOURCE_PINS.items()}
        formal = report['formal'] = formal_verifier(
            root, 'C88', **pins, action='compare_obligations', lean=lean)
        if (formal.get('sources') != pins
                or formal.get('outcome') != 'compared'):
            raise ValueError('C88 Specs were not compared against their pins')
        if formal.get('translation', {}).get('status') != 'matched':
            raise ValueError('C88 Spec translation is unresolved')
        directions = formal.get('directions', {})
        if not directions or any(row.get('status') != 'matched'
                                 for row in directions.values()):
            raise ValueError('C88 Spec directions are not matched')
        executable = shutil.which(lean)
        if executable is None:
            raise ValueError('Lean executable unavailable')
        selected = str(Path(executable).resolve(strict=True))
        observed, report['witness'] = _observe(
            root, pins, formal['lean'], selected)
        report['status'] = _result_status(observed, pins)
        report['public_report'] = observed['report']
        report['direction_order'] = observed['direction_order']
        directions = report['public_report']['directions']
        report['public_report']['directions'] = {
            name: directions[name] for name in report['direction_order']}
        report['formal_path'] = observed['formal_path']
        report['observations'] = observed['observations']
        report['unresolved'].extend(observed['unresolved'])
        if observed['formal_path'] != 'matched':
            report['unresolved'].append('C88 authored path is unresolved.')
    except (OSError, ValueError, SyntaxError, KeyError, TypeError,
            subprocess.TimeoutExpired) as error:
        report['unresolved'].append(str(error))
    return report
