import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_property_relation_lowering import (
    declared_relation_names, lower_typed_fields,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_native_model_claim,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import (
    validate_relation_endpoint_levels,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.model_relation_validation import validate_model_relations

ADDRESSES = {'Atom': 'Node//Artifact//Atom', 'Project': 'Node//Artifact//Component//Project', 'Atom.Header': 'Node//Artifact//Atom.Header', 'Atom.Header.AtomID': 'Node//Artifact//Atom.Header.Atom ID'}


_ATOM_RELATIONS = '''from anechoic.model import Atom, Property, Relation
from anechoic.formal_claims import Cardinality
class atom_relations(Property):
    name = 'Relations'
    bearer = Atom.Header
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 0
    property.dependent_property.name.allowed = Relation.subclasses().name
    property.dependent_property.cardinality = 1
    property.dependent_property.value.cardinality = 2
    property.dependent_property.value.format = Relation.target_references()
    field_options = {'default': None, 'kw_only': True}
'''


def test_atom_relations_use_explicit_relation_names_and_target_references():
    text = _ATOM_RELATIONS
    explicit = '''from anechoic.model import Relation
class Reference(Relation):
    name = 'IS_REFERENCE'
    inverse_alias = 'HAS_REFERENCE'
'''
    derived = ('from anechoic.formal_claims import declare_relation\n'
               "declare_relation(relation_name='DERIVED_REFERENCE', derived_from='IS_REFERENCE', "
               "source_endpoint={'level': 'instances'}, target_endpoint={'level': 'instances'})\n")
    records = [('derived', 'MODEL//ANECHOIC <+ Graph/Relation//DERIVED_REFERENCE', derived)]
    typed_derivation = """from anechoic.model import Relation
class RecursiveReference(Relation):
    name = 'RECURSIVE_REFERENCE'
    relation.derived_from = 'IS_REFERENCE'
    relation.source_endpoint = {'level': 'instances'}
    relation.target_endpoint = {'level': 'instances'}
"""
    derived_scope = 'MODEL//ANECHOIC <+ Graph/Relation//RECURSIVE_REFERENCE'
    fields = [
        ('reference', 'MODEL//ANECHOIC <+ Graph/Relation//IS_REFERENCE', explicit, 'manifest_relation'),
        ('recursive', derived_scope, typed_derivation, 'manifest_relation'),
    ]
    names = declared_relation_names(records, fields)
    claim = lower_typed_fields('manifest_property', text, '', ADDRESSES, relation_names=names)
    arguments = parse_native_model_claim(claim)['arguments']
    assert arguments['allowed_relation_names'] == ('IS_REFERENCE',)
    lowered = lower_typed_fields('manifest_relation', typed_derivation, derived_scope, ADDRESSES)
    assert parse_native_model_claim(lowered)['arguments']['derived_from'] == 'IS_REFERENCE'
    assert arguments['property_occurrence_cardinality'] == {'minimum': 0, 'maximum': 1}
    assert arguments['dependent_property_cardinality'] == 1
    assert arguments['dependent_property_value_cardinality'] == 2
    assert arguments['dependent_property_value_format'] == 'atom_reference'
    assert arguments['value_cardinality'] == 0
    assert arguments['value_format'] == 'dict[str, list[str]] | None'
    _assert_invalid_relation_selectors(text, names)


def _assert_invalid_relation_selectors(text, names):
    for invalid in (
        text.replace('Relation.target_references()', 'str'),
        text.replace('Relation.subclasses().name', 'Relation.subclasses()'),
        text.replace('Relation.subclasses().name', 'Relation.subclasses().inverse_alias'),
    ):
        with unittest.TestCase().assertRaisesRegex(ValueError, 'both Relation selectors'):
            lower_typed_fields('manifest_property', invalid, '', ADDRESSES, relation_names=names)
    with unittest.TestCase().assertRaisesRegex(ValueError, 'duplicate or unsupported typed field'):
        lower_typed_fields('manifest_property', text + '    dependent_property_cardinality = 1\n',
                           '', ADDRESSES, relation_names=names)


def test_property_lowering_preserves_constraints_and_refs():
    text = '''from anechoic.model import Property, Atom, Project
class AtomTier(Property):
    name = "Tier"
    bearer = Atom.Header
    value_format = int
    field_options = {"kw_only": True}
    allowed_values = (0, 1)
    applies_to_entity_classes = (Project,)
'''
    result = parse_native_model_claim(lower_typed_fields('manifest_property', text, '', ADDRESSES))['arguments']
    assert result['entity_name'] == 'Tier'
    assert result['base_path'] == 'Node//Artifact//Atom.Header'
    assert result['applies_to_entity_classes'] == ('Node//Artifact//Component//Project',)
    assert result['allowed_values'] == (0, 1)


def test_content_constraints_survive_typed_lowering():
    text = """from anechoic.model import Property, Atom, Requirement, Method, Evaluation, Delivery
from anechoic.formal_claims import Cardinality
class Content(Property):
    bearer = Atom
    property_occurrence_cardinality = 1
    value_cardinality = 0
    dependent_property_cardinality = Cardinality(minimum=0, maximum=None)
    dependent_property_name_format = str
    recursive_dependent_property_cardinality = Cardinality(minimum=0, maximum=None)
    recursive_dependent_property_name_format = str
    recursive_dependent_property_value_format = 'markdown'
    ordered_dependent_property_roles = (Requirement, Method, Evaluation, Delivery)
    ordered_dependent_property_pairs = (('Summary', 'Claim'), ('Claim', 'Semantics'), ('Semantics', 'Details'))
"""
    result = parse_native_model_claim(lower_typed_fields('manifest_property', text, '', ADDRESSES))['arguments']
    assert result['dependent_property_cardinality'] == {'minimum': 0, 'maximum': None}
    assert result['dependent_property_name_format'] == 'str'
    assert result['recursive_dependent_property_cardinality'] == {'minimum': 0, 'maximum': None}
    assert result['recursive_dependent_property_name_format'] == 'str'
    assert result['recursive_dependent_property_value_format'] == 'markdown'
    assert result['ordered_dependent_property_roles'] == ('Requirement', 'Method', 'Evaluation', 'Delivery')
    assert result['ordered_dependent_property_pairs'] == (('Summary', 'Claim'), ('Claim', 'Semantics'), ('Semantics', 'Details'))


def test_relation_endpoint_pairs_preserve_disjoint_shapes():
    text = '''from anechoic.model import Relation, Atom, Project
class IS_CONTAINED_BY(Relation):
    endpoint_pairs = (
        {"source_endpoint": {"level": "instances", "entity_paths": (Atom,)},
         "target_endpoint": {"level": "instances", "entity_paths": (Project,)}},
    )
    inverse_alias = "CONTAINS"
'''
    result = parse_native_model_claim(lower_typed_fields('manifest_relation', text, '', ADDRESSES))['arguments']
    assert result['endpoint_pairs'][0]['source_endpoint']['entity_paths'] == ('Node//Artifact//Atom',)
    assert result['inverse_alias'] == 'CONTAINS'


def test_relation_axes_use_native_validation():
    text = ("from anechoic.model import Relation\nclass LINK(Relation):\n"
            "    source_endpoint = {}\n    target_endpoint = {}\n"
            "    inverse_alias = 'LINKED_BY'\n"
            "    relation.axes = {'Functional': 'no', 'Transitive': 'no'}\n"
            "    relation.inverse_axes = {'Functional': 'no'}\n")
    args = parse_native_model_claim(lower_typed_fields('manifest_relation', text, '', {}))['arguments']
    assert args['axes'] == {'Functional': 'no', 'Transitive': 'no'}
    assert args['inverse_axes'] == {'Functional': 'no'}
    for invalid in (text.replace("'Functional': 'no'", "'Functional': ''"),
                    text.replace("    inverse_alias = 'LINKED_BY'\n", '')):
        with unittest.TestCase().assertRaises(ValueError):
            parse_native_model_claim(lower_typed_fields('manifest_relation', invalid, '', {}))
    with unittest.TestCase().assertRaisesRegex(ValueError, 'duplicate or unsupported'):
        lower_typed_fields('manifest_relation', text + "    axes = {'Functional': 'yes'}\n", '', {})


def test_relation_forbidden_status_pairs_require_distinct_literal_pairs():
    prefix = ('from anechoic.model import Relation\nclass REPLACES(Relation):\n'
              '    source_endpoint = {}\n    target_endpoint = {}\n'
              '    relation.forbidden_status_pairs = ')
    valid = "(('active', 'active'), ('draft', 'active'), ('active', 'draft'))"
    result = parse_native_model_claim(lower_typed_fields('manifest_relation', prefix + valid, '', {}))
    assert result['arguments']['forbidden_status_pairs'] == (
        ('active', 'active'), ('draft', 'active'), ('active', 'draft'),
    )
    for invalid in ('()', "('active', 'active')", "(('active',),)", "(('active', 1),)",
                    "(('active', ''),)", "(('active', ' active'),)", "(('active', str),)",
                    "[('active', 'active'), ['active', 'active']]"):
        with unittest.TestCase().assertRaisesRegex(ValueError, 'forbidden_status_pairs'):
            parse_native_model_claim(lower_typed_fields('manifest_relation', prefix + invalid, '', {}))


def test_core_relations_fold_and_enforce_endpoint_levels():
    relations = (
        ('IS_NARROWER_THAN', 'model_entities', 'model_entities', 'HAS_NARROWER', 'reverse_written_alias', '/'),
        ('IS_INSTANCE_OF', 'instances', 'model_entities', 'HAS_INSTANCE', 'written_alias', '//'),
    )
    for name, source, target, inverse, alias_key, alias in relations:
        typed = (f'from anechoic.model import Relation\nclass {name}(Relation):\n'
                 f'    source_endpoint = {{"level": {source!r}}}\n'
                 f'    target_endpoint = {{"level": {target!r}}}\n'
                 f'    inverse_alias = {inverse!r}\n    {alias_key} = {alias!r}\n')
        legacy = ('from anechoic.formal_claims import declare_relation\n'
                  f'declare_relation(relation_name={name!r}, source_endpoint={{"level": {source!r}}}, '
                  f'target_endpoint={{"level": {target!r}}}, inverse_alias={inverse!r}, {alias_key}={alias!r})')
        parsed = parse_native_model_claim(lower_typed_fields('manifest_relation', typed, '', {}))
        assert parsed == parse_native_model_claim(legacy)
        validate_relation_endpoint_levels(parsed, name, source, target)
        validate_relation_endpoint_levels(parsed, inverse, target, source)
        with unittest.TestCase().assertRaisesRegex(ValueError, 'endpoint levels or kinds'):
            validate_relation_endpoint_levels(parsed, name, source, 'instances')
        if name == 'IS_INSTANCE_OF':
            class Node:
                pass
            registry = {name: (parsed['arguments'], False)}
            validate_model_relations(Node, {name: [Node]}, {Node: {}}, {'Node': Node}, endpoint_registry=registry)
            with unittest.TestCase().assertRaisesRegex(ValueError, 'endpoint levels or kinds'):
                validate_model_relations(Node, {name: [Node()]}, {Node: {}}, {'Node': Node}, endpoint_registry=registry)


def test_written_alias_uses_native_parser_validation():
    typed = 'from anechoic.model import Relation\nclass R(Relation):\n    written_alias = ""\n'
    with unittest.TestCase().assertRaises(ValueError):
        parse_native_model_claim(lower_typed_fields('manifest_relation', typed, '', {}))



def test_cardinality_is_validated_by_native_parser():
    text = """from anechoic.model import Property, Atom
from anechoic.formal_claims import Cardinality
class Concern(Property):
    bearer = Atom.Header
    value_format = object
    property_occurrence_cardinality = Cardinality(minimum=0, maximum=1)
"""
    result = parse_native_model_claim(lower_typed_fields('manifest_property', text, '', ADDRESSES))['arguments']
    assert result['property_occurrence_cardinality'] == {'minimum': 0, 'maximum': 1}


def test_value_forms_and_existing_options():
    prefix = "from anechoic.model import Property, Atom\nfrom anechoic.formal_claims import value\nclass Tier(Property):\n    bearer = Atom.Header\n    value_format = int\n"
    fixed = parse_native_model_claim(lower_typed_fields('manifest_property', prefix + "    value = value(fixed=0)\n    field_options = {'kw_only': True}\n", '', ADDRESSES))['arguments']
    assert fixed['allowed_values'] == (0,)
    default = parse_native_model_claim(lower_typed_fields('manifest_property', prefix + "    value = value(default=1)\n    allowed_values = (0, 1)\n    field_options = {'kw_only': True}\n", '', ADDRESSES))['arguments']
    assert default['field_options'] == {'kw_only': True, 'default': 1}
    assert default['allowed_values'] == (0, 1)
    for suffix in ("    value = value(fixed=0)\n    allowed_values = (1,)\n", "    value = value(default=0)\n    field_options = {'default_factory': 'dict'}\n"):
        with unittest.TestCase().assertRaises(ValueError):
            lower_typed_fields('manifest_property', prefix + suffix, '', ADDRESSES)


def test_dotted_reference_requires_exact_alias_and_preserves_spaces():
    text = "from anechoic.model import Property, Atom\nclass Identifier(Property):\n    bearer = Atom.Header.AtomID\n    value_format = str\n"
    args = parse_native_model_claim(lower_typed_fields('manifest_property', text, '', ADDRESSES))['arguments']
    assert args['base_path'] == 'Node//Artifact//Atom.Header.Atom ID'
    with unittest.TestCase().assertRaises(ValueError):
        lower_typed_fields('manifest_property', text, '', {'Atom': ADDRESSES['Atom']})


def test_relation_axis_domain_comes_from_the_manifest():
    for axis, values in (('Transitive', ('no', 'yes')), ('Symmetric', ('stated', 'derived'))):
        text = (f"from anechoic.model import Property, Relation\nclass {axis}(Property):\n"
                f"    bearer = Relation\n    classification = True\n    allowed_values = {values!r}\n")
        subject = f'MODEL//ANECHOIC <+ Graph/Relation >| {axis}'
        args = parse_native_model_claim(lower_typed_fields('manifest_property', text, subject, {'Relation': 'Graph/Relation'}))['arguments']
        assert args == {'entity_name': 'Relation', 'allowed_axis_values': {axis: values}}
        for bad_subject in ('MODEL//ANECHOIC <+ Graph/Relation', subject + 'x'):
            with unittest.TestCase().assertRaises(ValueError):
                lower_typed_fields('manifest_property', text, bad_subject, {'Relation': 'Graph/Relation'})
        with unittest.TestCase().assertRaises(ValueError):
            lower_typed_fields('manifest_property', text, subject, {'Relation': 'Unrelated'})

def test_rejects_unimported_or_literal_address():
    for reference in ['Missing', 'Project', '"Node//Artifact//Atom"']:
        text = f'''from anechoic.model import Property, Atom
    class Tier(Property):
        bearer = {reference}
        value_format = int
    '''
        with unittest.TestCase().assertRaises(ValueError):
            lower_typed_fields('manifest_property', text, '', ADDRESSES)


def test_rejects_executable_class_body():
    with unittest.TestCase().assertRaises(ValueError):
        lower_typed_fields('manifest_property', 'from anechoic.model import Property\nclass X(Property):\n    print(1)\n', '', {})


if __name__ == "__main__":
    test_property_lowering_preserves_constraints_and_refs()
    test_relation_endpoint_pairs_preserve_disjoint_shapes()
    test_relation_forbidden_status_pairs_require_distinct_literal_pairs()
    test_cardinality_is_validated_by_native_parser()
    test_value_forms_and_existing_options()
    test_dotted_reference_requires_exact_alias_and_preserves_spaces()
    test_relation_classification_axes_match_existing_effect_and_scope()
    test_rejects_unimported_or_literal_address()
    test_rejects_executable_class_body()


def test_relation_endpoint_cardinalities():
    text = ('from anechoic.model import Relation\n'
            'from anechoic.formal_claims import Cardinality\n'
            'class LINK(Relation):\n'
            '    source_endpoint = {}\n    target_endpoint = {}\n'
            '    relation.sources_per_target = Cardinality(minimum=1, maximum=1)\n'
            '    relation.targets_per_source = Cardinality(minimum=0, maximum=2)\n')
    claim = lower_typed_fields('manifest_relation', text, '', {})
    args = parse_native_model_claim(claim)['arguments']
    assert args['sources_per_target'] == {'minimum': 1, 'maximum': 1}
    assert args['targets_per_source'] == {'minimum': 0, 'maximum': 2}
    with unittest.TestCase().assertRaises(ValueError):
        parse_native_model_claim(lower_typed_fields('manifest_relation', text.replace('minimum=0, maximum=2', 'minimum=3, maximum=2'), '', {}))
