"""Native Model Claims are inspected as syntax and never executed."""

import sys
import unittest

from ._native_manifest_claim_cases import NativeManifestClaimCases


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (  # noqa: E402
    NativeModelClaimError,
    parse_native_model_claim,
)


class NativeModelClaimTests(NativeManifestClaimCases, unittest.TestCase):
    def test_unknown_declaration_and_constraint_keys_fail_closed(self):
        prefix = (
            "from anechoic.formal_claims import declare_entity, "
            "declare_relation\n"
        )
        cases = (
            "declare_entity(entity_name='A', value_cardinailty=1)",
            "declare_relation(relation_name='R', source_endpoint={'level': 'instances'}, "
            "target_endpoint={'level': 'instances'}, target_per_source=1)",
            (
                "declare_entity(entity_name='A', "
                "instance_relation_constraints={'R': {'target_entity_pathz': "
                "('A',)}})"
            ),
            (
                "declare_entity(entity_name='A', "
                "instance_property_constraints={'P': {'value_cardinailty': "
                "1}})"
            ),
        )
        for case in cases:
            with (
                self.subTest(case=case),
                self.assertRaisesRegex(NativeModelClaimError, "unsupported"),
            ):
                parse_native_model_claim(prefix + case)

    def test_typed_instance_is_static_and_requires_trusted_symbols(self):
        prefix = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ScopeUnit\n"
        )
        call = (
            'declare_entity(entity_name="ENGINE", instance=ScopeUnit('
            'id="CA-SU-14", name="ENGINE", ordered=False, container="anechoic"))'
        )
        result = parse_native_model_claim(prefix + call)
        self.assertEqual("ScopeUnit", result["arguments"]["instance"]["type"])
        self.assertEqual(
            "CA-SU-14", result["arguments"]["instance"]["fields"]["id"]
        )
        invalid = (
            call.replace(
                'name="ENGINE", ordered',
                'name="ENGINE", name="ENGINE", ordered',
            ),
            call.replace('id="CA-SU-14"', 'id=open("file")'),
            call + '\nprint("side effect")',
            call.replace("instance=ScopeUnit", "instance=Untrusted"),
        )
        for item in invalid:
            with (
                self.subTest(item=item),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(prefix + item)
        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim(
                "from anechoic.formal_claims import declare_entity\n" + call
            )

    def test_named_instance_check_is_preserved_without_execution(self):
        claim = """
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

def check_scope_unit(unit: ScopeUnit) -> bool:
    raise RuntimeError("must not run while reading")

declare_entity(entity_name="Scope Unit", instance_check=check_scope_unit)
"""
        result = parse_native_model_claim(claim)
        check = result["instance_check"]
        self.assertEqual(
            result["arguments"]["instance_check"], "check_scope_unit"
        )
        self.assertEqual(
            (check["name"], check["parameter"], check["parameter_type"]),
            ("check_scope_unit", "unit", "ScopeUnit"),
        )
        self.assertIn(
            'raise RuntimeError("must not run while reading")', check["source"]
        )
        self.assertNotIn("anechoic.model", sys.modules)

    def test_invalid_instance_checks_are_rejected(self):
        prefix = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ScopeUnit\n"
        )
        cases = (
            "def check(unit: ScopeUnit) -> bool:\n    return True\n"
            'declare_entity(entity_name="Scope Unit", instance_check="check")',
            "def check(unit: ScopeUnit) -> bool:\n    return True\n"
            'declare_entity(entity_name="Scope Unit", instance_check=ScopeUnit)',
            'def check(unit: ScopeUnit) -> str:\n    return "yes"\n'
            'declare_entity(entity_name="Scope Unit", instance_check=check)',
            "def check(unit: str) -> bool:\n    return True\n"
            'declare_entity(entity_name="Scope Unit", instance_check=check)',
            "def check(unit: ScopeUnit, other: ScopeUnit) -> bool:\n    return True\n"
            'declare_entity(entity_name="Scope Unit", instance_check=check)',
            "def check(unit: ScopeUnit = None) -> bool:\n    return True\n"
            'declare_entity(entity_name="Scope Unit", instance_check=check)',
            "def check(unit: ScopeUnit) -> bool:\n    return True\n"
            'declare_entity(entity_name="Scope Unit")',
        )
        for case in cases:
            with (
                self.subTest(case=case),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(prefix + case)

    def test_nested_cardinality_and_dataclass_fields_are_preserved(self):
        claim = """
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
"""
        result = parse_native_model_claim(claim)
        self.assertEqual(
            {"minimum": 0, "maximum": 1},
            result["arguments"]["value_cardinality"],
        )
        self.assertEqual(
            {"HAS_PROPERTY": {"targets_per_source": 1}},
            result["arguments"]["instance_relation_constraints"],
        )
        self.assertEqual(("Atom",), result["classes"][0]["bases"])
        self.assertEqual(
            "str | None", result["classes"][0]["fields"][0]["annotation"]
        )
        self.assertEqual(
            {"default_factory": "list"},
            result["classes"][0]["fields"][1]["field"],
        )
        self.assertEqual({"kw_only": True}, result["classes"][0]["dataclass"])

    def test_relation_endpoint_flags_and_model_scopes(self):
        claim = """
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="CARRIES",
    source_endpoint={"level": "model_entities", "axis": True},
    target_endpoint={"level": "instances", "ephemeral": False},
)
"""
        result = parse_native_model_claim(claim)
        self.assertIs(result["arguments"]["source_endpoint"]["axis"], True)
        self.assertIs(
            result["arguments"]["target_endpoint"]["ephemeral"], False
        )
        legacy = claim.replace('"axis": True', '"classification_axis": True')
        self.assertEqual(
            result["arguments"], parse_native_model_claim(legacy)["arguments"]
        )
        duplicate = claim.replace(
            '"axis": True', '"axis": True, "classification_axis": True'
        )
        with self.assertRaisesRegex(NativeModelClaimError, "duplicate axis"):
            parse_native_model_claim(duplicate)

    def test_relation_axes_require_trimmed_nonempty_mappings(self):
        prefix = (
            "from anechoic.formal_claims import declare_relation\n"
            'declare_relation(relation_name="R", source_endpoint={}, target_endpoint={}'
        )
        metadata = (
            ', inverse_alias="R_INVERSE", axes={"Axis": "Value"}, '
            'inverse_axes={"Axis": "Other"}'
        )
        arguments = parse_native_model_claim(prefix + metadata + ")")[
            "arguments"
        ]
        self.assertEqual({"Axis": "Value"}, arguments["axes"])
        self.assertEqual({"Axis": "Other"}, arguments["inverse_axes"])
        self.assertNotIn(
            "axes", parse_native_model_claim(prefix + ")")["arguments"]
        )
        legacy = metadata.replace(
            "inverse_axes", "inverse_classifications"
        ).replace(" axes=", " classifications=")
        self.assertEqual(
            arguments,
            parse_native_model_claim(prefix + legacy + ")")["arguments"],
        )
        with self.assertRaisesRegex(NativeModelClaimError, "duplicate axes"):
            parse_native_model_claim(
                prefix + metadata + ', classifications={"Axis": "Value"})'
            )
        self._reject_invalid_relation_axes(prefix)

    def _reject_invalid_relation_axes(self, prefix):
        for field in ("axes", "inverse_axes"):
            for value in (
                "{}",
                "[]",
                '{"": "Value"}',
                '{" Axis": "Value"}',
                '{"Axis": ""}',
                '{"Axis": " Value"}',
                '{"Axis": 1}',
            ):
                claim = (
                    prefix + f', inverse_alias="R_INVERSE", {field}={value})'
                )
                with (
                    self.subTest(field=field, value=value),
                    self.assertRaises(NativeModelClaimError),
                ):
                    parse_native_model_claim(claim)
        with self.assertRaisesRegex(
            NativeModelClaimError, "requires inverse_alias"
        ):
            parse_native_model_claim(
                prefix + ', inverse_axes={"Axis": "Value"})'
            )

    def test_legacy_claim_is_identified_for_existing_reader(self):
        self.assertIsNone(
            parse_native_model_claim(
                'property_rule(address="Atom.Name", values="1")'
            )
        )

    def test_invalid_and_executable_forms_are_rejected(self):
        claims = (
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="Name", base_path=__import__("os").getcwd())',
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="A")\nopen("/tmp/pwned", "w")',
            "from anechoic.formal_claims import declare_entity\n"
            'if True:\n    declare_entity(entity_name="A")',
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="A")\ndeclare_entity(entity_name="B")',
            "from anechoic.formal_claims import Cardinality, declare_entity\n"
            'declare_entity(entity_name="A", value_cardinality=Cardinality(minimum=2, maximum=1))',
            "from anechoic.formal_claims import declare_entity\n"
            'class Bad(object):\n    x = open("/tmp/pwned", "w")\n'
            'declare_entity(entity_name="Bad", entity_class=Bad)',
        )
        for claim in claims:
            with self.subTest(claim=claim):
                with self.assertRaises(NativeModelClaimError):
                    parse_native_model_claim(claim)

    def test_class_cannot_replace_annotations_or_declare_type_parameters(self):
        for declaration, message in (
            (
                (
                    "class Item:\n    __annotations__: ClassVar[object] = "
                    '{"payload": "int"}'
                ),
                "special attributes",
            ),
            ("class Item[int: str]:\n    payload: int", "type parameters"),
        ):
            claim = (
                "from anechoic.formal_claims import declare_entity\n"
                "from typing import ClassVar\n"
                + declaration
                + '\ndeclare_entity(entity_name="Item", entity_class=Item)'
            )
            with (
                self.subTest(declaration=declaration),
                self.assertRaisesRegex(NativeModelClaimError, message),
            ):
                parse_native_model_claim(claim)


if __name__ == "__main__":
    unittest.main()
