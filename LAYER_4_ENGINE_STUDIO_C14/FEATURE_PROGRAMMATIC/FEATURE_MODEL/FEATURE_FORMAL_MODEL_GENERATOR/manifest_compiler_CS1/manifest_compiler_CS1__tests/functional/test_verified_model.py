"""Verify the complete active Model before a local release is packaged."""

from hashlib import sha256
import json
from pathlib import Path
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest

from pydantic.dataclasses import is_pydantic_dataclass

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import admit_active_model_records, compile_native_bindings
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.manifest_compiler_CS1__shared import (
    read_active_model_sources, render_atom_header_lean, verify_model_lean, write_model,
)
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CURRENT_STATUSES
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import find_ontology_component


class VerifiedModelTests(unittest.TestCase):
    def test_active_model_checks_and_loads(self):
        root = Path(__file__).resolve().parents[7]
        control = root / "_anechoic_anechoic"
        ontology = find_ontology_component(control)
        self.assertTrue(ontology.is_dir(), "Active C9 Model is missing")
        selected = read_active_model_sources(control, ontology)
        self.assertTrue(any(source.startswith(f"{ontology.relative_to(control)}/") for source, _, _ in selected))
        self.assertTrue(any("PROJECT_CONFIG/" in source for source, _, _ in selected))
        with TemporaryDirectory() as directory:
            staged = Path(directory)
            fingerprint = write_model(staged, control, verify_lean=True)
            raw = (staged / "model.json").read_bytes()
            descriptor = json.loads(raw)
            self.assertEqual(descriptor["declarations"], [list(claim) for claim in selected])
            self.assertTrue(descriptor["bindings"]["declarations"])
            self.assertTrue(descriptor["class_modules"])
            with open_admitted_model(staged, fingerprint, sha256(raw).hexdigest()) as model:
                self.assertEqual({cls.__name__ for cls in model._types.values()}, set(descriptor["class_modules"]))
                self.assertTrue(all(is_pydantic_dataclass(cls) for cls in model._types.values()))
                types = {cls.__name__: cls for cls in model._types.values()}
                for name, marker in (("SpecAtom", "S"), ("ProjectConfigAtom", "C")):
                    declared = types[name].__dataclass_fields__["status"].metadata["allowed_values"]
                    self.assertEqual(set(declared), CURRENT_STATUSES[marker] | {"draft", "archived"})
                ticket_statuses = types["TicketAtom"].__dataclass_fields__["status"].metadata["allowed_values"]
                self.assertEqual(set(ticket_statuses), {
                    "draft", "backlog", "in_queue", "done", "canceled", "resolved", "complete", "archived",
                })
                project = model._validate("Project", {}, {})
                component = model._validate("Component", {}, {model._parent_relation: [project]})
                self.assertEqual(type(component).__name__, "Component")
                with self.assertRaises(ValueError):
                    model._validate("Component", {}, {model._parent_relation: [component, project]})

    def test_header_predicate_checks_observed_values(self):
        control = Path(__file__).resolve().parents[7] / "_anechoic_anechoic"
        selected = read_active_model_sources(control, find_ontology_component(control))
        records, originals, _ = admit_active_model_records(selected)
        bindings = compile_native_bindings(records, originals)
        program = render_atom_header_lean(records, bindings)
        program += """
def atomRoot := "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
def specRoot := atomRoot ++ "//Specification"
def ticketRoot := atomRoot ++ "//Ticket"
def header : AtomHeader := ⟨"SPEC", specRoot ++ "//Axiom", some (.text "active"), some (.integer 0), none⟩
example : atomHeaderValid header = true := by decide
example : atomHeaderValid {header with modelClass := specRoot, tier := some (.integer 1)} = true := by decide
example : atomHeaderValid {header with status := none} = false := by decide
example : atomHeaderValid {header with status := some .other} = false := by decide
example : atomHeaderValid {header with tier := none} = false := by decide
example : atomHeaderValid {header with tier := some (.integer 1)} = false := by decide
example : atomHeaderValid {header with family := "TKT", priority := none} = false := by decide
example : atomHeaderValid {header with family := "TKT", priority := some (.integer 2)} = false := by decide
example : atomHeaderValid {header with modelClass := specRoot ++ "//Unknown"} = false := by decide
example : atomHeaderValid {header with family := "TKT", modelClass := ticketRoot, priority := some (.integer 2)} = false := by decide
def ticket : AtomHeader := ⟨"TKT", ticketRoot, some (.text "in_queue"), none, some (.integer 2)⟩
example : atomHeaderValid ticket = true := by decide
example : atomHeaderValid {ticket with priority := none} = false := by decide
example : atomHeaderValid {ticket with status := some (.text "backlog")} = true := by decide
example : atomHeaderValid {ticket with status := some (.text "draft")} = true := by decide
example : atomHeaderValid {ticket with status := some (.text "archived")} = true := by decide
example : atomHeaderValid {ticket with status := some (.text "ready")} = false := by decide
example : atomHeaderValid {header with status := some (.text "backlog")} = false := by decide
example : atomHeaderValid {header with status := some (.text "unknown")} = false := by decide
example : atomHeaderValid {ticket with status := some (.text "unknown")} = false := by decide
def config : AtomHeader := ⟨"PROJECT_CONFIG", atomRoot ++ "//project_config", some (.text "active"), none, none⟩
example : atomHeaderStatusValid config = true := by decide
example : atomHeaderStatusValid {config with status := some (.text "draft")} = true := by decide
example : atomHeaderStatusValid {config with status := some (.text "archived")} = true := by decide
example : atomHeaderStatusValid {config with status := some (.text "ready")} = false := by decide
example : atomHeaderStatusValid {config with status := some (.text "unknown")} = false := by decide
example : atomHeaderValid {header with family := "OTHER"} = false := by decide
"""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "Header.lean"
            path.write_text(program, encoding="utf-8")
            result = subprocess.run([os.environ.get("LEAN_BIN") or shutil.which("lean") or "lean", str(path)], capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_lean_rejects_unknown_relation_endpoint_with_source(self):
        control = Path(__file__).resolve().parents[7] / "_anechoic_anechoic"
        selected = read_active_model_sources(control, find_ontology_component(control))
        records, originals, _ = admit_active_model_records(selected)
        bindings = compile_native_bindings(records, originals)
        subject, declaration = next((subject, declaration) for subject, declaration in bindings["declarations"]
                                    if declaration["kind"] == "relation" and declaration["arguments"].get("source_endpoint"))
        args = declaration["arguments"]
        args["source_endpoint"]["entity_paths"] = ("MissingLeanEndpoint",)
        for name, (catalog_args, reverse) in bindings["endpoints"].items():
            if catalog_args["relation_name"] == args["relation_name"]:
                bindings["endpoints"][name] = (args, reverse)
        source = next(source for source, claim_subject, _ in records if claim_subject == subject)
        with self.assertRaises(ValueError) as error:
            verify_model_lean(records, bindings)
        self.assertIn(source, str(error.exception))
        self.assertIn("unknown Relation endpoint MissingLeanEndpoint", str(error.exception))

if __name__ == "__main__":
    unittest.main()
