"""Lower the bounded C45 HTTP Contract to a Lean value without executing it."""
from pathlib import Path

from SPEC_ENGINE_C75.contract_model__pub import lean_string, parse_contract

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    formal_claim_fences,
    parse_carrier,
)


def contract_to_lean(path: Path) -> str:
    """Read the active C45 Contract and lower its one supported formal claim."""
    parsed = parse_carrier(path.read_bytes(), path)
    meta = parsed.metadata
    state = meta.get('state', {})
    if (meta.get('atom_id') != 'AN-S-3185' or meta.get('atom_family') != 'SPEC'
            or meta.get('container', {}).get('component') != 'C45'
            or state.get('status') != 'active' or type(state.get('version')) is not int):
        raise ValueError('invalid Contract identity or state')
    fences = list(formal_claim_fences(parsed.body))
    if len(fences) != 1 or fences[0][0] != 'python contract':
        raise ValueError('expected exactly one python contract formal claim')
    claim = parse_contract(fences[0][1])
    rows = claim["outcomes"]
    values = ', '.join(f'("{name}", {status}, "{kind}")' for name, status, kind in rows)
    checks = claim["facts"]
    check_values = ', '.join(
        f'({lean_string(name)}, [{", ".join(lean_string(value) for value in items)}])'
        for name, items in checks
    )
    return ('namespace BackendHttpContract\n'
            f'def expected : List (String × Nat × String) := [{values}]\n'
            f'def expectedChecks : List (String × List String) := [{check_values}]\n'
            'end BackendHttpContract\n')
