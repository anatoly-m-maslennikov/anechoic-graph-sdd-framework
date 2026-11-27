import unittest
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.\
    manifest_compiler_CS1 import (
    active_model_sources as sources,
)
# fmt: on


_CUSTOM_BODY = (
    "## Formal Manifest\n\n```python anechoic-edsl\n"
    "class APPLIES(Relation):\n    pass\n```\n"
)


def _implicit_header():
    return {
        "atom_family": "SPEC",
        "atom_id": "AN-S-1",
        "state": {
            "status": "draft",
            "version": 1,
            "updated_at": "2026-11-24T00:00:00Z",
        },
        "concern": {
            "subject": "Graph",
            "path": "Model",
            "relation": "is_contained_by",
        },
        "structure": {"container": {"component": "C9"}},
        "context": {"lens": "DOM/CONT", "template": "manifest_node"},
    }


def _variant_fixture():
    metadata = {
        "atom_family": "PROJECT_CONFIG",
        "atom_id": "AN-C-2",
        "structure": {"container": {"component": "C00"}},
        "context": {"template": "manifest_node"},
        "state": {
            "status": "active",
            "version": 1,
            "updated_at": "2026-11-24T00:00:00Z",
        },
        "concern": {
            "path": "Model/Graph/Node//Atom//Spec Atom//.Header.Context",
            "relation": ".",
            "subject": "Template := axiom",
        },
    }
    body = """## Formal Manifest

```python anechoic-edsl
from anechoic.formal_claims import value
from anechoic.model import SpecAtom

class Axiom(SpecAtom):
    node.template = value(fixed='axiom')
```
"""
    return metadata, body


class ContinuantModelSourceTests(unittest.TestCase):
    def test_implicit_continuant_node_and_custom_concern(self):
        self._check_implicit_node()
        self._check_custom_concern()

    def _check_implicit_node(self):
        # fmt: off
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.\
            ATOM_LIFECYCLE__shared import InputError
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.\
            native_draft_guards import _validate_c9_typed_manifest
        # fmt: on

        header = _implicit_header()
        _validate_c9_typed_manifest(header, "## Summary\n\nGraph\n")
        typed = []
        sources._collect_manifest_claims(
            "## Summary\n\nGraph\n",
            False,
            "node@1",
            "MODEL//ANECHOIC <+ Graph",
            header["context"],
            set(),
            [],
            typed,
            header["concern"],
        )
        assert typed[0][2] == "class Graph:\n    pass\n"
        for subject, relation in [
            ("Graph Node", "is_contained_by"),
            ("Graph", "is_narrower_than"),
        ]:
            invalid = {
                **header,
                "concern": {
                    **header["concern"],
                    "subject": subject,
                    "relation": relation,
                },
            }
            with self.assertRaises(InputError):
                _validate_c9_typed_manifest(invalid, "## Summary\n\nGraph\n")

    def _check_custom_concern(self):
        metadata = {
            "atom_family": "PROJECT_CONFIG",
            "atom_id": "AN-C-1",
            "structure": {"container": {"component": "C00"}},
            "context": {"template": "manifest_relation"},
            "state": {
                "status": "active",
                "version": 1,
                "updated_at": "2026-11-24T00:00:00Z",
            },
            "concern": {
                "subject": "APPLIES",
                "path": "Model/Graph/Relation",
                "relation": "is_narrower_than",
            },
        }
        body = _CUSTOM_BODY
        typed = []
        sources._collect_active_source(
            Path("/snapshot/__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-1-test.md"),
            True,
            metadata,
            body,
            Path("/snapshot"),
            set(),
            set(),
            [],
            typed,
        )
        assert typed[0][1] == "MODEL//ANECHOIC <+ Graph/Relation//APPLIES"
        with self.assertRaisesRegex(ValueError, "cannot contain Claim scope"):
            sources._collect_active_source(
                Path("/snapshot/__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-1-test.md"),
                True,
                metadata,
                "## Claim scope\n\nMODEL//ANECHOIC <+ Graph\n\n" + body,
                Path("/snapshot"),
                set(),
                set(),
                [],
                [],
            )

    def test_split_variant_concern_agrees_with_fixed_template(self):
        metadata, body = _variant_fixture()
        path = Path("/snapshot/__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-2-test.md")
        typed = []
        sources._collect_active_source(
            path,
            True,
            metadata,
            body,
            Path("/snapshot"),
            set(),
            set(),
            [],
            typed,
        )
        assert (
            typed[0][1]
            == "MODEL//ANECHOIC <+ Graph/Node//Atom//Spec Atom//Axiom"
        )
        self._check_variant_draft(metadata, body, path)

    def _check_variant_draft(self, metadata, body, path):
        # fmt: off
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.\
            ATOM_LIFECYCLE__shared import InputError
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.\
            native_draft_guards import _validate_c9_typed_manifest
        # fmt: on

        draft = {
            **metadata,
            "atom_family": "SPEC",
            "atom_id": "AN-S-2",
            "tier": 2,
            "container": {"component": "C9"},
            "context": {**metadata["context"], "lens": "DOM/CONT"},
        }
        draft.pop("structure")
        _validate_c9_typed_manifest(draft, body)
        for rule in ("value(fixed='other')", "value(default='axiom')"):
            mismatched = body.replace("value(fixed='axiom')", rule)
            with self.assertRaisesRegex(
                ValueError, "must match the fixed node.template"
            ):
                sources._collect_active_source(
                    path,
                    True,
                    metadata,
                    mismatched,
                    Path("/snapshot"),
                    set(),
                    set(),
                    [],
                    [],
                )
            with self.assertRaises(InputError):
                _validate_c9_typed_manifest(draft, mismatched)


if __name__ == "__main__":
    unittest.main()
