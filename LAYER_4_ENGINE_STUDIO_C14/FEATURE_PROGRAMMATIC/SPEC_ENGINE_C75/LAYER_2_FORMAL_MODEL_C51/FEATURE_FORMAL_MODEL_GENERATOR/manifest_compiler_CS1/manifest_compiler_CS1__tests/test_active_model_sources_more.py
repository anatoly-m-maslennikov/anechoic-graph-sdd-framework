import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    ReadContext,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.\
    native_draft_guards import (
    _validate_c9_typed_manifest,
)  # fmt: skip
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


class ActiveModelSourcesMoreTests(unittest.TestCase):
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

    def test_custom_multiple_declarations_and_rejections(self):
        self.put("AN-S-1-SPEC--atom.md", carrier())
        custom = self.root / "002_PROJECT_CONFIG" / "CUSTOM_MODEL"
        custom.mkdir(parents=True)
        declaration = custom / "AN-C-1-MODEL_MANIFEST--node.md"
        text = custom_carrier() + (
            "\n### Other\n\nMODEL//ANECHOIC <+ Other\n\n"
            f"```python\n{CLAIM}```\n"
        )
        declaration.write_text(text)
        self.assertEqual(len(self.read()), 3)
        for invalid in (
            text.replace(
                "MODEL//ANECHOIC <+ Other", "MODEL//ANECHOIC <+ Node"
            ),
            text.replace("MODEL//ANECHOIC <+ Other", "Other"),
            text + "\n#### Nested\n\nignored\n",
            text + "\nExtra text\n",
            text.replace(
                "declare_entity(entity_name='Atom')",
                "declare_entity(entity_name='Atom')\nprint('unsafe')",
            ),
        ):
            with self.subTest(invalid=invalid[-60:]):
                declaration.write_text(invalid)
                with self.assertRaises(ValueError):
                    self.read()
        declaration.write_text(custom_carrier())
        (custom / "AN-C-1-MODEL_MANIFEST--duplicate.md").write_text(
            custom_carrier(subject="MODEL//ANECHOIC <+ Other")
        )
        with self.assertRaisesRegex(ValueError, "duplicate Model source ID"):
            self.read()

    def test_typed_template_must_match_class(self):
        self.put("AN-S-1-SPEC--atom.md", carrier())
        custom = self.root / "__PROJECT_CONFIG" / "CUSTOM_MODEL"
        custom.mkdir(parents=True)
        typed = custom_carrier().replace(
            "template: model_manifest", "template: manifest_node"
        )
        typed = typed.replace(
            "### Node\n\nMODEL//ANECHOIC <+ Node\n\n```python\n" + CLAIM,
            "```python anechoic-edsl\nfrom anechoic.model import Property\n"
            "class Example(Property):\n    pass\n",
        )
        (custom / "AN-C-1-MANIFEST_NODE--node.md").write_text(typed)
        with self.assertRaisesRegex(
            ValueError, "template and class do not match"
        ):
            self.read()

    def test_c9_typed_template_mismatch_rejected_for_all_kinds(self):
        for template, base in (
            ("manifest_node", "Property"),
            ("manifest_property", "Relation"),
            ("manifest_relation", "NodeConstraints"),
        ):
            text = carrier().replace(
                "  lens: SPEC", f"  lens: SPEC\n  template: {template}"
            )
            text = text[: text.index("## Claim\n")] + (
                "## Formal Manifest\n\n```python anechoic-edsl\n"
                f"from anechoic.model import {base}\n"
                f"class Example({base}):\n    pass\n```\n"
            )
            self.put("AN-S-1-SPEC--atom.md", text)
            with (
                self.subTest(template=template),
                self.assertRaisesRegex(
                    ValueError, "template and class do not match"
                ),
            ):
                self.read()

    def test_typed_c9_without_scope_is_rejected(self):
        text = carrier().replace(
            "  lens: SPEC", "  lens: SPEC\n  template: manifest_node"
        )
        text = text.replace("MODEL//ANECHOIC <+ Atom", "Other")
        self.put("AN-S-1-SPEC--atom.md", text)
        with self.assertRaisesRegex(
            ValueError, "typed Manifest requires a Model Claim scope"
        ):
            self.read()

    def put_property_relation(self):
        relation = (
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='IS_PROPERTY_OF', "
            "source_endpoint={'level': 'model_entities'}, "
            "target_endpoint={'level': 'model_entities'})\n"
        )
        self.put(
            "AN-S-4-SPEC--is-property-of.md",
            carrier(
                "AN-S-4",
                subject="MODEL//ANECHOIC <+ Graph/Relation//IS_PROPERTY_OF",
            ).replace(CLAIM, relation),
        )

    def unscoped_c9_fixture(self):
        atom = CLAIM.replace(
            "declare_entity(entity_name='Atom')",
            "class Atom:\n    pass\n"
            "declare_entity(entity_name='Atom', entity_class=Atom, "
            "entity_kind='Primary')",
        )
        self.put("AN-S-1-SPEC--atom.md", carrier().replace(CLAIM, atom))
        scope = "MODEL//ANECHOIC <+ Atom.Header.Relations"
        relations = (
            carrier("AN-S-2", subject=scope)
            .replace(
                "  lens: SPEC", "  lens: SPEC\n  template: manifest_property"
            )
            .replace(
                "## Claim\n\n### Formal Claim\n\n```python\n" + CLAIM,
                "## Formal Manifest\n\n```python anechoic-edsl\n"
                "from anechoic.model import Atom, Property\n"
                "class AtomRelations(Property):\n    name = 'Relations'\n"
                "    bearer = Atom.Header\n    value_cardinality = 0\n",
            )
        )
        header_scope = "MODEL//ANECHOIC <+ Atom.Header"
        header = (
            relations.replace("AN-S-2", "AN-S-3")
            .replace(scope, header_scope)
            .replace("AtomRelations", "Header")
            .replace("'Relations'", "'Header'")
            .replace("bearer = Atom.Header", "bearer = Atom")
        )
        self.put("AN-S-2-SPEC--relations.md", relations)
        self.put("AN-S-3-SPEC--header.md", header)
        self.put_property_relation()
        scoped = self.read()
        self.assertEqual(
            scoped[2][:2],
            ("META_ONTOLOGY_C9/AN-S-2-SPEC--relations.md@1", scope),
        )

        return scoped, relations, header, scope, header_scope

    def test_unscoped_c9_property_matches_scoped_property(self):
        scoped, relations, header, scope, header_scope = (
            self.unscoped_c9_fixture()
        )

        def unscoped(text, subject):
            return text.replace(f"## Claim scope\n\n{subject}\n\n", "")

        self.put("AN-S-2-SPEC--relations.md", unscoped(relations, scope))
        self.put("AN-S-3-SPEC--header.md", unscoped(header, header_scope))
        rows = []
        for path in sorted(self.component.glob("*.md")):
            source = path.relative_to(self.root).as_posix()
            parsed = sources.parse_carrier(path.read_bytes(), path)
            rows.append(
                {
                    "source_path": source,
                    "exact_ref": f"{parsed.metadata['identity']['atom_id']}@1",
                    "metadata": parsed.metadata,
                    "body": parsed.body,
                }
            )
        _validate_c9_typed_manifest(rows[1]["metadata"], rows[1]["body"])
        self.assertEqual(self.read(), scoped)
        self.assertEqual(
            sources.compile_active_model_rows(rows, has_c9=True), scoped
        )
        rows[1]["body"] = rows[1]["body"].replace(
            "    bearer = Atom.Header\n",
            "    bearer = Atom.Header\n    classification = True\n",
        )
        with self.assertRaisesRegex(ValueError, "Invalid typed Model scope"):
            _validate_c9_typed_manifest(rows[1]["metadata"], rows[1]["body"])
        with self.assertRaisesRegex(ValueError, "ordinary Property"):
            sources.compile_active_model_rows(rows, has_c9=True)

    def test_changed_input_rejected(self):
        self.put("AN-S-1-SPEC--atom.md", carrier())
        with (
            patch.object(
                ReadContext, "currentness", return_value={"state": "changed"}
            ),
            self.assertRaisesRegex(ValueError, "changed"),
        ):
            self.read()


if __name__ == "__main__":
    unittest.main()
