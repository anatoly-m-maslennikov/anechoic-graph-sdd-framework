"""Verify the Project Model build selects authority and stops before writing on failure."""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR import generate_model
from scope_declaration_test_support import write_scope_unit_declarations


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
                root = Path(directory).resolve()
                control = root / ".anechoic_test"
                control.mkdir()
                (control / "anechoic_project_settings.toml").write_text(
                    '[project]\nname="TEST"\n[artifacts.identity]\nproject_prefix="CA"\n'
                    '[paths]\ncontrol_root=".anechoic_test"\n', encoding="utf-8",
                )
                write_scope_unit_declarations(root, control_root=control)
                requirements = control / "04_requirement"
                requirements.mkdir(exist_ok=True)
                valid = requirements / "CA-R-9-DECLARATION--fixture.md"
                valid.write_text(model_carrier("CA-R-9", "Atom", entity("Atom")), encoding="utf-8")
                output = root / "model.py"
                self.assertEqual(generate_model.main(["--project-root", str(root), "--output", str(output)]), 0)
                self.assertIn("class Atom", output.read_text(encoding="utf-8"))
                self.assertEqual(output.stat().st_mode & 0o777, 0o644)
                valid.unlink()
                for number, (subject, claim) in enumerate(declarations, start=1):
                    identifier = f"CA-R-{number}"
                    (requirements / f"{identifier}-DECLARATION--fixture.md").write_text(
                        model_carrier(identifier, subject, claim), encoding="utf-8",
                    )
                output.write_bytes(b"prior Model\n")
                stderr = StringIO()
                with redirect_stderr(stderr):
                    result = generate_model.main(["--project-root", str(root), "--output", str(output)])
                self.assertEqual(result, 1)
                self.assertIn(expected.lower(), stderr.getvalue().lower())
                self.assertEqual(output.read_bytes(), b"prior Model\n")

    def test_build_uses_declared_scope_sources(self):
        root = Path("/project")
        authority = Path(".anechoic_project/SCOPE")
        selection = SimpleNamespace(
            root=root, control_root=root / authority.parent,
            structure={"scope_units": [{"authority_path": str(authority)}]},
        )
        selected = {"source": {"path": str(authority / "04_requirement/CA-R-1.md")}}
        copy = {"source": {"path": ".anechoic_project/EXPORT/04_requirement/CA-R-1.md"}}

        def read_sources(_control, project, *, include_source):
            return [row for row in (copy, selected) if include_source(project / row["source"]["path"])]

        with (
            patch.object(generate_model, "resolve_project", return_value=selection),
            patch.object(generate_model, "read_current_model_carriers", side_effect=read_sources),
            patch.object(generate_model, "build_model_class_source", side_effect=lambda rows: tuple(rows)),
        ):
            self.assertEqual(generate_model.build_project_model(root), (selected,))

    def test_failed_build_leaves_existing_output_intact(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "model.py"
            output.write_text("prior Model", encoding="utf-8")
            stderr = StringIO()
            with (
                patch.object(generate_model, "build_project_model", side_effect=ValueError("missing parent")),
                redirect_stderr(stderr),
            ):
                self.assertEqual(generate_model.main(["--project-root", directory, "--output", str(output)]), 1)
            self.assertEqual(output.read_text(encoding="utf-8"), "prior Model")
            self.assertIn("missing parent", stderr.getvalue())
