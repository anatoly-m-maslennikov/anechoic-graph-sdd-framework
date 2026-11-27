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

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import admit_active_model_records, compile_native_bindings
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.manifest_compiler_CS1__shared import (
    read_active_model_sources, render_atom_header_lean, verify_model_lean, write_model,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CURRENT_STATUSES
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import find_ontology_component


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
            variant = next((snapshot / custom).glob("AN-C-3194-*.md")).read_text()
            variant = variant.replace("AN-C-3194", "AN-C-99991").replace("Axiom", "Probe").replace("axiom", "probe")
            variant = variant.replace("relations:\n  IS_REPLACEMENT_FOR:\n  - AN-C-3193\n", "")
            variant = variant.replace("node.tier = value(fixed=0)", "node.tier = value(default=0)")
            node = snapshot / custom / "AN-C-99991-MANIFEST_NODE--declare-probe.md"
            node.write_text(variant, encoding="utf-8")
            status = snapshot / custom / "AN-C-99992-MANIFEST_PROPERTY--declare-probe-status.md"
            status.write_text("""---
atom_family: PROJECT_CONFIG
atom_id: AN-C-99992
container:
  component: C00
context:
  template: manifest_property
state:
  status: active
  version: 1
  updated_at: '2026-11-27T00:00:00Z'
concern:
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Probe.Header.State
  relation: is_property_of
  subject: Status
---

## Summary

Declare Probe Status

## Formal Manifest

```python anechoic-edsl
from anechoic.model import Atom, Property, Probe

class ProbeStatus(Property):
    name = 'Status'
    bearer = Atom.Header.State
    property.applies_to = (Probe,)
    property.value.allowed = ('draft', 'ready', 'active', 'archived', 'reviewed')
```
""", encoding="utf-8")
            current = snapshot / custom / "AN-C-99993-MANIFEST_PROPERTY--extend-ticket-status.md"
            extension = (status.read_text().replace("AN-C-99992", "AN-C-99993")
                         .replace("//Specification//Probe.Header.State", "//Ticket.Header.State")
                         .replace("Probe", "TicketAtom")
                         .replace("('draft', 'ready', 'active', 'archived', 'reviewed')", "('triage',)"))
            current.write_text(extension, encoding="utf-8")
            stage = root / "accepted"
            stage.mkdir()
            fingerprint = write_model(stage, snapshot)
            descriptor = stage / "model.json"
            accepted = descriptor.read_bytes()
            with open_admitted_model(stage, fingerprint, sha256(accepted).hexdigest()) as model:
                types = {cls.__name__: cls for cls in model._types.values()}
                probe = types["Probe"].__dataclass_fields__
                previous = types["Axiom"].__dataclass_fields__
                self.assertEqual(("probe",), probe["template"].metadata["allowed_values"])
                self.assertEqual(0, probe["tier"].default)
                self.assertEqual((0, True), model.project_spec_template("probe")[1:])
                self.assertIn("reviewed", probe["status"].metadata["allowed_values"])
                self.assertEqual(("axiom",), previous["template"].metadata["allowed_values"])
                self.assertNotIn("reviewed", previous["status"].metadata["allowed_values"])
                ticket = types["TicketAtom"].__dataclass_fields__["status"].metadata["allowed_values"]
                self.assertTrue({"draft", "backlog", "in_queue", "triage", "archived"} <= set(ticket))
            rejected = root / "rejected"
            rejected.mkdir()
            current.write_text(extension.replace("'triage'", "'archived'"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must add distinct Current Status"):
                write_model(rejected, snapshot)
            current.write_text(extension, encoding="utf-8")
            node.write_text(variant.replace("Lens.SPEC", "Lens.UNKNOWN"), encoding="utf-8")
            with self.assertRaises(ValueError):
                write_model(rejected, snapshot)
            self.assertEqual(accepted, descriptor.read_bytes())
            self.assertFalse((rejected / "model.json").exists())

    def test_project_contract_subtype_remains_valid_when_creation_is_disabled(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header

        control = Path(__file__).resolve().parents[8] / '_anechoic_anechoic'
        ontology = find_ontology_component(control)
        custom = Path('__PROJECT_CONFIG/CUSTOM_MODEL')
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            snapshot = root / 'snapshot'
            shutil.copytree(ontology, snapshot / ontology.relative_to(control))
            shutil.copytree(control / custom, snapshot / custom)
            variant = next((snapshot / custom).glob('AN-C-3194-*.md')).read_text()
            variant = variant.replace('AN-C-3194', 'AN-C-99991').replace('Axiom', 'Probe').replace('axiom', 'probe')
            variant = variant.replace('relations:\n  IS_REPLACEMENT_FOR:\n  - AN-C-3193\n', '')
            variant = variant.replace('//Specification//.Header.Context',
                                      '//Specification//Contract//Project Contract//.Header.Context')
            variant = variant.replace('Lens, Project, SpecAtom', 'Lens, ProjectContract')
            variant = variant.replace('class Probe(SpecAtom):', 'class Probe(ProjectContract):')
            variant = variant.replace('    node.container_type = value(fixed=Project)\n', '')
            variant = variant.replace('    node.tier =', '    node.creation_enabled = value(fixed=False)\n    node.tier =')
            (snapshot / custom / 'AN-C-99991-MANIFEST_NODE--declare-probe.md').write_text(variant)
            stage = root / 'model'
            stage.mkdir()
            fingerprint = write_model(stage, snapshot)
            digest = sha256((stage / 'model.json').read_bytes()).hexdigest()
            header = canonical_native_header({'identity': {'atom_id': 'AN-S-99991'},
                'context': {'container': {'component': 'C00'}, 'tier': 0, 'template': 'probe', 'lens': 'SPEC'},
                'state': {'status': 'draft', 'version': 1, 'updated_at': '2026-11-27T00:00:00+00:00'}})
            body = '\n## Summary\n\nProbe\n\n## Guarantee\n\nThe Project records the decision.\n'
            with open_admitted_model(stage, fingerprint, digest) as model:
                self.assertEqual((0, False), model.project_spec_template('probe')[1:])
                model.validate_project_spec('probe', header, 'C00', body)
                with self.assertRaises(ValueError):
                    model.validate_project_spec('probe', header, 'C00', '\n## Summary\n\nMissing Guarantee\n')
                with self.assertRaises(ValueError):
                    model.validate_project_spec('probe', header, 'C9', body)

    def test_active_model_checks_and_loads(self):
        root = Path(__file__).resolve().parents[8]
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
        control = Path(__file__).resolve().parents[8] / "_anechoic_anechoic"
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
        nodes = [
            (f"{name}.md", f"ANECHOIC_MODEL <+ {name}",
             "from anechoic.formal_claims import declare_entity\n"
             f"class {name}:\n    pass\n"
             f"declare_entity(entity_name='{name}', entity_class={name})")
            for name in ("Source", "Target")
        ]
        source = "links.md"
        relation = (
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='LINKS', "
            "source_endpoint={'level': 'instances', 'entity_paths': ('Source',)}, "
            "target_endpoint={'level': 'instances', 'entity_paths': ('Target',)})"
        )
        subject = "ANECHOIC_MODEL <+ Relation//LINKS"
        records = [*nodes, (source, subject, relation)]
        verify_model_lean(records, compile_native_bindings(records, {}))

        records[-1] = (source, subject, relation.replace("'Target'", "'MissingLeanEndpoint'"))
        duplicate = records[-1][2].replace("'LINKS'", "'OTHER_LINKS'")
        records.append(("other.md", "ANECHOIC_MODEL <+ Relation//OTHER_LINKS", duplicate))
        bindings = compile_native_bindings(records, {})
        with self.assertRaises(ValueError) as error:
            verify_model_lean(records, bindings)
        self.assertIn(f"{source}: unknown Relation endpoint MissingLeanEndpoint", str(error.exception))
        self.assertIn("Model.lean:", str(error.exception))
        self.assertEqual(1, str(error.exception).count("error:"))

if __name__ == "__main__":
    unittest.main()
