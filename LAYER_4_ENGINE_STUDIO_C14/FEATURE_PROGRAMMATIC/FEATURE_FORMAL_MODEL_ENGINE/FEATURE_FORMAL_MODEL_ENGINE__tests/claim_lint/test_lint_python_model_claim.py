"""Tests for the static Python Claim lint entry point."""

import json
import subprocess
import sys
import tempfile
import unittest

from ._claim_address_cases import ClaimAddressCases
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import (
    lint_python_model_claim,
)

TOOLS = Path(__file__).resolve().parents[2]


class LintPythonModelClaimTests(ClaimAddressCases, unittest.TestCase):
    def lint(self, source):
        return lint_python_model_claim(
            source,
            declared_addresses=["ANECHOIC_MODEL <+ Atom.Name", "Atom"],
            relation_names=["HAS_PROPERTY"],
            path="test.md",
            first_line=10,
        )

    def test_known_reference_and_relation(self):
        self.assertEqual(
            self.lint(
                (
                    'relation(source="Atom", name="HAS_PROPERTY", '
                    'target="Atom.Name")'
                )
            ),
            (),
        )

    def test_unknown_reference_and_relation_with_location(self):
        self.assertIn(
            "test.md:11:",
            self.lint('\nproperty_rule(address="Atom.Missing")')[0],
        )
        self.assertIn(
            "unknown address",
            self.lint('property_rule(address="Atom.Missing")')[0],
        )
        self.assertIn(
            "unknown Relation: WRONG",
            self.lint('relation(source="Atom", name="WRONG")')[0],
        )

    def test_unsupported_qualification_is_explicit(self):
        self.assertIn(
            "unknown address", self.lint('subject_path(address="Node.**")')[0]
        )

    def test_qualifier_wildcard_and_bound_instance(self):
        addresses = ["Atom", "Atom.Header.Context.Role", "Atom.Content.Claim"]
        source = (
            "subject_path(address='Atom/(.Header.Context.Role := Method).Content.Claim')\n"
            "subject_path(address='Atom.**')\n"
            "subject_path(address='Atom//$a')\n"
            "subject_path(address='a.Content.Claim')"
        )
        self.assertEqual(
            lint_python_model_claim(
                source, declared_addresses=addresses, relation_names=[]
            ),
            (),
        )
        result = lint_python_model_claim(
            source,
            declared_addresses=["Atom", "Atom.Content.Claim"],
            relation_names=[],
        )
        self.assertIn("unknown qualifier Property", result[0])

    def test_membership_and_named_scope_references(self):
        source = (
            "subject_path(address='Atom/(.Role in (Method, Evaluation)).Content.*')\n"
            "subject_path(address='(Atom, Atom.Content.**)')\n"
            "set_value(address='Scope Unit//TOOLS.Name', value='TOOLS')"
        )
        declared = [
            "Atom",
            "Atom.Role",
            "Atom.Content",
            "Scope Unit//TOOLS",
            "Scope Unit.Name",
        ]
        self.assertEqual(
            lint_python_model_claim(
                source, declared_addresses=declared, relation_names=[]
            ),
            (),
        )
        diagnostics = lint_python_model_claim(
            source,
            declared_addresses=declared[:-2] + ["Scope Unit.Name"],
            relation_names=[],
        )
        self.assertIn("unknown instance: Scope Unit//TOOLS", diagnostics[0])

    def test_set_value_validates_relation_alias_without_changing_expression(
        self,
    ):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.python.python__shared import (
            parse_grouped_python_model_claim,
        )

        options = dict(
            declared_addresses=["Relation"],
            relation_names=["NARROWER_THAN", "HAS_NARROWER"],
        )
        source = (
            "# model\nset_value(address='alias(Relation//NARROWER_THAN)', "
            "value='\"/\"')"
        )
        self.assertEqual((), lint_python_model_claim(source, **options))
        self.assertEqual(
            (('alias(Relation//NARROWER_THAN) == "/"', "model"),),
            parse_grouped_python_model_claim(source),
        )
        inverse = (
            "set_value(address='alias(Relation//HAS_NARROWER)', value='/')"
        )
        self.assertEqual((), lint_python_model_claim(inverse, **options))
        invalid = (
            "set_value(address='alias(Relation//narrower_than)', value='/')",
            "set_value(address='alias(Relation//MISSING)', value='/')",
            "set_value(address='alias(Relation/NARROWER_THAN)', value='/')",
            "set_value(address='alias(Relation//NARROWER_THAN', value='/')",
            "set_value(address='alias(Relation//NARROWER_THAN)', value='')",
            (
                "set_value(address='alias(Relation//NARROWER_THAN)', "
                "value='\"\"')"
            ),
            "set_value(address='alias(Relation//NARROWER_THAN)', value=1)",
        )
        for claim in invalid:
            with self.subTest(claim=claim):
                self.assertTrue(lint_python_model_claim(claim, **options))

    def test_helpers_check_declared_relations_and_delivery_targets(self):
        addresses = ["Atom", "Atom.Name"]

        def lint(source, names, **kwargs):
            return lint_python_model_claim(
                source,
                declared_addresses=addresses,
                relation_names=names,
                **kwargs,
            )

        self.assertIn(
            "CONTAINS",
            lint('composition(container="Atom", parts=("Atom.Name",))', [])[0],
        )
        self.assertIn(
            "HAS_AXIS",
            lint('classify(address="Atom", axis="Role", value="Method")', [])[
                0
            ],
        )
        self.assertIn(
            "IS_ORDERED_RIGHT_BEFORE",
            lint('order_before(first="Atom", second="Atom.Name")', [])[0],
        )
        delivery = 'deliver(source="Atom", carrier="Atom.Name")'
        self.assertEqual(lint(delivery, []), ())
        self.assertIn(
            "unknown carrier",
            lint('deliver(source="Atom", carrier="Missing")', [])[0],
        )
        self.assertEqual(lint('relation(source="Atom", name="*")', []), ())

    def test_cli_delivery_claim_checks_carrier(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            addresses, relations, claim = (
                root / name
                for name in ("addresses.json", "relations.json", "claim.py")
            )
            addresses.write_text(json.dumps(["Atom", "Carrier"]))
            relations.write_text("[]")
            claim.write_text('deliver(source="Atom", carrier="Carrier")')
            command = [
                sys.executable,
                "-B",
                str(TOOLS / "lint_python_model_claim__pub.py"),
                str(claim),
                "--addresses",
                str(addresses),
                "--relations",
                str(relations),
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            claim.write_text('deliver(source="Atom", carrier="Unknown")')
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown carrier", result.stderr)

    def test_registry_inverse_alias_must_reference_registered_relation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry, addresses, claim = (
                root / name
                for name in ("registry.json", "addresses.json", "claim.py")
            )
            addresses.write_text(json.dumps(["Atom"]))
            claim.write_text(
                'relation(source="Atom", name="IS_IN", target="Atom")'
            )
            command = [
                sys.executable,
                "-B",
                str(TOOLS / "lint_python_model_claim__pub.py"),
                str(claim),
                "--addresses",
                str(addresses),
                "--relations",
                str(registry),
            ]
            self._write_inverse_registry(registry, ["CONTAINS"], "CONTAINS")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self._write_inverse_registry(registry, [], "MISSING")
            self.assertEqual(
                subprocess.run(
                    command, capture_output=True, text=True
                ).returncode,
                2,
            )

    @staticmethod
    def _write_inverse_registry(registry, names, canonical):
        registry.write_text(
            json.dumps(
                {
                    "registered_names": names,
                    "inverse_aliases": [
                        {"alias": "IS_IN", "canonical": canonical}
                    ],
                }
            )
        )

    def test_rejects_unsafe_placement_folder(self):
        source = (
            "placement_rules = ({'kind': 'status', 'role': 'Plan', 'status': 'Backlog', "
            "'base': 'role', 'folder': '../Backlog'},)"
        )
        errors = lint_python_model_claim(
            source, declared_addresses=[], relation_names=[]
        )
        self.assertIn("Unsafe placement folder", errors[0])

    def test_python_is_never_executed(self):
        self.assertTrue(self.lint('__import__("os").system("exit 1")'))

    def test_cli_reads_markdown_formal_claim_and_relation_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            addresses = tmp / "addresses.json"
            relations = tmp / "relations.json"
            claim = tmp / "atom.md"
            addresses.write_text(json.dumps(["Atom"]))
            relations.write_text(json.dumps({"registered_names": ["KNOWN"]}))
            claim.write_text(
                (
                    "## Claim\n### Formal Claim\n```python\n"
                    'relation(source="Atom", name="MISSING")\n```\n'
                )
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOLS / "lint_python_model_claim__pub.py"),
                    str(claim),
                    "--addresses",
                    str(addresses),
                    "--relations",
                    str(relations),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn(f"{claim}:4:", result.stderr)
            self.assertIn("unknown Relation: MISSING", result.stderr)


if __name__ == "__main__":
    unittest.main()
