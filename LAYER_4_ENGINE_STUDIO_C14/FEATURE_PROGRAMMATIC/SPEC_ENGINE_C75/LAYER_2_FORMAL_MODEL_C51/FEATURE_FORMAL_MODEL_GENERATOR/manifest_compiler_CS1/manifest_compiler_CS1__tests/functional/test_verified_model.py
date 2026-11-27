"""Verify the complete active Model before a local release is packaged."""

import json
import importlib.util
import os
import shutil
import subprocess
import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic.dataclasses import is_pydantic_dataclass

from importlib import import_module

_tools = "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
_formal = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
_generator = _formal + "FEATURE_FORMAL_MODEL_GENERATOR."
_adapters = import_module(_tools + "ADAPTERS_C30__shared")
_ontology = import_module(_tools + "model_ontology_path__pub")
_bindings = import_module(
    _generator + "FEATURE_FORMAL_MODEL_GENERATOR__shared"
)
_compiler = import_module(
    _generator + "manifest_compiler_CS1.manifest_compiler_CS1__shared"
)
_validation = import_module(
    _formal + "FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared"
)
CURRENT_STATUSES = _adapters.CURRENT_STATUSES
find_ontology_component = _ontology.find_ontology_component
admit_active_model_records = _bindings.admit_active_model_records
compile_native_bindings = _bindings.compile_native_bindings
read_active_model_sources = _compiler.read_active_model_sources
render_atom_header_lean = _compiler.render_atom_header_lean
verify_model_lean = _compiler.verify_model_lean
write_model = _compiler.write_model
open_admitted_model = _validation.open_admitted_model


_spec = importlib.util.spec_from_file_location(
    "_verified_model_fixtures",
    Path(__file__).with_name("_verified_model_fixtures.py"),
)
_fixtures = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixtures)
extension_fixture = _fixtures.extension_fixture
contract_fixture = _fixtures.contract_fixture
contract_header = _fixtures.contract_header


class VerifiedModelTests(unittest.TestCase):
    def test_project_config_extends_the_model(self):
        control = Path(__file__).resolve().parents[8] / "_anechoic_anechoic"
        ontology = find_ontology_component(control)
        custom = Path("__PROJECT_CONFIG/CUSTOM_MODEL")
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            snapshot = root / "spec"
            shutil.copytree(ontology, snapshot / ontology.relative_to(control))
            shutil.copytree(control / custom, snapshot / custom)
            variant, node, current, extension = extension_fixture(
                snapshot / custom
            )
            stage = root / "accepted"
            stage.mkdir()
            fingerprint = write_model(stage, snapshot)
            descriptor = stage / "model.json"
            accepted = descriptor.read_bytes()
            _fixtures.assert_project_extension(
                self, stage, fingerprint, accepted, open_admitted_model
            )
            rejected = root / "rejected"
            rejected.mkdir()
            current.write_text(
                extension.replace("'triage'", "'archived'"), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                ValueError, "must add distinct Current Status"
            ):
                write_model(rejected, snapshot)
            current.write_text(extension, encoding="utf-8")
            node.write_text(
                variant.replace("Lens.SPEC", "Lens.UNKNOWN"), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                write_model(rejected, snapshot)
            self.assertEqual(accepted, descriptor.read_bytes())
            self.assertFalse((rejected / "model.json").exists())

    def test_project_contract_subtype_remains_valid_when_creation_is_disabled(
        self,
    ):
        control = Path(__file__).resolve().parents[8] / "_anechoic_anechoic"
        ontology = find_ontology_component(control)
        custom = Path("__PROJECT_CONFIG/CUSTOM_MODEL")
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            snapshot = root / "snapshot"
            shutil.copytree(ontology, snapshot / ontology.relative_to(control))
            shutil.copytree(control / custom, snapshot / custom)
            contract_fixture(snapshot / custom)
            stage = root / "model"
            stage.mkdir()
            fingerprint = write_model(stage, snapshot)
            digest = sha256((stage / "model.json").read_bytes()).hexdigest()
            header, body = contract_header()
            with open_admitted_model(stage, fingerprint, digest) as model:
                self.assertEqual(
                    (0, False), model.project_spec_template("probe")[1:]
                )
                model.validate_project_spec("probe", header, "C00", body)
                with self.assertRaises(ValueError):
                    model.validate_project_spec(
                        "probe",
                        header,
                        "C00",
                        "\n## Summary\n\nMissing Guarantee\n",
                    )
                with self.assertRaises(ValueError):
                    model.validate_project_spec("probe", header, "C9", body)

    def assert_active_model(self, model, descriptor):
        self.assertEqual(
            {cls.__name__ for cls in model._types.values()},
            set(descriptor["class_modules"]),
        )
        self.assertTrue(
            all(is_pydantic_dataclass(cls) for cls in model._types.values())
        )
        types = {cls.__name__: cls for cls in model._types.values()}
        for name, marker in (
            ("SpecAtom", "S"),
            ("ProjectConfigAtom", "C"),
        ):
            declared = (
                types[name]
                .__dataclass_fields__["status"]
                .metadata["allowed_values"]
            )
            self.assertEqual(
                set(declared),
                CURRENT_STATUSES[marker] | {"draft", "archived"},
            )
        self.assert_ticket_and_parent(model, types)

    def assert_ticket_and_parent(self, model, types):
        ticket_statuses = (
            types["TicketAtom"]
            .__dataclass_fields__["status"]
            .metadata["allowed_values"]
        )
        self.assertEqual(
            set(ticket_statuses),
            {
                "draft",
                "backlog",
                "in_queue",
                "done",
                "canceled",
                "resolved",
                "complete",
                "archived",
            },
        )
        project = model._validate("Project", {}, {})
        component = model._validate(
            "Component", {}, {model._parent_relation: [project]}
        )
        self.assertEqual(type(component).__name__, "Component")
        with self.assertRaises(ValueError):
            model._validate(
                "Component",
                {},
                {model._parent_relation: [component, project]},
            )

    def test_active_model_checks_and_loads(self):
        root = Path(__file__).resolve().parents[8]
        control = root / "_anechoic_anechoic"
        ontology = find_ontology_component(control)
        self.assertTrue(ontology.is_dir(), "Active C9 Model is missing")
        selected = read_active_model_sources(control, ontology)
        self.assertTrue(
            any(
                source.startswith(f"{ontology.relative_to(control)}/")
                for source, _, _ in selected
            )
        )
        self.assertTrue(
            any("PROJECT_CONFIG/" in source for source, _, _ in selected)
        )
        with TemporaryDirectory() as directory:
            staged = Path(directory)
            fingerprint = write_model(staged, control, verify_lean=True)
            raw = (staged / "model.json").read_bytes()
            descriptor = json.loads(raw)
            self.assertEqual(
                descriptor["declarations"], [list(claim) for claim in selected]
            )
            self.assertTrue(descriptor["bindings"]["declarations"])
            self.assertTrue(descriptor["class_modules"])
            with open_admitted_model(
                staged, fingerprint, sha256(raw).hexdigest()
            ) as model:
                self.assert_active_model(model, descriptor)

    def test_header_predicate_checks_observed_values(self):
        control = Path(__file__).resolve().parents[8] / "_anechoic_anechoic"
        selected = read_active_model_sources(
            control, find_ontology_component(control)
        )
        records, originals, _ = admit_active_model_records(selected)
        bindings = compile_native_bindings(records, originals)
        program = render_atom_header_lean(records, bindings)
        program += _fixtures.HEADER_CHECKS
        with TemporaryDirectory() as directory:
            path = Path(directory) / "Header.lean"
            path.write_text(program, encoding="utf-8")
            result = subprocess.run(
                [
                    os.environ.get("LEAN_BIN")
                    or shutil.which("lean")
                    or "lean",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            self.assertEqual(
                result.returncode, 0, result.stdout + result.stderr
            )

    def test_lean_rejects_unknown_relation_endpoint_with_source(self):
        nodes = [
            (
                f"{name}.md",
                f"ANECHOIC_MODEL <+ {name}",
                (
                    "from anechoic.formal_claims import declare_entity\n"
                    f"class {name}:\n    pass\n"
                    f"declare_entity(entity_name='{name}', "
                    f"entity_class={name})"
                ),
            )
            for name in ("Source", "Target")
        ]
        source = "links.md"
        relation = (
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='LINKS', "
            "source_endpoint={'level': 'instances', "
            "'entity_paths': ('Source',)}, "
            "target_endpoint={'level': 'instances', "
            "'entity_paths': ('Target',)})"
        )
        subject = "ANECHOIC_MODEL <+ Relation//LINKS"
        records = [*nodes, (source, subject, relation)]
        verify_model_lean(records, compile_native_bindings(records, {}))

        records[-1] = (
            source,
            subject,
            relation.replace("'Target'", "'MissingLeanEndpoint'"),
        )
        duplicate = records[-1][2].replace("'LINKS'", "'OTHER_LINKS'")
        records.append(
            ("other.md", "ANECHOIC_MODEL <+ Relation//OTHER_LINKS", duplicate)
        )
        bindings = compile_native_bindings(records, {})
        with self.assertRaises(ValueError) as error:
            verify_model_lean(records, bindings)
        self.assertIn(
            f"{source}: unknown Relation endpoint MissingLeanEndpoint",
            str(error.exception),
        )
        self.assertIn("Model.lean:", str(error.exception))
        self.assertEqual(1, str(error.exception).count("error:"))


if __name__ == "__main__":
    unittest.main()
