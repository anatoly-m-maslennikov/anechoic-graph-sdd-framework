"""Native Model Claims are inspected as syntax and never executed."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (  # noqa: E402
    NativeModelClaimError,
    parse_native_model_claim,
    validate_aspect_instance,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.components.components__shared import (  # noqa: E402
    parse_component_manifest,
    parse_component_manifest_fields,
)


class NativeManifestClaimCases:
    def test_component_manifest_markdown_sections(self):
        formal = (
            "## Formal manifest\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ComponentManifest\n"
            'declare_entity(entity_name="Component Manifest", instance=ComponentManifest('
            'tier=0, component_id="AN-C-14", name="Example", layer=3, lens_whitelist=None))\n```\n'
        )
        body = "## Purpose\n\nText\n\n### Details\n\n- Item\n\n" + formal
        fields, purpose = parse_component_manifest(body)
        self.assertEqual("Text\n\n### Details\n\n- Item", purpose)
        self.assertEqual("AN-C-14", fields["component_id"])
        self.assertEqual(fields, parse_component_manifest_fields(body))
        short = (
            formal.replace(
                "from anechoic.formal_claims import declare_entity\n", ""
            )
            .replace(
                'declare_entity(entity_name="Component Manifest", instance=',
                "",
            )
            .replace("None))", "None)")
        )
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
        self._reject_invalid_component_sections(body, formal, short)

    def _reject_invalid_component_sections(self, body, formal, short):
        invalid = (
            body + "\n## Purpose\nAgain\n",
            body + "\n" + formal,
            formal + "\n## Claim\n",
            formal.replace("## Formal manifest", "### Formal manifest"),
            formal.replace("```python", "```text"),
            formal + "\n```python\npass\n```\n",
            formal.replace('name="Example"', "name=load_name()"),
            short.replace(
                "from anechoic.model import ComponentManifest\n", ""
            ),
            short.replace('name="Example"', "name=load_name()"),
        )
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_component_manifest(value)

    def test_aspect_instance_requires_full_matching_structure_address(self):
        prefix = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import Aspect\n"
        )
        address = (
            "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Schema"
        )
        call = (
            'declare_entity(entity_name="Schema", instance=Aspect(address='
            f"{address!r}"
            "))"
        )
        result = parse_native_model_claim(prefix + call)
        self.assertEqual(
            {"type": "Aspect", "fields": {"address": address}},
            result["arguments"]["instance"],
        )
        self.assertEqual(
            address, validate_aspect_instance(result["arguments"])
        )
        spaced = call.replace(
            address,
            (
                "PROJECT STRUCTURE // ANECHOIC  <+  Aspects <+ Engineering "
                "<+ Schema"
            ),
        )
        self.assertEqual(
            address,
            validate_aspect_instance(
                parse_native_model_claim(prefix + spaced)["arguments"]
            ),
        )
        self._reject_invalid_aspect_addresses(prefix, address, call)

    def _reject_invalid_aspect_addresses(self, prefix, address, call):
        invalid = (
            call.replace('entity_name="Schema"', 'entity_name="Other"'),
            call.replace(address, "Engineering <+ Schema"),
            call.replace(address, "ANECHOIC_MODEL <+ Aspects <+ Schema"),
            call.replace(address, "ANECHOIC_STRUCTURE <+ Aspects <+ Schema"),
            call.replace(
                'entity_name="Schema",',
                'entity_name="Schema", value_cardinality=1,',
            ),
            call.replace(
                address, "PROJECT STRUCTURE//ANECHOIC <+ Engineering <+ Schema"
            ),
            call.replace(
                address, "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Schema/X"
            ),
            call.replace("Aspect(address=", 'Aspect(name="Schema", address='),
            call.replace("address=", "address=read(").replace("))", ")))"),
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

    def test_project_manifest_parameters_are_literal_mapping_only(self):
        imports = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest, Project\n"
        )
        claim = (
            'declare_entity(entity_name="Project Manifest", instance=ProjectManifest('
            'name="Anechoic", prefix="AN", parameters={"options": {"verbose": False}}))'
        )
        parsed = parse_native_model_claim(imports + claim)
        self.assertEqual(
            {
                "name": "Anechoic",
                "prefix": "AN",
                "parameters": {"options": {"verbose": False}},
            },
            parsed["arguments"]["instance"]["fields"],
        )
        for invalid in (
            claim.replace("False", "read()"),
            claim.replace("False", "str"),
            claim.replace(
                '"verbose": False', '"verbose": False, "verbose": True'
            ),
            claim.replace("instance=ProjectManifest", "instance=Project"),
        ):
            with (
                self.subTest(claim=invalid),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(imports + invalid)

    def test_project_manifest_lens_whitelist_accepts_literal_lists(self):
        imports = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest, Project\n"
        )
        claim = (
            'declare_entity(entity_name="Project Manifest", instance=ProjectManifest('
            'name="Anechoic", prefix="AN", lens_whitelist={value}))'
        )
        for value in (None, [], ["SPEC", "DES"]):
            with self.subTest(value=value):
                result = parse_native_model_claim(
                    imports + claim.format(value=repr(value))
                )
                self.assertEqual(
                    value,
                    result["arguments"]["instance"]["fields"][
                        "lens_whitelist"
                    ],
                )
        for value in (
            "load_lenses()",
            '["SPEC", str]',
            '[""]',
            '[" SPEC"]',
            "[17]",
            '("SPEC",)',
            '"SPEC"',
        ):
            with (
                self.subTest(value=value),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(imports + claim.format(value=value))
        with self.assertRaisesRegex(NativeModelClaimError, "scalar literals"):
            parse_native_model_claim(
                imports
                + claim.replace(
                    "instance=ProjectManifest", "instance=Project"
                ).format(value='["SPEC"]')
            )

    def test_component_manifest_is_literal_only(self):
        imports = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ComponentManifest\n"
        )
        claim = (
            'declare_entity(entity_name="Component Manifest", instance=ComponentManifest('
            'tier=0, component_id="AN-C-14", name="Example", layer=3, lens_whitelist={value}))'
        )
        for value in (None, [], ["SPEC", "DES"]):
            with self.subTest(value=value):
                instance = parse_native_model_claim(
                    imports + claim.format(value=repr(value))
                )["arguments"]["instance"]
                self.assertEqual(
                    {
                        "type": "ComponentManifest",
                        "fields": {
                            "tier": 0,
                            "component_id": "AN-C-14",
                            "name": "Example",
                            "layer": 3,
                            "lens_whitelist": value,
                        },
                    },
                    instance,
                )
        self._reject_nonliteral_component_fields(imports, claim)

    def _reject_nonliteral_component_fields(self, imports, claim):
        for value in (
            "load_lenses()",
            '["SPEC", str]',
            '[""]',
            '[" SPEC"]',
            "[17]",
            '("SPEC",)',
        ):
            with (
                self.subTest(value=value),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(imports + claim.format(value=value))
        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim(
                imports
                + claim.format(value="None").replace(
                    'name="Example"', "name=load_name()"
                )
            )
        with self.assertRaises(NativeModelClaimError):
            parse_native_model_claim(
                imports.splitlines()[0] + "\n" + claim.format(value="None")
            )

    def test_property_manifest_formats_and_options_are_static(self):
        claim = (
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="Boundaries", entity_kind="Property", '
            'relation_name="IS_PROPERTY_OF", base_path="Component Manifest", '
            'value_format=dict[str, object] | None, field_options={"default": None})'
        )
        arguments = parse_native_model_claim(claim)["arguments"]
        self.assertEqual(arguments["value_format"], "dict[str, object] | None")
        self.assertEqual(arguments["field_options"], {"default": None})
        for expression in ('"dict[str, object]"', "object.attribute", "str()"):
            with (
                self.subTest(expression=expression),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(
                    claim.replace("dict[str, object] | None", expression)
                )
        with self.assertRaisesRegex(
            NativeModelClaimError, "unsupported Property field options"
        ):
            parse_native_model_claim(
                claim.replace(
                    '{"default": None}', '{"default_factory": "unknown"}'
                )
            )
