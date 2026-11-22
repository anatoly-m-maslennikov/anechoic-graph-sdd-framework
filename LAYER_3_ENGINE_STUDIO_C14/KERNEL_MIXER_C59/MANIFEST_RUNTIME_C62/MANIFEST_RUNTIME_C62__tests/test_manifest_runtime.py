"""Exercise the Kernel with the real compiler and source watcher."""

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from threading import Event
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
NATIVE_CONTROL = ROOT.parent / "native-control"
if not NATIVE_CONTROL.is_dir():
    NATIVE_CONTROL = ROOT / "_anechoic_anechoic"
ENGINE = ROOT / "LAYER_3_ENGINE_STUDIO_C14"
PROGRAMMATIC = ENGINE / "FEATURE_PROGRAMMATIC"

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__pub import resolve_native_project  # noqa: E402
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62 import runtime  # noqa: E402
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__pub import reviewed_native_model  # noqa: E402
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_CS3.structure_host_CS3__pub import read_structure  # noqa: E402
from KERNEL_MIXER_C59.ORCHESTRATOR_C66.ORCHESTRATOR_C66__shared import Orchestrator  # noqa: E402


def _runtime_fixture(root):
    control = root / "_anechoic_anechoic"
    control.mkdir()
    source = NATIVE_CONTROL
    for name in ("AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md",
                 "AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md",
                 "AN-S-3040-SPEC-COMPONENT_MANIFEST--declare-meta-ontology.md"):
        shutil.copyfile(source / name, control / name)
    ontology = "LAYER_1_META_ONTOLOGY_C9"
    (control / ontology).mkdir()
    for declaration in (source / ontology).glob("AN-S-*-SPEC--*.md"):
        shutil.copyfile(declaration, control / ontology / declaration.name)
    component = control / "AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md"
    original = component.read_text(encoding="utf-8")
    model = reviewed_native_model()
    selection = resolve_native_project(
        root, control.name, validate_manifest=model.validate_manifest,
        require_atom_state=model.requires_atom_state,
        require_atom_header=model.requires_atom_header,
    )
    return control, ontology, component, original, model, selection


def _runtime_observers():
    failed = Event()
    real_compile = runtime._compile
    processes = []
    builders = []
    real_popen = subprocess.Popen

    def compile_checked(*args, **kwargs):
        try:
            return real_compile(*args, **kwargs)
        except RuntimeError:
            failed.set()
            raise

    def record_process(*args, **kwargs):
        process = real_popen(*args, **kwargs)
        command = args[0]
        if "-m" in command:
            module = command[command.index("-m") + 1]
            if module.endswith((".model_host_CS2.host", ".structure_host_CS3.host")):
                processes.append(process)
            if module == (
                "FEATURE_PROGRAMMATIC.FEATURE_MODEL."
                "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler"
            ):
                builders.append(process)
        return process

    return failed, processes, builders, compile_checked, record_process


class ManifestRuntimeTests(unittest.TestCase):
    def test_relevant_named_lens_and_revision_directories(self):
        control = Path(".anechoic_project")
        manifest = control / "AN-S-1-SPEC-PROJECT_MANIFEST--project.md"
        self.assertTrue(runtime._relevant(str(control / "AN-S-2-DOM-COMPONENT_MANIFEST--component.md"), control, manifest))
        for directory in ("01_draft", "02_ready", "09_archived", "000_draft", "099_archived"):
            self.assertFalse(runtime._relevant(str(control / directory / "AN-S-2-SPEC-COMPONENT_SEED_MANIFEST--seed.md"), control, manifest))

    def _wait_for(self, predicate):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(0.05)
        self.fail("Timed out waiting for a Structure update")


    def _assert_generation(self, generation, model, bound_model, builders, processes):
        self.assertEqual(1, len(builders))
        self.assertEqual(0, builders[0].poll())
        self.assertEqual([], processes)
        descriptor = json.loads((generation / "model.json").read_text())
        self.assertNotEqual(model.fingerprint, descriptor["model_sha256"])
        self.assertEqual(bound_model.fingerprint, descriptor["model_sha256"])
        declared = {subject for _, subject, _ in descriptor["declarations"]}
        self.assertIn("MODEL//ANECHOIC <+ Node//Artifact//Atom", declared)
        self.assertEqual(len(declared), len(descriptor["declarations"]))
        module = generation / "anechoic_runtime_model" / "component_manifest.py"
        self.assertEqual(descriptor["modules"][module.name], hashlib.sha256(module.read_bytes()).hexdigest())
        subprocess.run([sys.executable, "-c", """
from pathlib import Path
import sys
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_generation__pub import open_admitted_model
generation, fingerprint, digest = Path.cwd(), *sys.argv[1:]
with (open_admitted_model(generation, fingerprint, digest) as first,
      open_admitted_model(generation, fingerprint, digest) as second):
    assert {'Task', 'Subtask', 'Sub-epic', 'Epic', 'Version'} <= set(first.ticket_labels)
    assert first._types['Component Manifest'] is not second._types['Component Manifest']
assert not any('FEATURE_FORMAL_MODEL_GENERATOR' in name for name in sys.modules)
""", bound_model.fingerprint, hashlib.sha256((generation / "model.json").read_bytes()).hexdigest()],
            cwd=generation, env=runtime._environment(), check=True)
        return descriptor

    def _assert_worker(self, owner, kind, status):
        def matching():
            return any(run["kind"] == kind and run["status"] == status
                       for run in owner.worker_runs()["latest"])

        self._wait_for(matching)
        run = next(run for run in owner.worker_runs()["latest"] if run["kind"] == kind)
        self.assertTrue(run["id"])
        self.assertIsInstance(run["pid"], int)
        self.assertGreater(run["pid"], 0)
        self.assertEqual(status, run["status"])

    def _assert_refresh(self, active, control, ontology, component, original, failed, descriptor, owner, generation):
        initial = read_structure(active)
        self.assertEqual("Engine Studio", initial.component("C14").name)
        self.assertEqual("AN-S-3039@1", initial.component("C14").ref)
        changed = original.replace("version: 1", "version: 2").replace("Engine Studio", "Updated Studio")
        component.write_text(changed, encoding="utf-8")
        self._wait_for(lambda: read_structure(active).component("C14").ref == "AN-S-3039@2")
        self._assert_worker(owner, "structure_refresh", "completed")
        valid = read_structure(active)
        admitted_model = (generation / "model.json").read_bytes()
        self.assertEqual("Updated Studio", valid.component("C14").name)
        self.assertEqual("Engine Studio", initial.component("C14").name)
        self.assertEqual("AN-S-3039@1", initial.component("C14").ref)
        with self.assertRaises(TypeError):
            initial.components["C14"] = valid.component("C14")
        component.write_text(changed.replace("C14", "invalid"), encoding="utf-8")
        self.assertTrue(failed.wait(15), "Invalid source was not compiled")
        self._assert_worker(owner, "structure_refresh", "failed")
        self.assertEqual(valid, read_structure(active))
        self.assertEqual(admitted_model, (generation / "model.json").read_bytes())
        component.write_text(changed.replace("version: 2", "version: 3").replace(
            "Updated Studio", "Recovered Studio"), encoding="utf-8")
        self._wait_for(lambda: read_structure(active).component("C14").ref == "AN-S-3039@3")
        self.assertEqual("Recovered Studio", read_structure(active).component("C14").name)
        self.assertEqual("Updated Studio", valid.component("C14").name)
        claim = control / ontology / "AN-S-3109-SPEC--declare-component-manifest.md"
        revision = claim.read_text(encoding="utf-8")
        revised, count = re.subn(r"(?m)^  version: (\d+)$",
                                 lambda match: f"  version: {int(match[1]) + 1}", revision)
        self.assertEqual(count, 1)
        claim.write_text(revised, encoding="utf-8")
        component.write_text(changed.replace("version: 2", "version: 4"), encoding="utf-8")
        self._wait_for(lambda: read_structure(active).component("C14").ref == "AN-S-3039@4")
        self.assertEqual(descriptor["model_sha256"], read_structure(active).model_sha256)

    def test_startup_rejects_tampered_generation_before_yield(self):
        real_compile = runtime._compile
        for target in ("descriptor", "module", "structure", "fingerprint"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                *_, selection = _runtime_fixture(root)
                generations = []

                def tamper(*args, **kwargs):
                    compiled = real_compile(*args, **kwargs)
                    generation = args[1]
                    generations.append(generation)
                    if target in {"structure", "fingerprint"}:
                        result = json.loads(compiled)
                        if target == "structure":
                            result["structure"]["components"] = []
                        else:
                            result["structure"]["model_sha256"] = "b" * 64
                        return json.dumps(result).encode()
                    path = (generation / "model.json" if target == "descriptor" else
                            generation / "anechoic_runtime_model/component_manifest.py")
                    path.write_bytes(path.read_bytes() + b"\n")
                    return compiled

                with (patch.dict("os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}),
                      patch.object(runtime, "_compile", side_effect=tamper)):
                    with self.assertRaisesRegex(ValueError, "model (descriptor |module )?hash mismatch|components must be an object"):
                        with runtime.run_manifest_runtime(selection):
                            self.fail("A tampered generation must not be yielded")
                self.assertEqual(1, len(generations))
                self.assertFalse(generations[0].exists())

    def test_real_compiler_reloads_and_keeps_last_valid_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            control, ontology, component, original, model, selection = _runtime_fixture(root)
            failed, processes, builders, compile_checked, record_process = _runtime_observers()
            owner = Orchestrator()
            with (patch.dict("os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}),
                  patch.object(runtime, "_compile", side_effect=compile_checked),
                  patch.object(runtime.subprocess, "Popen", side_effect=record_process)):
                with runtime.run_manifest_runtime(selection, orchestrator=owner) as (generation, active, bound_model):
                    descriptor = self._assert_generation(generation, model, bound_model, builders, processes)
                    self._assert_worker(owner, "model_build", "completed")
                    self._assert_refresh(active, control, ontology, component, original, failed, descriptor, owner, generation)
                previous_builders = len(builders)
                with runtime.run_manifest_runtime(selection) as (_, active, bound_model):
                    self.assertEqual(previous_builders + 1, len(builders))
                    self.assertEqual([], processes)
                    self.assertNotEqual(descriptor["model_sha256"], read_structure(active).model_sha256)


if __name__ == "__main__":
    unittest.main()
