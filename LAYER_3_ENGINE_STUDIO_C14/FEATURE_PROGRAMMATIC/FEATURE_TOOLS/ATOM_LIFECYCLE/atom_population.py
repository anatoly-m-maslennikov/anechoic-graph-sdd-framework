"""Compile legacy revision population declarations."""

def compile_atom_population_model(rows):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.formal_claim__pub import iter_formal_claims
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_model_claim__pub import parse_native_model_claim
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import header_value
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import canonical_model_address

    selected = {}
    for row in rows:
        _, subject = header_value(row['header_json'], 'topics.main_subject')
        if not isinstance(subject, str) or not subject.startswith('ANECHOIC_MODEL'):
            continue
        address = canonical_model_address(subject)
        if address in {'Atom', 'Atom.Content.Summary'}:
            for code in iter_formal_claims(row['_content_bytes'].decode('utf-8')):
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
