"""Compile legacy revision population declarations."""

def compile_atom_population_model(rows):
    from FEATURE_FORMAL_MODEL_ENGINE.model_catalog import _native_block
    from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
    from header_groups import header_value
    from lint_python_model_claim import _canonical_address

    selected = {}
    for row in rows:
        _, subject = header_value(row['header_json'], 'topics.main_subject')
        if not isinstance(subject, str) or not subject.startswith('ANECHOIC_MODEL'):
            continue
        address = _canonical_address(subject)
        if address in {'Atom', 'Atom.Content.Summary'}:
            for code in _native_block(row['_content_bytes'].decode('utf-8')):
                if claim := parse_native_model_claim(code):
                    selected[address] = claim['arguments']
    if not selected:
        return False
    atom, summary = selected.get('Atom', {}), selected.get('Atom.Content.Summary', {})
    identity = atom.get('population_unique_constraints')
    summaries = summary.get('population_functional_dependencies')
    if not identity and not summaries:
        return False
    if (identity != ({'keys': ('Header.Identity.ID', 'Header.State.Version')},)
            or summaries != ({'keys': ('Header.Identity.ID',), 'dependents': ('Content.Summary',),
                              'status_groups': ('Current', 'Backlog', 'Archived')},)):
        raise ValueError('Atom population Declarations differ from the supported revision checks')
    return True
