import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1 import (
    active_model_sources as sources,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.\
    manifest_compiler_CS1__shared import (
    read_active_model_sources,
)  # fmt: skip

CLAIM = (
    "from anechoic.formal_claims import declare_entity\n"
    "declare_entity(entity_name='Atom')\n"
)


def carrier(
    identifier="AN-S-1",
    subject="MODEL//ANECHOIC <+ Atom",
    status="active",
    version=1,
):
    return (
        f"---\nidentity:\n  atom_id: {identifier}\ncontext:\n"
        "  container:\n    component: C9\n"
        f"  lens: SPEC\nstate:\n  status: {status}\n"
        f"  version: {version}\n---\n"
        f"## Claim scope\n\n{subject}\n\n## Claim\n\n"
        f"### Formal Claim\n\n```python\n{CLAIM}```\n"
    )


def custom_carrier(
    identifier="AN-C-1", subject="MODEL//ANECHOIC <+ Node", status="active"
):
    return (
        f"---\natom_family: PROJECT_CONFIG\natom_id: {identifier}\n"
        "structure:\n  container:\n    component: C00\n"
        f"context:\n  template: model_manifest\nstate:\n"
        f"  status: {status}\n  version: 1\n"
        f"  updated_at: 2026-11-20T00:00:00Z\n---\n"
        "## Semantics\n\nSemantics.\n\n## Formal Manifest\n\n"
        f"### Node\n\n{subject}\n\n```python\n{CLAIM}```\n"
    )


class ActiveModelSourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.component = self.root / "META_ONTOLOGY_C9"
        self.component.mkdir()

    def put(self, filename, text):
        (self.component / filename).write_text(text)

    def read(self):
        return read_active_model_sources(self.root, self.component)

    def test_selection_and_out_of_scope(self):
        self.put("AN-S-1-SPEC--atom.md", carrier(version=2))
        self.put("AN-S-2-SPEC--draft.md", carrier("AN-S-2", status="draft"))
        self.put("AN-S-3-SPEC--other.md", carrier("AN-S-3", subject="Other"))
        (self.component / "000_draft").mkdir()
        (self.component / "000_draft" / "bad.md").write_text("bad")
        self.assertEqual(
            self.read(),
            (
                (
                    "META_ONTOLOGY_C9/AN-S-1-SPEC--atom.md@2",
                    "MODEL//ANECHOIC <+ Atom",
                    CLAIM,
                ),
            ),
        )

    def test_typed_des_property_selected_and_legacy_des_excluded(self):
        folder = self.component / "_DES"
        folder.mkdir()
        typed = (
            carrier("AN-S-2", subject="MODEL//ANECHOIC <+ Atom.Content")
            .replace(
                "  lens: SPEC", "  lens: DES\n  template: manifest_property"
            )
            .replace(
                "## Claim\n\n### Formal Claim\n\n```python\n" + CLAIM,
                "## Formal Manifest\n\n```python anechoic-edsl\n"
                "from anechoic.model import Atom, Property\n"
                "class Content(Property):\n    bearer = Atom\n"
                "    value_cardinality = 0\n",
            )
        )
        (folder / "AN-S-2-SPEC--content.md").write_text(typed)
        (folder / "AN-S-3-SPEC--legacy.md").write_text(
            carrier("AN-S-3").replace("lens: SPEC", "lens: DES")
        )
        with patch.object(
            sources,
            "_lower_active_sources",
            side_effect=lambda records, subjects, typed, **kw: (
                records,
                typed,
            ),
        ):
            records, selected = self.read()
        self.assertEqual([], records)
        self.assertEqual(1, len(selected))
        self.assertIn("/_DES/AN-S-2-", selected[0][0])
        self.assertEqual("manifest_property", selected[0][3])

    def test_spec_directory_and_cross_layout_duplicate(self):
        spec = self.component / "_SPEC"
        spec.mkdir()
        (spec / "AN-S-1-SPEC--atom.md").write_text(carrier())
        self.assertEqual(
            self.read()[0][0], "META_ONTOLOGY_C9/_SPEC/AN-S-1-SPEC--atom.md@1"
        )
        self.put(
            "AN-S-1-SPEC--other.md", carrier(subject="MODEL//ANECHOIC <+ Node")
        )
        with self.assertRaisesRegex(ValueError, "duplicate Model source ID"):
            self.read()

    def test_new_custom_config_directory(self):
        self.put("AN-S-1-SPEC--atom.md", carrier())
        custom = self.root / "__PROJECT_CONFIG" / "CUSTOM_MODEL"
        custom.mkdir(parents=True)
        (custom / "AN-C-1-MODEL_MANIFEST--node.md").write_text(
            custom_carrier()
        )
        self.assertEqual(len(self.read()), 2)

    def test_raw_custom_node_axis_values_are_checked(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
            LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.\
            manifest_compiler_CS1.typed_property_relation_lowering import (
            lower_typed_fields,
        )  # fmt: skip

        scope = "MODEL//ANECHOIC <+ Graph/Axis >| Temporality"
        axis = (
            "from anechoic.model import Property, Axis\n"
            "class Temporality(Property):\n    bearer = Axis\n"
            "    property.axis = True\n    allowed_values = ('Continuant',)\n"
        )
        claim = lower_typed_fields(
            "manifest_property", axis, scope, {"Axis": "Graph/Axis"}
        )
        self.put(
            "AN-S-1-SPEC--axis.md",
            carrier(subject=scope).replace(CLAIM, claim + "\n"),
        )
        custom = self.root / "__PROJECT_CONFIG" / "CUSTOM_MODEL"
        custom.mkdir(parents=True)
        path = custom / "AN-C-1-MODEL_MANIFEST--node.md"
        node = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import Node\n"
            "class Probe(Node):\n    pass\n"
            "declare_entity(entity_name='Probe', entity_class=Probe, "
            "entity_kind='Primary', axes={'Temporality': 'Continuant'})\n"
        )
        path.write_text(
            custom_carrier(subject="MODEL//ANECHOIC <+ Probe").replace(
                CLAIM, node
            )
        )
        with patch.object(sources, "_check_relation_references"):
            self.assertEqual(len(self.read()), 2)
            path.write_text(path.read_text().replace("Continuant", "Bogus"))
            with self.assertRaisesRegex(
                ValueError, "unadmitted Entity axis Temporality=Bogus"
            ):
                self.read()

    def test_canonical_header_classifies_model(self):
        text = carrier().replace(
            "identity:\n  atom_id: AN-S-1",
            "atom_family: SPEC\natom_id: AN-S-1",
        )
        text = text.replace(
            "context:\n  container:", "structure:\n  tier: 1\n  container:"
        )
        text = text.replace("  lens: SPEC", "context:\n  lens: SPEC")
        text = text.replace(
            "  version: 1", "  version: 1\n  updated_at: 2026-11-20T00:00:00Z"
        )
        self.put("AN-S-1-OTHER--atom.md", text)
        self.assertEqual(1, len(self.read()))

    def test_duplicate_id_subject_and_invalid(self):
        self.put("AN-S-1-SPEC--atom.md", carrier())
        for name, text in [
            (
                "AN-S-1-SPEC--duplicate.md",
                carrier(subject="MODEL//ANECHOIC <+ Node"),
            ),
            ("AN-S-2-SPEC--duplicate.md", carrier("AN-S-2")),
            (
                "AN-S-2-SPEC--invalid.md",
                carrier("AN-S-2", subject="MODEL//ANECHOIC <+"),
            ),
            ("wrong.md", carrier("AN-S-2", subject="MODEL//ANECHOIC <+ Node")),
        ]:
            with self.subTest(name=name):
                self.put(name, text)
                with self.assertRaises(ValueError):
                    self.read()
                (self.component / name).unlink()

    def test_custom_sources_are_shallow_and_share_duplicate_checks(self):
        self.put("AN-S-1-SPEC--atom.md", carrier())
        custom = self.root / "002_PROJECT_CONFIG" / "CUSTOM_MODEL"
        custom.mkdir(parents=True)
        declaration = custom / "AN-C-1-MODEL_MANIFEST--node.md"
        declaration.write_text(custom_carrier())
        (custom / "AN-C-2-MODEL_MANIFEST--draft.md").write_text(
            custom_carrier("AN-C-2", status="draft")
        )
        (custom / "099_archived").mkdir()
        (custom / "099_archived" / "bad.md").write_text("bad")
        self.assertEqual(len(self.read()), 2)
        declaration.write_text(
            custom_carrier(subject="MODEL//ANECHOIC <+ Atom")
        )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.read()

    def test_custom_source_requires_native_identity_and_model_scope(self):
        self.put("AN-S-1-SPEC--atom.md", carrier())
        custom = self.root / "002_PROJECT_CONFIG" / "CUSTOM_MODEL"
        custom.mkdir(parents=True)
        declaration = custom / "AN-C-1-MODEL_MANIFEST--node.md"
        declaration.write_text(custom_carrier(subject="Other"))
        with self.assertRaisesRegex(ValueError, "Model Claim scope"):
            self.read()
        declaration.write_text(custom_carrier("AN-P-1"))
        with self.assertRaisesRegex(ValueError, "identity"):
            self.read()


if __name__ == "__main__":
    unittest.main()
