"""Bind the carrier pilot to its authored Manifest, Contract, and Draft Solution."""
import hashlib
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    formal_claim_fences,
    parse_carrier,
    parse_component_manifest,
)

_BASE = ('_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/'
         'FEATURE_PROGRAMMATIC_C15/FEATURE_TOOLS_C16/')
_PATHS = {
    'manifest': _BASE + '_SPEC/AN-S-3069-SPEC-COMPONENT_MANIFEST--declare-adapters.md',
    'contract': _BASE + 'ADAPTERS_C30/AN-S-3303-SWD-COMPONENT_CONTRACT--read-guarded-filesystem-inputs.md',
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


def _lean_block(parsed, evidence):
    blocks = [text for lang, text in formal_claim_fences(parsed.body) if lang == 'lean']
    if len(blocks) != 1:
        raise ValueError('expected exactly one Lean formal claim in ' + evidence['atom_id'])
    evidence['formal_sha256'] = hashlib.sha256(blocks[0].encode()).hexdigest()
    return blocks[0]


def formal_inputs(root):
    """Return independent claims and source pins, rejecting unbound carriers."""
    manifest, me = _carrier(root, 'manifest', 'AN-S-3069', 'active')
    contract, ce = _carrier(root, 'contract', 'AN-S-3303', 'active')
    solution, se = _carrier(root, 'solution', 'AN-S-4742', 'draft')
    fields = parse_component_manifest(manifest.body)[0]
    exports = fields.get('boundaries', {}).get('code', {}).get('exports', {})
    required = ('frontmatter_bounds', 'source_body')
    if fields.get('component_id') != 'C30' or any(
        exports.get('ADAPTERS_C30__shared.' + name) != 'public' for name in required
    ):
        raise ValueError('C30 Manifest does not expose the required symbols')
    if (se['version'] != 1
            or contract.metadata.get('container', {}).get('component') != 'C30'
            or solution.metadata.get('container', {}).get('component') != 'C30'
            or 'AN-S-3069' not in contract.metadata.get('relations', {}).get('ANSWERS', [])
            or f"AN-S-3303@{ce['version']}" not in solution.metadata.get('relations', {}).get('IS_SOLUTION_FOR', [])):
        raise ValueError('Contract or Solution binding does not match the current carriers')
    blocks = [_lean_block(contract, ce), _lean_block(solution, se)]
    return blocks, {'manifest': me, 'contract': ce, 'solution': se}
