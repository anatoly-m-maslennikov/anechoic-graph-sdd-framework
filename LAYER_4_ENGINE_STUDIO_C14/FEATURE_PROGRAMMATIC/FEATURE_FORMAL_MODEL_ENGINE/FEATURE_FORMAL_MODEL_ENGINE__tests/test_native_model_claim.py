"""Native Model Claims are inspected as syntax and never executed."""

from pathlib import Path
import sys
import unittest


FEATURE = Path(__file__).resolve().parents[1]
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import NativeModelClaimError, parse_native_model_claim, validate_aspect_instance  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (  # noqa: E402
    parse_component_manifest, parse_component_manifest_fields,
)


class NativeModelClaimTests(unittest.TestCase):
    def test_component_manifest_markdown_sections(self):
        formal = ('## Formal manifest\n\n```python\n'
                  'from anechoic.formal_claims import declare_entity\n'
                  'from anechoic.model import ComponentManifest\n'
                  'declare_entity(entity_name="Component Manifest", instance=ComponentManifest('
                  'tier=0, component_id="AN-C-14", name="Example", layer=3, lens_whitelist=None))\n```\n')
        body = '## Purpose\n\nText\n\n### Details\n\n- Item\n\n' + formal
        fields, purpose = parse_component_manifest(body)
        self.assertEqual('Text\n\n### Details\n\n- Item', purpose)
        self.assertEqual('AN-C-14', fields['component_id'])
        self.assertEqual(fields, parse_component_manifest_fields(body))
        short = formal.replace('from anechoic.formal_claims import declare_entity\n', '').replace(
            'declare_entity(entity_name="Component Manifest", instance=', '').replace('None))', 'None)')
        self.assertEqual(fields, parse_component_manifest_fields(short))
        self.assertIsNone(parse_component_manifest(formal)[1])
        self.assertIsNone(
            parse_component_manifest("## Purpose\n\n" + formal)[1]
        )
        legacy = (
            "## Claim\n\n### Component ID\n\nAN-C-14\n\n### Name\n\nExample\n"
        )
        self.assertEqual(
            ({"component_id": "AN-C-14", "name": "Example"}, None),
            parse_component_manifest(legacy),
        )
        invalid = (body + '\n## Purpose\nAgain\n', body + '\n' + formal,
                   formal + '\n## Claim\n', formal.replace('## Formal manifest', '### Formal manifest'),
                   formal.replace('```python', '```text'), formal + '\n```python\npass\n```\n',
                   formal.replace('name="Example"', 'name=load_name()'),
                   short.replace('from anechoic.model import ComponentManifest\n', ''),
                   short.replace('name="Example"', 'name=load_name()'))
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_component_manifest(value)

    def test_unknown_declaration_and_constraint_keys_fail_closed(self):
        prefix = "from anechoic.formal_claims import declare_entity, declare_relation\n"
        cases = (
            "declare_entity(entity_name='A', value_cardinailty=1)",
            "declare_relation(relation_name='R', source_endpoint={'level': 'instances'}, "
            "target_endpoint={'level': 'instances'}, target_per_source=1)",
            "declare_entity(entity_name='A', instance_relation_constraints={'R': {'target_entity_pathz': ('A',)}})",
            "declare_entity(entity_name='A', instance_property_constraints={'P': {'value_cardinailty': 1}})",
        )
        for case in cases:
            with self.subTest(case=case), self.assertRaisesRegex(NativeModelClaimError, 'unsupported'):
                parse_native_model_claim(prefix + case)

    def test_typed_instance_is_static_and_requires_trusted_symbols(self):
        prefix = ('from anechoic.formal_claims import declare_entity\n'
                  'from anechoic.model import ScopeUnit\n')
        call = ('declare_entity(entity_name="ENGINE", instance=ScopeUnit('
                'id="CA-SU-14", name="ENGINE", ordered=False, container="anechoic"))')
        result = parse_native_model_claim(prefix + call)
        self.assertEqual("ScopeUnit", result["arguments"]["instance"]["type"])
        self.assertEqual("CA-SU-14", result["arguments"]["instance"]["fields"]["id"])
        invalid = (
            call.replace('name="ENGINE", ordered', 'name="ENGINE", name="ENGINE", ordered'),
            call.replace('id="CA-SU-14"', 'id=open("file")'),
            call + '\nprint("side effect")',
            call.replace('instance=ScopeUnit', 'instance=Untrusted'),
        )
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(prefix + item)
        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim('from anechoic.formal_claims import declare_entity\n' + call)

    def test_aspect_instance_requires_full_matching_structure_address(self):
        prefix = ('from anechoic.formal_claims import declare_entity\n'
                  'from anechoic.model import Aspect\n')
        address = (
            "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Schema"
        )
        call = f'declare_entity(entity_name="Schema", instance=Aspect(address={address!r}))'
        result = parse_native_model_claim(prefix + call)
        self.assertEqual({"type": "Aspect", "fields": {"address": address}},
                         result["arguments"]["instance"])
        self.assertEqual(
            address, validate_aspect_instance(result["arguments"])
        )
        spaced = call.replace(address, 'PROJECT STRUCTURE // ANECHOIC  <+  Aspects <+ Engineering <+ Schema')
        self.assertEqual(address, validate_aspect_instance(parse_native_model_claim(prefix + spaced)["arguments"]))
        invalid = (
            call.replace('entity_name="Schema"', 'entity_name="Other"'),
            call.replace(address, 'Engineering <+ Schema'),
            call.replace(address, 'ANECHOIC_MODEL <+ Aspects <+ Schema'),
            call.replace(address, 'ANECHOIC_STRUCTURE <+ Aspects <+ Schema'),
            call.replace('entity_name="Schema",', 'entity_name="Schema", value_cardinality=1,'),
            call.replace(address, 'PROJECT STRUCTURE//ANECHOIC <+ Engineering <+ Schema'),
            call.replace(address, 'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Schema/X'),
            call.replace('Aspect(address=', 'Aspect(name="Schema", address='),
            call.replace('address=', 'address=read(').replace('))', ')))'),
        )
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(prefix + item)
        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim('from anechoic.formal_claims import declare_entity\n' + call)

    def test_project_manifest_parameters_are_literal_mapping_only(self):
        imports = ('from anechoic.formal_claims import declare_entity\n'
                   'from anechoic.model import ProjectManifest, Project\n')
        claim = ('declare_entity(entity_name="Project Manifest", instance=ProjectManifest('
                 'name="Anechoic", prefix="AN", parameters={"options": {"verbose": False}}))')
        parsed = parse_native_model_claim(imports + claim)
        self.assertEqual({"name": "Anechoic", "prefix": "AN", "parameters": {"options": {"verbose": False}}},
                         parsed["arguments"]["instance"]["fields"])
        for invalid in (claim.replace('False', 'read()'), claim.replace('False', 'str'),
                        claim.replace('"verbose": False', '"verbose": False, "verbose": True'),
                        claim.replace('instance=ProjectManifest', 'instance=Project')):
            with self.subTest(claim=invalid), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(imports + invalid)

    def test_project_manifest_lens_whitelist_accepts_literal_lists(self):
        imports = ('from anechoic.formal_claims import declare_entity\n'
                   'from anechoic.model import ProjectManifest, Project\n')
        claim = ('declare_entity(entity_name="Project Manifest", instance=ProjectManifest('
                 'name="Anechoic", prefix="AN", lens_whitelist={value}))')
        for value in (None, [], ["SPEC", "DES"]):
            with self.subTest(value=value):
                result = parse_native_model_claim(imports + claim.format(value=repr(value)))
                self.assertEqual(value, result["arguments"]["instance"]["fields"]["lens_whitelist"])
        for value in ('load_lenses()', '["SPEC", str]', '[""]', '[" SPEC"]', '[17]', '("SPEC",)', '"SPEC"'):
            with self.subTest(value=value), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(imports + claim.format(value=value))
        with self.assertRaisesRegex(NativeModelClaimError, "scalar literals"):
            parse_native_model_claim(imports + claim.replace('instance=ProjectManifest', 'instance=Project')
                                     .format(value='["SPEC"]'))

    def test_component_manifest_is_literal_only(self):
        imports = ('from anechoic.formal_claims import declare_entity\n'
                   'from anechoic.model import ComponentManifest\n')
        claim = ('declare_entity(entity_name="Component Manifest", instance=ComponentManifest('
                 'tier=0, component_id="AN-C-14", name="Example", layer=3, lens_whitelist={value}))')
        for value in (None, [], ["SPEC", "DES"]):
            with self.subTest(value=value):
                instance = parse_native_model_claim(imports + claim.format(value=repr(value)))["arguments"]["instance"]
                self.assertEqual({"type": "ComponentManifest", "fields": {
                    "tier": 0, "component_id": "AN-C-14", "name": "Example", "layer": 3,
                    "lens_whitelist": value,
                }}, instance)
        for value in ('load_lenses()', '["SPEC", str]', '[""]', '[" SPEC"]', '[17]', '("SPEC",)'):
            with self.subTest(value=value), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(imports + claim.format(value=value))
        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim(imports + claim.format(value='None').replace('name="Example"', 'name=load_name()'))
        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim(imports.splitlines()[0] + '\n' + claim.format(value='None'))

    def test_named_instance_check_is_preserved_without_execution(self):
        claim = '''
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

def check_scope_unit(unit: ScopeUnit) -> bool:
    raise RuntimeError("must not run while reading")

declare_entity(entity_name="Scope Unit", instance_check=check_scope_unit)
'''
        result = parse_native_model_claim(claim)
        check = result["instance_check"]
        self.assertEqual(result["arguments"]["instance_check"], "check_scope_unit")
        self.assertEqual((check["name"], check["parameter"], check["parameter_type"]),
                         ("check_scope_unit", "unit", "ScopeUnit"))
        self.assertIn('raise RuntimeError("must not run while reading")', check["source"])
        self.assertNotIn("anechoic.model", sys.modules)

    def test_invalid_instance_checks_are_rejected(self):
        prefix = ("from anechoic.formal_claims import declare_entity\n"
                  "from anechoic.model import ScopeUnit\n")
        cases = (
            'def check(unit: ScopeUnit) -> bool:\n    return True\n'
            'declare_entity(entity_name="Scope Unit", instance_check="check")',
            'def check(unit: ScopeUnit) -> bool:\n    return True\n'
            'declare_entity(entity_name="Scope Unit", instance_check=ScopeUnit)',
            'def check(unit: ScopeUnit) -> str:\n    return "yes"\n'
            'declare_entity(entity_name="Scope Unit", instance_check=check)',
            'def check(unit: str) -> bool:\n    return True\n'
            'declare_entity(entity_name="Scope Unit", instance_check=check)',
            'def check(unit: ScopeUnit, other: ScopeUnit) -> bool:\n    return True\n'
            'declare_entity(entity_name="Scope Unit", instance_check=check)',
            'def check(unit: ScopeUnit = None) -> bool:\n    return True\n'
            'declare_entity(entity_name="Scope Unit", instance_check=check)',
            'def check(unit: ScopeUnit) -> bool:\n    return True\n'
            'declare_entity(entity_name="Scope Unit")',
        )
        for case in cases:
            with self.subTest(case=case), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(prefix + case)

    def test_nested_cardinality_and_dataclass_fields_are_preserved(self):
        claim = '''
from dataclasses import dataclass, field
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Atom

@dataclass(kw_only=True)
class Method(Atom):
    label: str | None = None
    tags: list[str] = field(default_factory=list)

declare_entity(
    entity_class=Method,
    entity_name="Method",
    value_cardinality=Cardinality(minimum=0, maximum=1),
    instance_relation_constraints={"HAS_PROPERTY": {"targets_per_source": 1}},
)
'''
        result = parse_native_model_claim(claim)
        self.assertEqual({"minimum": 0, "maximum": 1}, result["arguments"]["value_cardinality"])
        self.assertEqual({"HAS_PROPERTY": {"targets_per_source": 1}},
                         result["arguments"]["instance_relation_constraints"])
        self.assertEqual(("Atom",), result["classes"][0]["bases"])
        self.assertEqual("str | None", result["classes"][0]["fields"][0]["annotation"])
        self.assertEqual({"default_factory": "list"}, result["classes"][0]["fields"][1]["field"])
        self.assertEqual({"kw_only": True}, result["classes"][0]["dataclass"])

    def test_relation_endpoint_flags_and_model_scopes(self):
        claim = '''
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="CARRIES",
    source_endpoint={"level": "model_entities", "axis": True},
    target_endpoint={"level": "instances", "ephemeral": False},
)
'''
        result = parse_native_model_claim(claim)
        self.assertIs(result["arguments"]["source_endpoint"]["axis"], True)
        self.assertIs(result["arguments"]["target_endpoint"]["ephemeral"], False)
        legacy = claim.replace('"axis": True', '"classification_axis": True')
        self.assertEqual(result["arguments"], parse_native_model_claim(legacy)["arguments"])
        duplicate = claim.replace('"axis": True', '"axis": True, "classification_axis": True')
        with self.assertRaisesRegex(NativeModelClaimError, "duplicate axis"):
            parse_native_model_claim(duplicate)

    def test_relation_axes_require_trimmed_nonempty_mappings(self):
        prefix = ('from anechoic.formal_claims import declare_relation\n'
                  'declare_relation(relation_name="R", source_endpoint={}, target_endpoint={}')
        metadata = ', inverse_alias="R_INVERSE", axes={"Axis": "Value"}, inverse_axes={"Axis": "Other"}'
        arguments = parse_native_model_claim(prefix + metadata + ')')["arguments"]
        self.assertEqual({"Axis": "Value"}, arguments["axes"])
        self.assertEqual({"Axis": "Other"}, arguments["inverse_axes"])
        self.assertNotIn("axes", parse_native_model_claim(prefix + ')')["arguments"])
        legacy = metadata.replace('inverse_axes', 'inverse_classifications').replace(' axes=', ' classifications=')
        self.assertEqual(arguments, parse_native_model_claim(prefix + legacy + ')')["arguments"])
        with self.assertRaisesRegex(NativeModelClaimError, "duplicate axes"):
            parse_native_model_claim(prefix + metadata + ', classifications={"Axis": "Value"})')
        for field in ("axes", "inverse_axes"):
            for value in ('{}', '[]', '{"": "Value"}', '{" Axis": "Value"}',
                          '{"Axis": ""}', '{"Axis": " Value"}', '{"Axis": 1}'):
                claim = prefix + f', inverse_alias="R_INVERSE", {field}={value})'
                with self.subTest(field=field, value=value), self.assertRaises(NativeModelClaimError):
                    parse_native_model_claim(claim)
        with self.assertRaisesRegex(NativeModelClaimError, "requires inverse_alias"):
            parse_native_model_claim(prefix + ', inverse_axes={"Axis": "Value"})')

    def test_legacy_claim_is_identified_for_existing_reader(self):
        self.assertIsNone(parse_native_model_claim('property_rule(address="Atom.Name", values="1")'))

    def test_invalid_and_executable_forms_are_rejected(self):
        claims = (
            'from anechoic.formal_claims import declare_entity\n'
            'declare_entity(entity_name="Name", base_path=__import__("os").getcwd())',
            'from anechoic.formal_claims import declare_entity\n'
            'declare_entity(entity_name="A")\nopen("/tmp/pwned", "w")',
            'from anechoic.formal_claims import declare_entity\n'
            'if True:\n    declare_entity(entity_name="A")',
            'from anechoic.formal_claims import declare_entity\n'
            'declare_entity(entity_name="A")\ndeclare_entity(entity_name="B")',
            'from anechoic.formal_claims import Cardinality, declare_entity\n'
            'declare_entity(entity_name="A", value_cardinality=Cardinality(minimum=2, maximum=1))',
            'from anechoic.formal_claims import declare_entity\n'
            'class Bad(object):\n    x = open("/tmp/pwned", "w")\n'
            'declare_entity(entity_name="Bad", entity_class=Bad)',
        )
        for claim in claims:
            with self.subTest(claim=claim):
                with self.assertRaises(NativeModelClaimError):
                    parse_native_model_claim(claim)

    def test_class_cannot_replace_annotations_or_declare_type_parameters(self):
        for declaration, message in (
            ('class Item:\n    __annotations__: ClassVar[object] = {"payload": "int"}', "special attributes"),
            ("class Item[int: str]:\n    payload: int", "type parameters"),
        ):
            claim = ('from anechoic.formal_claims import declare_entity\n'
                     'from typing import ClassVar\n'
                     + declaration + '\ndeclare_entity(entity_name="Item", entity_class=Item)')
            with self.subTest(declaration=declaration), self.assertRaisesRegex(NativeModelClaimError, message):
                parse_native_model_claim(claim)

    def test_property_manifest_formats_and_options_are_static(self):
        claim = (
            'from anechoic.formal_claims import declare_entity\n'
            'declare_entity(entity_name="Boundaries", entity_kind="Property", '
            'relation_name="IS_PROPERTY_OF", base_path="Component Manifest", '
            'value_format=dict[str, object] | None, field_options={"default": None})'
        )
        arguments = parse_native_model_claim(claim)["arguments"]
        self.assertEqual(arguments["value_format"], "dict[str, object] | None")
        self.assertEqual(arguments["field_options"], {"default": None})
        for expression in ('"dict[str, object]"', 'object.attribute', 'str()'):
            with self.subTest(expression=expression), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(claim.replace("dict[str, object] | None", expression))
        with self.assertRaisesRegex(NativeModelClaimError, "unsupported Property field options"):
            parse_native_model_claim(claim.replace('{"default": None}', '{"default_factory": "unknown"}'))



if __name__ == "__main__":
    unittest.main()
