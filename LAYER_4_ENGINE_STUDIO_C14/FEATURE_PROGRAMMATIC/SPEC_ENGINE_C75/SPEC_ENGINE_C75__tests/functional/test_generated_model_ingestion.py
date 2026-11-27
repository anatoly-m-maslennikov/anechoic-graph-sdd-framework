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
    command = [
        sys.executable,
        "-B",
        "-P",
        "-m",
        COMPILER,
        str(root),
        "_anechoic_anechoic",
        digest,
        str(stage),
        "--ingested-model",
        "--attest-model",
    ]
    environment = {
        **os.environ,
        "PYTHONPATH": str(ENGINE),
        "ANECHOIC_STARTUP_TIMING": "1" if observe else "0",
    }
    return subprocess.run(
        command,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=ENGINE,
        env=environment,
        check=False,
    )


def _contract_outcomes():
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 \
        .carrier_read__pub import parse_carrier
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain

    root = ENGINE.parent
    base = root / ('_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/'
                   'FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75/'
                   'LAYER_2_FORMAL_MODEL_C51')

    def pin(directory, atom, version, parent):
        drafts = (directory / '01_draft').glob(f'{atom}@{version}-draft-*.md')
        active = (directory / '01_TIER_1_ARCHITECTURE').glob(f'{atom}-*.md')
        for path in (*active, *directory.glob(f'{atom}-*.md'), *drafts):
            raw = path.read_bytes()
            carrier = parse_carrier(raw, path)
            state = carrier.metadata["state"]
            if state["version"] == version and state["status"] in (
                "active",
                "draft",
            ):
                return {
                    "path": path.relative_to(root).as_posix(),
                    "atom_id": atom,
                    "version": version,
                    "status": state["status"],
                    "container_component": parent,
                    "sha256": sha256(raw).hexdigest(),
                }
        raise AssertionError(f"{atom}@{version} is absent")

    contract = pin(base, 'AN-S-3065', 39, 'C51')
    solution = pin(base / 'FEATURE_FORMAL_MODEL_GENERATOR_C50',
                   'AN-S-5015', 2, 'C50')
    lean = (os.environ.get('ANECHOIC_TEST_LEAN')
            or os.environ.get('LEAN_BIN') or 'lean')
    report = verify_formal_chain(root, 'C50', contract, solution=solution,
                                 action='manifest_compile', lean=lean)
    assert report['outcome'] == 'compared', report
    assert report['translation']['status'] == 'matched'
    assert report['directions']['manifest_solution']['status'] == 'unresolved'
    assert not report['uncovered_outcomes']
    facts = report['evidence']['coverage']
    assert any(fact['key'] == 'same_values' for fact in facts)
    assert all(fact['status'] != 'conflicting' for fact in facts)
    return {fact['output'] for fact in facts
            if fact['key'] == 'action' and fact['status'] == 'matched'}


def _check_candidate(stage, outcome, result, accepted, mode):
    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    raw = (stage / 'model.json').read_bytes()
    descriptor = json.loads(raw)
    assert response['model_descriptor_sha256'] == sha256(raw).hexdigest()
    assert response['structure']['model_sha256'] == descriptor['model_sha256']
    if mode is not None:
        prefix = 'ANECHOIC_STARTUP_TIMING '
        events = [json.loads(line.removeprefix(prefix))
                  for line in result.stderr.splitlines()
                  if line.startswith(prefix)]
        phases = [(event['phase'], event.get('mode')) for event in events
                  if event['phase'] in ('model_ready', 'structure_ready')]
        assert phases == [('model_ready', mode), ('structure_ready', 'built')]
    if outcome == 'compiled':
        assert not response['model_diagnostics']
        assert descriptor['model_inputs_sha256']
    elif outcome == 'reused':
        assert not response['model_diagnostics']
        assert descriptor == accepted
    else:
        assert response['model_diagnostics']
        assert descriptor['model_sha256'] == accepted['model_sha256']

def test_c50_formal_outcomes_drive_cli_cases():
    """Exercise the declared outcomes and verify the selected Model."""
    contract_outcomes = _contract_outcomes()
    with TemporaryDirectory() as tmp:
        project_root, digest = project(tmp)
        inputs = {'rows': [], 'has_c9': False, 'issues': [],
                  'accepted_model': None, 'compiler_sha256': COMPILER_SHA256}
        first = Path(tmp) / 'seed'
        seed = compile_model(project_root, digest, first, inputs)
        assert seed.returncode == 0, seed.stderr
        accepted = json.loads((first / 'model.json').read_text())
        tampered = {**accepted, 'module_sources': {
            **accepted['module_sources'], '__init__.py': 'tampered'}}
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
            mode = observed_modes.get(outcome)
            result = compile_model(project_root, digest, stage,
                                   fixtures[outcome], observe=mode is not None)
            if outcome == 'failed':
                assert result.returncode != 0
                failure = json.loads(result.stderr)
                assert failure['error']['code'] == 'model_compile_failed'
                assert failure['model_diagnostics']
                continue
            _check_candidate(stage, outcome, result, accepted, mode)
