import unittest

from ATOM_LIFECYCLE.header_constraints import compile_header_constraints, load_header_constraints


def declaration(source, name, base, **constraints):
    args = ', '.join(f'{key}={value!r}' for key, value in constraints.items())
    body = ('## Claim\n### Formal Claim\n```python\n'
            'from anechoic.formal_claims import declare_entity\n'
            f'declare_entity(entity_name={name!r}, base_path={base!r}, '
            f'relation_name="IS_PROPERTY_OF", {args})\n```\n')
    return {'id': source, '_content_bytes': body.encode()}


def compile_schema(rows):
    records = compile_header_constraints(rows)
    return load_header_constraints(records, {row['id'] for row in rows})


def test_native_property_domain_and_direct_value_cardinality():
    rows = [
        declaration('CA-R-1', 'Tier', 'Atom.Header.Context',
                    property_occurrence_cardinality=1, value_format='int', value_cardinality=1),
        declaration('CA-R-2', 'Priority', 'Atom/(.Header.Context.Role:=Concern).Header.Context.Concern',
                    property_occurrence_cardinality=1, value_format='str', value_cardinality=1,
                    allowed_values=('High', 'Medium', 'Low')),
        declaration('CA-R-3', 'Label', 'Atom.Header.Context', value_format='str',
                    value_cardinality={'minimum': 0, 'maximum': 1}),
    ]
    schema = compile_schema(rows)
    assert schema.validate({'role': 'Concern', 'tier': 1, 'priority': 'High'}) == []
    assert {field for field, _, _ in schema.validate({'role': 'Concern', 'priority': 'Unknown'})} == {'tier', 'priority'}
    assert {field for field, _, _ in schema.validate({'role': 'Plan', 'tier': 1, 'label': ['a', 'b']})} == {'label'}


def test_native_group_constraints_accept_equivalent_flat_and_nested_headers():
    rows = [
        declaration('CA-R-1', 'Identity', 'Atom.Header', property_occurrence_cardinality=1,
                    value_cardinality=0, dependent_property_cardinality=2,
                    allowed_dependent_property_names=('ID', 'Ref ID')),
        declaration('CA-R-2', 'Context', 'Atom.Header', property_occurrence_cardinality=1,
                    value_cardinality=0, dependent_property_cardinality={'minimum': 5, 'maximum': 7},
                    allowed_dependent_property_names=('Container', 'Role', 'Form', 'Label', 'Topics', 'Tier', 'Plan', 'Concern')),
        declaration('CA-R-3', 'State', 'Atom.Header', property_occurrence_cardinality=1,
                    value_cardinality=0, dependent_property_cardinality=3,
                    allowed_dependent_property_names=('Status', 'Version', 'Updated At')),
        declaration('CA-R-4', 'Concern', 'Atom.Header.Context', property_occurrence_cardinality=1,
                    value_cardinality=0, dependent_property_cardinality=1,
                    allowed_dependent_property_names=('Priority',), applies_to_entity_classes=('Concern',)),
    ]
    schema = compile_schema(rows)
    identity = {'id': 'CA-C-1', 'ref_id': 'CA-C-1'}
    context = {'container': {'scope_unit': 'CA-SU-00'}, 'role': 'concern', 'form': 'problem',
               'topics': {'main_subject': 'Atom'}, 'tier': 1}
    state = {'status': 'active', 'version': 1, 'updated_at': 'now'}
    flat = {**identity, **context, **state, 'atom_id': identity['id'], 'priority': 'High'}
    grouped = {'identity': identity, 'context': {**context, 'concern': {'priority': 'High'}}, 'state': state}
    assert schema.validate(flat) == []
    assert schema.validate({'role': 'Concern'}, metadata=grouped) == []
    assert schema.validate({'role': 'Concern'}, metadata={**grouped, 'identity': {**identity, 'extra': 'X'}})
    assert {field for field, _, _ in schema.validate({key: value for key, value in flat.items() if key != 'priority'})} == {'priority'}


def test_native_relations_require_one_or_more_targets():
    row = declaration('CA-R-1', 'Relations', 'Atom.Header', value_cardinality=0,
                      dependent_property_cardinality={'minimum': 1, 'maximum': None},
                      dependent_property_name_format='str', dependent_property_value_format='str',
                      dependent_property_value_cardinality={'minimum': 1, 'maximum': None})
    schema = compile_schema([row])
    assert schema.validate({'relations': {'uses': ['A', 'B']}}) == []
    assert {field for field, _, _ in schema.validate({'relations': {'uses': []}})} == {'relations.uses'}


def test_header_cardinality_asset_rejects_bad_bounds():
    row = {'kind': 'value', 'path': 'tags', 'selector': '', 'selected': '',
           'value': [1, 2], 'source': 'CA-R-1'}
    assert load_header_constraints([row], {'CA-R-1'}).values[0][3] == (1, 2)
    for bounds in ([2, 1], [-1, None], [1, True]):
        with unittest.TestCase().assertRaises(ValueError):
            load_header_constraints([{**row, 'value': bounds}], {'CA-R-1'})


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(test) for name, test in globals().items()
                              if name.startswith('test_') and callable(test))
