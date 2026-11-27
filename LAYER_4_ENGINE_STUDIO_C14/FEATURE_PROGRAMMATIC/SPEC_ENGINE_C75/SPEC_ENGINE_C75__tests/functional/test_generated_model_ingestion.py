"""Generate C50 CLI cases from the pinned Contract and Solution."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ENGINE = Path(__file__).resolve().parents[4]
COMPILER = 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub'
COMPILER_SHA256 = 'a' * 64


def project(directory):
    root = Path(directory).resolve() / 'project'
    (root / '_anechoic_anechoic').mkdir(parents=True)
    source, = ENGINE.parent.glob('AN-S-3037-SPEC-PROJECT_MANIFEST--*.md')
    data = source.read_bytes()
    (root / source.name).write_bytes(data)
    return root, sha256(data).hexdigest()


def compile_model(root, digest, stage, payload, *, observe=False):
    stage = stage.resolve()
    stage.mkdir()
    command = [sys.executable, '-B', '-P', '-m', COMPILER, str(root), '_anechoic_anechoic', digest,
               str(stage), '--ingested-model', '--attest-model']
    environment = {**os.environ, 'PYTHONPATH': str(ENGINE),
                   'ANECHOIC_STARTUP_TIMING': '1' if observe else '0'}
    return subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True,
                          cwd=ENGINE, env=environment, check=False)


def test_c50_formal_outcomes_drive_cli_cases():
    """Select CLI cases from the Contract and the Solution terminal outcomes."""
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain

    root = ENGINE.parent
    base = root / '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51'

    def pin(directory, atom, version, parent):
        drafts = (directory / '01_draft').glob(f'{atom}@{version}-draft-*.md')
        active = (directory / '01_TIER_1_ARCHITECTURE').glob(f'{atom}-*.md')
        for path in (*active, *directory.glob(f'{atom}-*.md'), *drafts):
            carrier = parse_carrier(path.read_bytes(), path)
            state = carrier.metadata['state']
            if state['version'] == version and state['status'] in ('active', 'draft'):
                return {'path': path.relative_to(root).as_posix(), 'atom_id': atom,
                        'version': version, 'status': state['status'],
                        'container_component': parent}
        raise AssertionError(f'{atom}@{version} is not available as Draft or Active')

    contract = pin(base, 'AN-S-3065', 38, 'C51')
    solution = pin(base / 'FEATURE_FORMAL_MODEL_GENERATOR_C50', 'AN-S-5015', 1, 'C50')
    lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or 'lean'
    report = verify_formal_chain(root, 'C50', contract, solution=solution,
                                 action='manifest_compile', lean=lean)
    assert report['outcome'] == 'compared', report
    assert report['translation']['status'] == 'matched'
    assert report['directions']['manifest_solution']['status'] == 'matched'
    assert not report['uncovered_outcomes']
    contract_outcomes = {fact['output'] for fact in report['evidence']['coverage']
                         if fact['key'] == 'terminal_output' and fact['status'] == 'matched'}

    with TemporaryDirectory() as tmp:
        project_root, digest = project(tmp)
        inputs = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None,
                  'compiler_sha256': COMPILER_SHA256}
        first = Path(tmp) / 'seed'
        seed = compile_model(project_root, digest, first, inputs)
        assert seed.returncode == 0, seed.stderr
        accepted = json.loads((first / 'model.json').read_text())
        tampered = {**accepted, 'module_sources': {**accepted['module_sources'], '__init__.py': 'tampered'}}
        fixtures = {
            'compiled': inputs,
            'reused': {**inputs, 'accepted_model': accepted},
            'fallback': {**inputs, 'has_c9': True, 'accepted_model': accepted},
            'failed': {**inputs, 'has_c9': True, 'accepted_model': tampered},
        }
        assert set(fixtures) == contract_outcomes
        observed_modes = {'compiled': 'built', 'reused': 'reused'}
        for outcome in sorted(contract_outcomes):
            stage = Path(tmp) / outcome
            result = compile_model(project_root, digest, stage, fixtures[outcome],
                                   observe=outcome in observed_modes)
            if outcome == 'failed':
                assert result.returncode != 0
                failure = json.loads(result.stderr)
                assert failure['error']['code'] == 'model_compile_failed'
                assert failure['model_diagnostics']
                continue
            assert result.returncode == 0, result.stderr
            response = json.loads(result.stdout)
            assert 'structure' in response
            raw = (stage / 'model.json').read_bytes()
            assert response['model_descriptor_sha256'] == sha256(raw).hexdigest()
            descriptor = json.loads(raw)
            if outcome in observed_modes:
                prefix = 'ANECHOIC_STARTUP_TIMING '
                events = [json.loads(line.removeprefix(prefix)) for line in result.stderr.splitlines()
                          if line.startswith(prefix)]
                phases = [(event['phase'], event.get('mode')) for event in events
                          if event['phase'] in ('model_ready', 'structure_ready')]
                assert phases == [('model_ready', observed_modes[outcome]), ('structure_ready', 'built')]
            if outcome == 'compiled':
                assert not response['model_diagnostics']
                assert descriptor['model_inputs_sha256']
            elif outcome == 'reused':
                assert not response['model_diagnostics']
                assert descriptor == accepted
            else:
                assert response['model_diagnostics']
                assert descriptor['model_sha256'] == accepted['model_sha256']
