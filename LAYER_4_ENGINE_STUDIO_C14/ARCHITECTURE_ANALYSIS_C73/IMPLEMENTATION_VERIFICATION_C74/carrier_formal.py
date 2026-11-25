"""Bind the carrier pilot to its authored Manifest, Contract, and Draft Solution."""
import hashlib
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    formal_claim_fences,
    parse_carrier,
    parse_component_manifest,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import (
    derive_atom_ref,
)
from SPEC_ENGINE_C75.carrier_framing__pub import framing_to_lean, parse_framing

_BASE = ('_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/'
         'FEATURE_PROGRAMMATIC_C15/FEATURE_TOOLS_C16/')
_PATHS = {
    'manifest': _BASE + '_SPEC/AN-S-3069-SPEC-COMPONENT_MANIFEST--declare-adapters.md',
    'contract': _BASE + 'ADAPTERS_C30/01_draft/AN-S-3303@16-draft-SWD-COMPONENT_CONTRACT--read-guarded-filesystem-inputs.md',
    'solution': _BASE + 'ADAPTERS_C30/01_draft/AN-S-4742@1-draft-SWD-DECISION--extract-the-carrier-body.md',
}


def _carrier(root, name, identity, status):
    path = Path(root) / _PATHS[name]
    raw = path.read_bytes()
    parsed = parse_carrier(raw, path)
    meta = parsed.metadata
    state = meta.get('state', {})
    if (meta.get('atom_id') != identity or meta.get('atom_family') != 'SPEC'
            or state.get('status') != status or type(state.get('version')) is not int):
        raise ValueError('invalid ' + name + ' identity or state')
    evidence = {'path': _PATHS[name], 'atom_id': identity, 'status': status,
                'version': state['version'], 'sha256': hashlib.sha256(raw).hexdigest()}
    return parsed, evidence


def _lean_block(parsed, evidence, role):
    blocks = list(formal_claim_fences(parsed.body))
    if len(blocks) != 1 or blocks[0][0] != 'python framing':
        raise ValueError('expected exactly one python framing formal claim in ' + evidence['atom_id'])
    source = blocks[0][1]
    evidence['formal_sha256'] = hashlib.sha256(source.encode()).hexdigest()
    return framing_to_lean(parse_framing(source, role), role)


def formal_inputs(root):
    """Return independent claims and source pins, rejecting unbound carriers."""
    manifest, me = _carrier(root, 'manifest', 'AN-S-3069', 'active')
    contract, ce = _carrier(root, 'contract', 'AN-S-3303', 'draft')
    solution, se = _carrier(root, 'solution', 'AN-S-4742', 'draft')
    fields = parse_component_manifest(manifest.body)[0]
    if fields.get('component_id') != 'C30':
        raise ValueError('Manifest does not bind component C30')
    if (ce['version'] != 16 or se['version'] != 1
            or contract.metadata.get('container', {}).get('component') != 'C30'
            or solution.metadata.get('container', {}).get('component') != 'C30'
            or 'AN-S-3069' not in contract.metadata.get('relations', {}).get('ANSWERS', [])
            or derive_atom_ref(ce['atom_id'], ce['version'], ce['status']) not in solution.metadata.get('relations', {}).get('IS_SOLUTION_FOR', [])):
        raise ValueError('Contract or Solution binding does not match the current carriers')
    blocks = [_lean_block(contract, ce, 'contract'), _lean_block(solution, se, 'solution')]
    return blocks, {'manifest': me, 'contract': ce, 'solution': se}
