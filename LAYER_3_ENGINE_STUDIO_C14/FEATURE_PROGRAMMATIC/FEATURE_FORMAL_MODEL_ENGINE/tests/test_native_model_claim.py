"""Native Model Claims are inspected as syntax and never executed."""

from pathlib import Path
import sys
import unittest


FEATURE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FEATURE))
from native_model_claim import NativeModelClaimError, parse_native_model_claim, validate_aspect_instance  # noqa: E402


class NativeModelClaimTests(unittest.TestCase):
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
        address = 'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Schema'
        call = f'declare_entity(entity_name="Schema", instance=Aspect(address={address!r}))'
        result = parse_native_model_claim(prefix + call)
        self.assertEqual({"type": "Aspect", "fields": {"address": address}},
                         result["arguments"]["instance"])
        self.assertEqual(address, validate_aspect_instance(result["arguments"]))
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

    def test_root_class_and_nested_dataclass_records(self):
        claim = '''
from dataclasses import dataclass
from anechoic.formal_claims import declare_entity

@dataclass(kw_only=True)
class AtomHeader:
    label: str | None = None

@dataclass(kw_only=True)
class Atom:
    header: AtomHeader

declare_entity(entity_class=Atom, entity_name="Atom")
'''
        result = parse_native_model_claim(claim)
        self.assertEqual((), result["classes"][0]["bases"])
        self.assertEqual((), result["classes"][1]["bases"])
        self.assertEqual("AtomHeader", result["classes"][1]["fields"][0]["annotation"])

    def test_relation_endpoint_flags_and_model_scopes(self):
        claim = '''
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="CARRIES",
    source_endpoint={"level": "model_entities", "classification_axis": True},
    target_endpoint={"level": "instances", "ephemeral": False},
)
'''
        result = parse_native_model_claim(claim)
        self.assertIs(result["arguments"]["source_endpoint"]["classification_axis"], True)
        self.assertIs(result["arguments"]["target_endpoint"]["ephemeral"], False)

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

    def test_unknown_names_and_duplicate_keyword_fail_with_line(self):
        source = ('from anechoic.formal_claims import declare_entity\n'
                  'declare_entity(entity_name="Name", value_format=Missing)\n')
        with self.assertRaisesRegex(NativeModelClaimError, "line 2.*unbound symbol: Missing"):
            parse_native_model_claim(source)
        source = ('from anechoic.formal_claims import declare_entity\n'
                  'declare_entity(entity_name="Name", entity_name="Name")\n')
        with self.assertRaisesRegex(NativeModelClaimError, "duplicate argument"):
            parse_native_model_claim(source)

    def test_invalid_cardinality_and_property_bearer_are_rejected(self):
        prefix = 'from anechoic.formal_claims import declare_entity\n'
        invalid = (
            'declare_entity(entity_name="Name", relation_name="IS_PROPERTY_OF")',
            'declare_entity(entity_name="Name", relation_name="IS_PROPERTY_OF", base_path=" ")',
            'declare_entity(entity_name="Name", value_cardinality=-1)',
            'declare_entity(entity_name="Name", value_cardinality=True)',
            'declare_entity(entity_name="Name", value_cardinality="1")',
            'declare_entity(entity_name="Name", '
            'instance_relation_constraints={"CONTAINS": {"targets_per_source": -1}})',
            'declare_entity(entity_name="Name", '
            'instance_property_constraints={"Name": {"value_cardinality": {"minimum": 2, "maximum": 1}}})',
        )
        for claim in invalid:
            with self.subTest(claim=claim), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(prefix + claim)

    def test_invalid_relation_endpoints_are_rejected(self):
        prefix = 'from anechoic.formal_claims import declare_relation\n'
        valid = '{"level": "instances"}'
        invalid = (
            'None',
            '{"level": None}',
            '{"level": "unknown"}',
            '{"level": "instances", "extra": "unexpected"}',
            '{"level": "instances", "entity_paths": "Atom"}',
            '{"level": "instances", "entity_paths": ("",)}',
            '{"level": "instances", "classification_axis": 1}',
            '{"level": "instances", "ephemeral": "false"}',
        )
        for endpoint in invalid:
            for side in ("source_endpoint", "target_endpoint"):
                other = "target_endpoint" if side == "source_endpoint" else "source_endpoint"
                claim = (f'declare_relation(relation_name="R", {side}={endpoint}, '
                         f'{other}={valid})')
                with self.subTest(side=side, endpoint=endpoint), self.assertRaises(NativeModelClaimError):
                    parse_native_model_claim(prefix + claim)

    def test_relation_endpoint_levels_default_independently(self):
        prefix = 'from anechoic.formal_claims import declare_relation\n'
        claim = ("declare_relation(relation_name='R', source_endpoint={'entity_paths': ('Node',)}, "
                 "target_endpoint={'level': 'instances'})")
        args = parse_native_model_claim(prefix + claim)["arguments"]
        self.assertEqual(args["source_endpoint"], {
            "entity_paths": ("Node",), "level": "model_entities_or_instances",
        })
        self.assertEqual(args["target_endpoint"]["level"], "instances")

        claim = ("declare_relation(relation_name='R', endpoint_pairs=("
                 "{'source_endpoint': {}, 'target_endpoint': {'level': 'model_entities'}},"
                 "{'source_endpoint': {'level': 'instances'}, 'target_endpoint': {}},))")
        pairs = parse_native_model_claim(prefix + claim)["arguments"]["endpoint_pairs"]
        self.assertEqual(pairs[0]["source_endpoint"]["level"], "model_entities_or_instances")
        self.assertEqual(pairs[0]["target_endpoint"]["level"], "model_entities")
        self.assertEqual(pairs[1]["source_endpoint"]["level"], "instances")
        self.assertEqual(pairs[1]["target_endpoint"]["level"], "model_entities_or_instances")

        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim(prefix + "declare_relation(relation_name='R', source_endpoint={})")


if __name__ == "__main__":
    unittest.main()
