from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope_carrier__pub import (
    ScopeDeclarationError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope_declaration_parse__pub import (
    parse_scope_unit_declaration,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.units.scope_unit_declarations__pub import (
    read_scope_unit_declarations,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.declarations.scopes.scope_unit_declaration_test_support import (
    ScopeUnitFixture,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.declarations.scopes import (
    _scope_unit_subject_cases as cases,
)

TOOLS = Path(__file__).resolve().parents[3]


class ScopeUnitDeclarationReaderTests(
    cases.ScopeUnitSubjectCases, ScopeUnitFixture, unittest.TestCase
):
    def test_formal_claim_layout_and_ambiguous_fences(self) -> None:
        source = self.declaration("demo", "CA-R-1", project=True)
        current = source.read_text(encoding="utf-8")
        self.assertIn("### Formal Claim\n\n```python\n", current)
        self.assertEqual(
            "demo", parse_scope_unit_declaration(current.encode(), source).name
        )
        for invalid in (
            current.replace("```python", "```CFEL"),
            current.replace("### Formal Claim", "### Prose Claim"),
            current + "\n```python\nextra\n```\n",
            current.rsplit("```", 1)[0],
            current.replace(
                "declare_entity(", "open('unexpected', 'w')\ndeclare_entity("
            ),
        ):
            with (
                self.subTest(invalid=invalid),
                self.assertRaises(ScopeDeclarationError),
            ):
                parse_scope_unit_declaration(invalid.encode(), source)

    def test_compatibility_python_claim_is_rejected(self) -> None:
        source = self.declaration("demo", "CA-R-1", project=True)
        current = source.read_text(encoding="utf-8")
        start = current.index("```python\n")
        old = current[:start] + (
            '```python\nset_value(address="Project//demo.Name", '
            'value="demo")\n```\n'
        )
        with self.assertRaises(ScopeDeclarationError):
            parse_scope_unit_declaration(old.encode(), source)

    def test_native_typed_scope_and_root(self) -> None:
        root, parent, child = self.complete_tree()

        def convert(source: Path, claim: str) -> str:
            text = source.read_text(encoding="utf-8")
            start = text.index("```python\n")
            end = text.index("\n```", start) + len("\n```")
            return text[:start] + "```python\n" + claim + "\n```" + text[end:]

        root_claim = (
            "from anechoic.model import Project\n"
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="demo", instance=Project(id="CA-SU-00", name="demo"))'
        )
        parent_claim = (
            "from anechoic.model import ScopeUnit\n"
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="PARENT", instance=ScopeUnit('
            'id="CA-SU-1", name="PARENT", label="LAYER", ordered=True, '
            'order_number=1, container="demo"))'
        )
        original = parse_scope_unit_declaration(parent.read_bytes(), parent)
        native = convert(parent, parent_claim)
        self.assertEqual(
            original, parse_scope_unit_declaration(native.encode(), parent)
        )
        self.assertEqual(
            parse_scope_unit_declaration(root.read_bytes(), root),
            parse_scope_unit_declaration(
                convert(root, root_claim).encode(), root
            ),
        )
        with_level = native.replace(
            'container="demo"', 'container="demo", structural_level=2'
        )
        self.assertEqual(
            2,
            parse_scope_unit_declaration(
                with_level.encode(), parent
            ).structural_level,
        )
        self._assert_invalid_native_claims(
            convert, root, parent, root_claim, parent_claim
        )
        root.write_text(convert(root, root_claim))
        parent.write_text(native)
        self._assert_native_lint_and_discovery(root, parent)

    def _assert_invalid_native_claims(
        self, convert, root, parent, root_claim, parent_claim
    ):
        invalid = (
            parent_claim.replace(
                'entity_name="PARENT"', 'entity_name="OTHER"'
            ),
            parent_claim.replace('name="PARENT"', 'name="OTHER"'),
            parent_claim.replace("ordered=True", "ordered=False"),
            parent_claim.replace("order_number=1", "order_number=True"),
            parent_claim.replace("order_number=1", "order_number=0"),
            parent_claim.replace('container="demo"', 'container="../bad"'),
            parent_claim.replace(
                'container="demo"', 'container="demo", structural_level=-1'
            ),
            parent_claim.replace('id="CA-SU-1"', 'id=__import__("os")'),
            parent_claim + '\nprint("side effect")',
        )
        for claim in invalid:
            with (
                self.subTest(claim=claim),
                self.assertRaises(ScopeDeclarationError),
            ):
                parse_scope_unit_declaration(
                    convert(parent, claim).encode(), parent
                )
        with self.assertRaises(ScopeDeclarationError):
            parse_scope_unit_declaration(
                convert(
                    root, root_claim.replace("CA-SU-00", "CA-SU-01")
                ).encode(),
                root,
            )

    def _assert_native_lint_and_discovery(
        self, root: Path, parent: Path
    ) -> None:
        addresses, relations = (
            self.root / "addresses.json",
            self.root / "relations.json",
        )
        addresses.write_text('["Scope Unit", "Project"]')
        relations.write_text("[]")
        linter = (
            TOOLS.parent
            / "FEATURE_FORMAL_MODEL_ENGINE/lint_python_model_claim__pub.py"
        )
        lint = subprocess.run(
            [
                sys.executable,
                "-B",
                str(linter),
                str(parent),
                str(root),
                "--addresses",
                str(addresses),
                "--relations",
                str(relations),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(0, lint.returncode, lint.stderr)
        result = read_scope_unit_declarations(self.root, self.control.name)
        self.assertEqual({"demo", "PARENT", "CHILD"}, set(result.by_name))

    def test_discovers_current_sources_and_derives_all_paths(self) -> None:
        root_source, parent_source, child_source = self.complete_tree()
        result = read_scope_unit_declarations(self.root, self.control.name)

        self.assertEqual(result.root.name, "demo")
        self.assertEqual(
            tuple(result.paths),
            tuple(sorted((root_source, parent_source, child_source))),
        )
        self.assertEqual(set(result.by_name), {"demo", "PARENT", "CHILD"})
        self.assertEqual(len(result.digest), 64)
        self.assertEqual(
            set(result.source_pins),
            {
                source.relative_to(self.root).as_posix()
                for source in (root_source, parent_source, child_source)
            },
        )
        self._assert_discovered_paths(result)

    def _assert_discovered_paths(self, result):
        rows = {
            row["scope_unit_name"]: row
            for row in result.as_structure()["scope_units"]
        }
        self.assertEqual(
            rows["demo"],
            {
                "scope_unit_name": "demo",
                "parent": "PROJECT",
                "scope_unit_id": None,
                "scope_unit_label": None,
                "scope_unit_type": "Unordered",
                "admitted_role_forms": (),
                "authority_path": ".anechoic_demo",
                "delivery_path": ".",
            },
        )
        self.assertEqual(
            rows["PARENT"]["authority_path"],
            ".anechoic_demo/CA-SU-1_LAYER_1_PARENT",
        )
        self.assertEqual(rows["PARENT"]["delivery_path"], "LAYER_1_PARENT")
        self.assertEqual(
            rows["CHILD"]["authority_path"],
            ".anechoic_demo/CA-SU-1_LAYER_1_PARENT/CA-SU-2_FEATURE_CHILD",
        )
        self.assertEqual(
            rows["CHILD"]["delivery_path"], "LAYER_1_PARENT/FEATURE_CHILD"
        )

    def test_structure_topics_follow_discovered_names(self) -> None:
        child, delegation = self._structure_topic_fixture()
        self.assertEqual(
            {"anechoic", "PARENT", "CHILD"},
            set(
                read_scope_unit_declarations(
                    self.root, self.control.name
                ).by_name
            ),
        )
        delegation.write_text(
            delegation.read_text().replace(
                "ANECHOIC_STRUCTURE/PARENT/CHILD",
                "ANECHOIC_STRUCTURE/WRONG/CHILD",
            )
        )
        with self.assertRaisesRegex(
            ScopeDeclarationError, "contradicts declared containment"
        ):
            read_scope_unit_declarations(self.root, self.control.name)
        delegation.unlink()
        child.write_text(
            child.read_text().replace(
                "ANECHOIC_STRUCTURE/PARENT/CHILD",
                "ANECHOIC_STRUCTURE/WRONG/CHILD",
            )
        )
        with self.assertRaisesRegex(
            ScopeDeclarationError, "contradicts declared containment"
        ):
            read_scope_unit_declarations(self.root, self.control.name)

    def _structure_topic_fixture(self):
        root, parent, child = self.complete_tree()
        import re

        def topic(path, value):
            path.write_text(
                re.sub(
                    r"(?m)^  active: .*$",
                    f'  active: "{value}"',
                    path.read_text(),
                )
            )

        root.write_text(
            root.read_text()
            .replace('entity_name="demo"', 'entity_name="anechoic"')
            .replace('name="demo"', 'name="anechoic"')
        )
        parent.write_text(
            parent.read_text().replace(
                'container="demo"', 'container="anechoic"'
            )
        )
        topic(root, "ANECHOIC_STRUCTURE")
        topic(parent, "ANECHOIC_STRUCTURE/PARENT")
        topic(child, "ANECHOIC_STRUCTURE/PARENT/CHILD")
        delegation = child.parent / "CA-R-4-delegation.md"
        raw = (
            child.read_text()
            .replace("CA-R-3", "CA-R-4")
            .replace("form: Scope Unit Declaration", "form: Scope Delegation")
        )
        raw = (
            raw[: raw.index("### Formal Claim")]
            + "### Prose Claim\n\nDelegated responsibility.\n"
        )
        delegation.write_text(
            raw.replace("---\n", "---\ncontainer:\n  scope_unit: CA-SU-1\n", 1)
        )
        return child, delegation


if __name__ == "__main__":
    unittest.main()
