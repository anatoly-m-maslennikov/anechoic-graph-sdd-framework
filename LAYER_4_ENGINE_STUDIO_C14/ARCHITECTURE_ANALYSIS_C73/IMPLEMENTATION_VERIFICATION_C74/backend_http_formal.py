"""Compare the declared C45 Tool API with its active HTTP Contract."""
import hashlib
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    formal_claim_fences,
    parse_carrier,
    parse_component_manifest,
)

from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.lean_values__pub import lean_string
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.contract_model__pub import parse_contract
from SPEC_ENGINE_C75.LAYER_4_SPEC_COMPARISON_C88.tool_api_obligations__pub import manifest_tool_api

_BASE = '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/'
_PATHS = {
    'manifest': _BASE + '_SPEC/AN-S-3059-SPEC-COMPONENT_MANIFEST--declare-workbench-backend.md',
    'contract': _BASE + 'FEATURE_WORKBENCH_BACKEND_C45/AN-S-3185-SWD-COMPONENT_CONTRACT--run-one-read-only-workbench-query.md',
    'solution': _BASE + 'FEATURE_WORKBENCH_BACKEND_C45/01_TIER_1_ARCHITECTURE/AN-S-3371-DES-DECISION--run-one-validated-read-only-workbench-query.md',
}


def _carrier(root, name, identity, component):
    path = Path(root) / _PATHS[name]
    raw = path.read_bytes()
    parsed = parse_carrier(raw, path)
    meta = parsed.metadata
    state = meta.get('state', {})
    if (meta.get('atom_id') != identity or meta.get('atom_family') != 'SPEC'
            or meta.get('container', {}).get('component') != component
            or state.get('status') != 'active' or type(state.get('version')) is not int):
        raise ValueError('invalid ' + name + ' identity or state')
    return parsed, {'path': _PATHS[name], 'atom_id': identity, 'version': state['version'],
                    'sha256': hashlib.sha256(raw).hexdigest()}


def _facts(root):
    manifest, me = _carrier(root, 'manifest', 'AN-S-3059', 'C43')
    contract, ce = _carrier(root, 'contract', 'AN-S-3185', 'C45')
    solution, se = _carrier(root, 'solution', 'AN-S-3371', 'C45')
    if 'AN-S-3059' not in contract.metadata.get('relations', {}).get('ANSWERS', []):
        raise ValueError('Contract does not ANSWER the selected Manifest')
    fields = parse_component_manifest(manifest.body)[0]
    if fields.get('component_id') != 'C45':
        raise ValueError('Manifest does not declare C45')
    api = fields.get('boundaries', {}).get('io', {}).get('server', {}).get('tool_api')
    if not isinstance(api, dict):
        raise TypeError('Manifest boundaries.io.server.tool_api is missing or invalid')
    fences = list(formal_claim_fences(contract.body))
    if len(fences) != 1 or fences[0][0] != 'python contract':
        raise ValueError('expected exactly one python contract formal claim')
    claim = parse_contract(fences[0][1])
    outcomes = claim["outcomes"]
    facts = dict(claim["facts"])
    expected = {'operation': [claim["operation"]]}
    for key in ('interface.protocol', 'interface.transport', 'input_format.fields',
                'error_handling.error_fields'):
        if key in facts:
            expected[key] = facts[key]
    observed, extra = manifest_tool_api(api)
    return observed, expected, facts, outcomes, extra, solution, {
        'manifest': me, 'contract': ce, 'solution': se}


def _expected_lean(expected):
    values = ', '.join(f'({lean_string(k)}, [{", ".join(lean_string(v) for v in vals)}])'
                       for k, vals in sorted(expected.items()))
    expected_lean = ('namespace BackendHttpContract\ndef expected : List (String × Nat × String) := []\n'
                     f'def expectedChecks : List (String × List String) := [{values}]\n'
                     'end BackendHttpContract\n')
    return expected_lean
