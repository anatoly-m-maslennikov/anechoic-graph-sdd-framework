"""Verify the Project Model build selects authority and stops before writing on failure."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import write_scope_unit_declarations


REPOSITORY = Path(__file__).resolve().parents[5]
MODULE = "FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.generate_model"


def model_carrier(identifier, subject, claim):
    return (f"---\natom_id: {identifier}\nrole: Requirement\nform: Declaration\n"
            f"status: Active\nversion: 1\nsubjects:\n  active: ANECHOIC_MODEL <+ {subject}\n"
            f"---\n## Claim\n### Formal Claim\n```python\n{claim}\n```\n")


def entity(name, parent=None):
    base = f"({parent})" if parent else ""
    imports = f"from anechoic.model import {parent}\n" if parent else ""
    return ("from anechoic.formal_claims import declare_entity\n" + imports
            + f"class {name}{base}:\n    pass\n"
            + f"declare_entity(entity_name='{name}', entity_class={name})")


class GenerateModelTests(unittest.TestCase):
    def test_real_build_errors_report_and_preserve_existing_model(self):
        relation = ("from anechoic.formal_claims import declare_relation\n"
                    "declare_relation(relation_name='LINKS', "
                    "source_endpoint={'level': 'instances', 'entity_paths': ('Atom',)}, "
                    "target_endpoint={'level': 'instances', 'entity_paths': ('Missing',)})")
        cases = (
            ("missing parent", [("Child", entity("Child", "Missing"))], "Missing Model parent"),
            ("inheritance cycle", [("Alpha", entity("Alpha", "Beta")),
                                   ("Beta", entity("Beta", "Alpha"))], "cycle"),
            ("unresolved endpoint", [("Atom", entity("Atom")), ("Relation//LINKS", relation)],
             "unknown Model address: Missing"),
            ("invalid Python", [("Atom", "declare_entity(")], "invalid native Python Claim"),
        )
        for label, declarations, expected in cases:
            with self.subTest(case=label), TemporaryDirectory() as directory:
                self._assert_real_failure(directory, declarations, expected)

    def _project(self, root, scopes=()):
        control = root / ".anechoic_test"
        control.mkdir()
        (control / "anechoic_project_settings.toml").write_text(
            '[project]\nname="TEST"\n[artifacts.identity]\nproject_prefix="CA"\n'
            '[paths]\ncontrol_root=".anechoic_test"\n', encoding="utf-8",
        )
        declarations = write_scope_unit_declarations(root, scopes, control_root=control)
        return control, declarations

    def _build(self, root, output):
        command = [sys.executable, "-B", "-m", MODULE, "--project-root", str(root), "--output", str(output)]
        return subprocess.run(command, cwd=REPOSITORY, capture_output=True, text=True, timeout=20)

    def _assert_real_failure(self, directory, declarations, expected):
        root = Path(directory).resolve()
        control, _ = self._project(root)
        requirements = control / "04_requirement"
        requirements.mkdir(exist_ok=True)
        valid = requirements / "CA-R-9-DECLARATION--fixture.md"
        valid.write_text(model_carrier("CA-R-9", "Atom", entity("Atom")), encoding="utf-8")
        output = root / "model.py"
        result = self._build(root, output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("class Atom", output.read_text(encoding="utf-8"))
        self.assertEqual(output.stat().st_mode & 0o777, 0o644)
        valid.unlink()
        for number, (subject, claim) in enumerate(declarations, start=1):
            identifier = f"CA-R-{number}"
            (requirements / f"{identifier}-DECLARATION--fixture.md").write_text(
                model_carrier(identifier, subject, claim), encoding="utf-8",
            )
        output.write_bytes(b"prior Model\n")
        result = self._build(root, output)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(expected.lower(), result.stderr.lower())
        self.assertEqual(output.read_bytes(), b"prior Model\n")

    def test_build_uses_declared_scope_sources(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            control, declarations = self._project(root, ({"scope_unit_name": "SCOPE"},))
            authority = declarations["SCOPE"]["authority_path"]
            for parent, name in ((authority, "Selected"), (control / "EXPORT", "Exported")):
                requirements = parent / "04_requirement"
                requirements.mkdir(parents=True)
                carrier = requirements / "CA-R-1-DECLARATION--fixture.md"
                carrier.write_text(model_carrier("CA-R-1", name, entity(name)), encoding="utf-8")
            output = root / "model.py"
            result = self._build(root, output)
            self.assertEqual(0, result.returncode, result.stderr)
            source = output.read_text(encoding="utf-8")
            self.assertIn("class Selected", source)
            self.assertNotIn("class Exported", source)
