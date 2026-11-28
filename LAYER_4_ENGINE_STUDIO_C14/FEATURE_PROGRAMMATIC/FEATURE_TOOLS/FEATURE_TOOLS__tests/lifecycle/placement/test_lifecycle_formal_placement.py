"""Formal Delivery claims alone determine the compiled placement policy."""

from dataclasses import replace
from pathlib import Path
import json
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TOOLS))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.FEATURE_TOOLS__tests__shared import (  # noqa: E402
    compile_candidate_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle._candidate_schema_read import (  # noqa: E402
    load_candidate_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.placement.placement_model import (  # noqa: E402
    active_placement,
)


def carrier(atom_id, role, status, body, subject=None):
    topics = (
        f"topics:\n  main_subject: {json.dumps(subject)}\n" if subject else ""
    )
    return (
        f"---\natom_id: {atom_id}\nrole: {role}\nform: Declaration\n"
        f"status: {status}\nversion: 1\n{topics}---\n{body}\n"
    )


def status_rule(status, base, folder, role=None):
    return {
        "kind": "status",
        "role": role,
        "status": status,
        "base": base,
        "folder": folder,
    }


RULES = (
    {"kind": "role_root"},
    status_rule("draft", "role", "draft"),
    status_rule("archived", "role", "archived"),
    status_rule("*", "container", "<lowercase status>"),
    status_rule("active", "container", ""),
    status_rule("backlog", "role", "Backlog", "plan"),
)


def native_body(rules):
    return (
        "## Claim\n### Formal Claim\n```python\nplacement_rules = "
        + repr(tuple(rules))
        + "\n```\n"
    )


def role_source(root, name, number, atom_id):
    class_name = name.replace(" ", "")
    order = (
        f', classifications={{"Role Order Number": {number}}}'
        if number is not None
        else ""
    )
    code = (
        "from anechoic.model import Atom\n"
        "from anechoic.formal_claims import declare_entity\n"
        f"class {class_name}(Atom):\n    pass\n"
        f"declare_entity(entity_class={class_name}, entity_name={name!r}, "
        f'qualification_property_path="Atom.Header.Context.Role"{order})'
    )
    subject = f"ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := {name})"
    (root / f"{atom_id}.md").write_text(
        carrier(
            atom_id,
            "Requirement",
            "Active",
            f"## Claim\n### Formal Claim\n```python\n{code}\n```\n",
            subject,
        )
    )


class FormalPlacementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "CA-R-1.md").write_text(
            carrier(
                "CA-R-1",
                "Requirement",
                "Active",
                "## Claim\n### Formal Claim\n```python\n"
                "from anechoic.formal_claims import declare_entity\n"
                "declare_entity(entity_name='Form', "
                "relation_name='IS_PROPERTY_OF', "
                "base_path='Atom.Header.Context', "
                "allowed_values=('Plan',))\n```\n",
                "ANECHOIC_MODEL <+ Atom.Header.Context.Form",
            )
        )

    def delivery(
        self,
        rules=RULES,
        atom_id="CA-D-747",
        subject="ANECHOIC_MODEL <+ Carrier",
        status="Active",
    ):
        (self.root / f"{atom_id}.md").write_text(
            carrier(
                atom_id,
                "Delivery",
                status,
                "## Claim\n### Prose Claim\n```python\n"
                "placement_rules = ()\n```\n"
                + native_body(rules).removeprefix("## Claim\n"),
                subject,
            )
        )

    def compile(self):
        output = self.root.parent / (self.root.name + "-schema.json")
        self.addCleanup(output.unlink, missing_ok=True)
        output.write_bytes(compile_candidate_schema(self.root))
        return load_candidate_schema(output)

    def _write_formal_sources(self):
        role_source(self.root, "Concern", 77, "CA-R-77")
        role_source(self.root, "Plan", 3, "CA-R-78")
        self.delivery(
            RULES[:1], "CA-D-747", "ANECHOIC_MODEL <+ Atom.Header.Context.Role"
        )
        self.delivery(
            RULES[1:5],
            "CA-D-9123",
            "ANECHOIC_MODEL <+ Atom.Header.State.Status",
        )
        self.delivery(
            RULES[5:],
            "CA-D-98236",
            "ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)."
            "Header.State.Status >| Status Group := Backlog",
        )
        self.delivery(
            RULES[5:],
            "CA-D-8890",
            "ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)."
            "Header.State.Status >| Status Group := Other",
        )
        self.delivery(RULES, "CA-D-8888", "ANECHOIC_MODEL <+ Unrelated")
        self.delivery(
            RULES, "CA-D-8889", "ANECHOIC_MODEL <+ Carrier <+ Unrelated"
        )
        for atom_id, status in [("CA-D-2", "Archived"), ("CA-D-3", "Draft")]:
            self.delivery(RULES, atom_id, "ANECHOIC_MODEL <+ Carrier", status)

    def test_formal_rules_compile_and_ignore_prose_comments_and_archived(self):
        self._write_formal_sources()
        rules = self.compile().placement
        self.assertEqual("77_concern", rules.role_folder("Concern"))
        self.assertEqual(("container", ""), rules.placement("Plan", "Active"))
        self.assertEqual(
            ("role", "Backlog"), rules.placement("Plan", "Backlog")
        )
        self.assertEqual(
            ("container", "resolved"), rules.placement("Concern", "Resolved")
        )
        self.assertEqual(("role", "draft"), rules.placement("Plan", "Draft"))
        self.assertEqual(
            ("role", "archived"), rules.placement("Plan", "Archived")
        )
        self.assertEqual(
            {"CA-D-747", "CA-D-9123", "CA-D-98236", "CA-R-77", "CA-R-78"},
            {row["atom_id"] for row in rules.sources},
        )
        updated = replace(rules)
        self.assertIs(updated.role_folders, rules.role_folders)
        self.assertIs(updated.sources[0], rules.sources[0])
        with self.assertRaises(TypeError):
            updated.role_folders["new"] = "42_new"

    def test_duplicate_formal_binding_fails(self):
        role_source(self.root, "Concern", 77, "CA-R-77")
        role_source(self.root, "Plan", 3, "CA-R-78")
        self.delivery(RULES + RULES[:1])
        with self.assertRaisesRegex(ValueError, "[Dd]uplicate"):
            self.compile()

    def test_native_placement_claim_rejects_unsafe_folder(self):
        role_source(self.root, "Concern", 77, "CA-R-77")
        role_source(self.root, "Plan", 3, "CA-R-78")
        self.delivery(RULES)
        rules = self.compile().placement
        self.assertEqual(
            ("role", "Backlog"), rules.placement("Plan", "Backlog")
        )
        bad = RULES[:-1] + (
            status_rule("backlog", "role", "../Backlog", "plan"),
        )
        self.delivery(bad)
        with self.assertRaisesRegex(ValueError, "Unsafe placement folder"):
            self.compile()

    def test_missing_placement_cannot_be_used_as_a_model(self):
        self.assertIsNone(self.compile().placement)
        with self.assertRaisesRegex(ValueError, "not bound"):
            active_placement()


if __name__ == "__main__":
    unittest.main()
