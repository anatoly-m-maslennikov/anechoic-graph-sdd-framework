"""Shared property declarations and inheritance test cases."""

from dataclasses import asdict
import sys
from types import ModuleType
from unittest.mock import patch

_shared = __import__(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared",
    fromlist=["assemble_model_classes", "assemble_model_modules"],
)
assemble_model_classes = _shared.assemble_model_classes
assemble_model_modules = _shared.assemble_model_modules


def primary(name, base=None, entity_name=None, extra=""):
    imports = f"from anechoic.model import {base}\n" if base else ""
    return (
        "from anechoic.formal_claims import declare_entity\n"
        + imports
        + f"class {name}{f'({base})' if base else ''}:\n    pass\n"
        + f"declare_entity(entity_name={entity_name or name!r}, "
        + f"entity_class={name}, entity_kind='Primary'{extra})\n"
    )


def prop(name, base, extra=""):
    return (
        "from anechoic.formal_claims import declare_entity\nfrom "
        "datetime import datetime\n"
        + f"declare_entity(entity_name={name!r}, entity_kind='Property', "
        + "relation_name='IS_PROPERTY_OF', "
        + f"base_path={base!r}{extra})\n"
    )


class PropertyInheritanceCases:
    def test_header_paths_and_inherited_group(self):
        atom = "Node//Artifact//Atom"
        spec = atom + "//SpecAtom"
        claims = self._header_claims(atom, spec)
        qualified = "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
        qualified_claims = [claim.replace(atom, qualified) for claim in claims]
        self.assertEqual(
            assemble_model_classes(claims),
            assemble_model_classes(qualified_claims),
        )
        self._check_header_instances(claims)
        self._check_header_rejections(claims, atom, spec)

    def _header_claims(self, atom, spec):
        return [
            primary("Node"),
            primary("Artifact", "Node"),
            primary(
                "Atom",
                "Artifact",
                extra=", identity_properties=('Header.Atom ID',)",
            ),
            primary("SpecAtom", "Atom"),
            prop(
                "Header",
                atom,
                ", value_cardinality=0, "
                "allowed_dependent_property_names=('Atom Family', 'Atom "
                "ID', 'State', 'Structure')",
            ),
            prop(
                "Atom Family",
                atom + ".Header",
                ", value_format=str, allowed_values=('SPEC', 'TKT', "
                "'PROJECT_CONFIG')",
            ),
            prop("Atom ID", atom + ".Header", ", value_format=str"),
        ] + self._header_claims_tail(atom, spec)

    def _header_claims_tail(self, atom, spec):
        return [
            prop(
                "State",
                atom + ".Header",
                ", value_cardinality=0, "
                "allowed_dependent_property_names=('Version', 'Status', "
                "'Updated At')",
            ),
            prop("Version", atom + ".Header.State", ", value_format=int"),
            prop("Status", atom + ".Header.State", ", value_format=str"),
            prop(
                "Updated At", atom + ".Header.State", ", value_format=datetime"
            ),
            prop(
                "Structure",
                atom + ".Header",
                ", value_cardinality=0, "
                "allowed_dependent_property_names=('Tier',)",
            ),
            prop("Tier", spec + ".Header.Structure", ", value_format=int"),
            prop(
                "Ref ID",
                atom,
                ", value_format=str, derived_from_properties=('Header.Atom "
                "ID', 'Header.State.Version', 'Header.State.Status')",
            ),
        ]

    def _check_header_instances(self, claims):
        namespace = {}
        exec(assemble_model_classes(claims), namespace)
        from datetime import datetime

        values = dict(
            atom_id="AN-S-1",
            version=2,
            status="draft",
            updated_at=datetime.now(),
            tier=3,
        )
        instance = namespace["SpecAtom"](atom_family="SPEC", **values)
        self.assertEqual(instance.ref_id, "AN-S-1@2-draft")
        self.assertNotIn("ref_id", asdict(instance))
        for atom_id in ("AN-C-1", "AN-P-1"):
            namespace["SpecAtom"](
                atom_family="PROJECT_CONFIG", **(values | {"atom_id": atom_id})
            )
        with self.assertRaisesRegex(ValueError, "Atom Family disagrees"):
            namespace["SpecAtom"](
                atom_family="PMETA", **(values | {"atom_id": "AN-P-1"})
            )
        with self.assertRaisesRegex(ValueError, "Atom Family disagrees"):
            namespace["SpecAtom"](atom_family="TKT", **values)

    def _check_header_rejections(self, claims, atom, spec):
        with self.assertRaisesRegex(
            ValueError, "Unresolved Property group bearer"
        ):
            assemble_model_classes(
                [
                    claim.replace(
                        spec + ".Header.Structure", spec + ".Header.Missing"
                    )
                    for claim in claims
                ]
            )
        with self.assertRaisesRegex(
            ValueError, "Duplicate inherited Property field"
        ):
            assemble_model_classes(
                claims
                + [
                    prop(
                        "Version",
                        spec + ".Header.Structure",
                        ", value_format=int",
                    )
                ]
            )
        with self.assertRaisesRegex(
            ValueError, "Unresolved Property group bearer"
        ):
            assemble_model_classes(
                [
                    claim.replace(atom + ".Header.State", atom + ".State")
                    if "entity_name='Version'" in claim
                    else claim
                    for claim in claims
                ]
            )

    def test_override_replaces_default_options(self):
        claims = [
            primary("Base"),
            primary("Child", "Base"),
            prop(
                "Name",
                "Base",
                ", value_format=str, field_options={'default': 'x', "
                "'kw_only': True}",
            ),
            prop(
                "Name",
                "Base",
                ", applies_to_entity_classes=('Base//Child',), "
                "field_options={}",
            ),
        ]
        namespace = {}
        exec(assemble_model_classes(claims), namespace)
        field = namespace["Child"].__dataclass_fields__["name"]
        self.assertFalse(field.kw_only)
        self.assertIs(field.default, __import__("dataclasses").MISSING)

    def test_descendant_override_preserves_nearest_fixed_value(self):
        base = [
            primary("Base"),
            primary("Parent", "Base"),
            primary("Child", "Parent"),
            prop(
                "Status",
                "Base",
                ", value_format=str, allowed_values=('draft', 'active')",
            ),
        ]
        parent = prop(
            "Status",
            "Base",
            ", applies_to_entity_classes=('Base//Parent',), "
            "allowed_values=('active',)",
        )
        child = prop(
            "Status",
            "Base",
            ", applies_to_entity_classes=('Base//Parent//Child',), "
            "field_options={'default': 'active'}",
        )
        for overrides in ([parent, child], [child, parent]):
            namespace = {}
            exec(assemble_model_classes(base + overrides), namespace)
            field = namespace["Child"].__dataclass_fields__["status"]
            self.assertEqual(field.metadata["allowed_values"], ("active",))
            self.assertEqual(namespace["Child"]().status, "active")
            for invalid in (
                child.replace("'active'", "'draft'"),
                child.replace("'active'", "None"),
                child.replace(
                    "field_options={'default': 'active'}",
                    "allowed_values=('draft', 'active')",
                ),
            ):
                with self.assertRaisesRegex(ValueError, "allowed_values"):
                    assemble_model_classes(base + [invalid, parent])

        self._check_own_fixed_value(base, parent, child)

    def _check_own_fixed_value(self, base, parent, child):
        own_fixed_value = child.replace(
            "field_options={'default': 'active'}", "allowed_values=('draft',)"
        )
        namespace = {}
        exec(
            assemble_model_classes(base + [own_fixed_value, parent]), namespace
        )
        self.assertEqual(
            namespace["Child"]
            .__dataclass_fields__["status"]
            .metadata["allowed_values"],
            ("draft",),
        )

    def test_class_var_and_mixed_layout(self):
        claims = [
            primary("Base"),
            prop(
                "URL Value",
                "Base",
                ", value_format=str, "
                "field_options={'class_var': True, 'default': 'value'}",
            ),
        ]
        module = ModuleType("manifest_classvar_fixture")
        with patch.dict(sys.modules, {module.__name__: module}):
            exec(assemble_model_classes(claims), vars(module))
            self.assertEqual(module.Base.url_value, "value")
            self.assertEqual(__import__("dataclasses").fields(module.Base), ())
        with self.assertRaisesRegex(ValueError, "requires entity_kind"):
            assemble_model_classes(
                claims
                + [
                    prop("Other", "Base", ", value_format=str").replace(
                        "entity_kind='Property', ", ""
                    )
                ]
            )

    def test_fields_are_sorted_required_first_and_independent_of_claim_order(
        self,
    ):
        claims = [
            primary("Base"),
            prop(
                "Optional",
                "Base",
                ", value_format=str, field_options={'default': 'x'}",
            ),
            prop("Required", "Base", ", value_format=str"),
        ]
        source = assemble_model_classes(claims)
        self.assertEqual(source, assemble_model_classes(reversed(claims)))
        self.assertEqual(
            assemble_model_modules(claims),
            assemble_model_modules(reversed(claims)),
        )
        namespace = {}
        exec(source, namespace)
        self.assertEqual(namespace["Base"]("value").required, "value")
        self.assertEqual(
            assemble_model_modules(self.claims()),
            assemble_model_modules(reversed(self.claims())),
        )
