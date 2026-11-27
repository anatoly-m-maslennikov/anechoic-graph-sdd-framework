"""Exercise the Kernel with the real compiler and source watcher."""
from unittest.mock import NonCallableMock

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from threading import Event
import time
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[4]
ENGINE = ROOT / "LAYER_4_ENGINE_STUDIO_C14"
PROGRAMMATIC = ENGINE / "FEATURE_PROGRAMMATIC"

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import resolve_native_project  # noqa: E402
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.MANIFEST_RUNTIME_C62__shared import run_manifest_runtime  # noqa: E402
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__shared import reviewed_native_model  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_structure  # noqa: E402
from .kernel_probe import kernel_process, wait_ready, write_reviewed_declarations  # noqa: E402


def _runtime_fixture(root):
    control = root / "_anechoic_anechoic"
    source = ROOT / control.name
    owner = Path("ONTOLOGY_SCORE_C82")
    ontology = owner / "CONTINUANT_PITCHFORK_C9"
    component = Path("01_TIER_1_ARCHITECTURE/AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md")
    meta = owner / "01_TIER_1_ARCHITECTURE/AN-S-3040-SPEC-COMPONENT_MANIFEST--declare-meta-ontology.md"
    shutil.copyfile(ROOT / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md",
                    root / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md")
    for relative in (component, Path("01_TIER_1_ARCHITECTURE/AN-S-4909-SPEC-COMPONENT_MANIFEST--declare-ontology-score.md"), meta):
        destination = control / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, destination)
    write_reviewed_declarations(control, ROOT)
    (control / "LAYER_1_META_ONTOLOGY_C9").rename(control / ontology)
    meta = control / meta
    meta.write_text(meta.read_text(encoding="utf-8").replace(
        "relations:\n  CONTRIBUTES_TO:\n  - AN-S-3328\n", ""), encoding="utf-8")
    component = control / component
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
    processes = []
    builders = []
    real_popen = subprocess.Popen

    def record_process(*args, **kwargs):
        process = real_popen(*args, **kwargs)
        command = args[0]
        if "-m" in command:
            module = command[command.index("-m") + 1]
            if module.endswith((".model_host_CS2.host", ".structure_host_CS3.host")):
                processes.append(process)
            if module == (
                "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub"
            ):
                builders.append(process)
                communicate = process.communicate

                def tracked_communicate(*args, **kwargs):
                    result = communicate(*args, **kwargs)
                    if process.returncode:
                        failed.set()
                    return result

                process.communicate = tracked_communicate
        return process

    return failed, processes, builders, record_process


class ManifestRuntimeTests(unittest.TestCase):
    def test_test_image_mode_controls_current_startup_compiler_wait(self):
        switch = "ANECHOIC_TEST_IMAGE_DEADLINES"
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}):
            root = Path(temporary).resolve()
            control = root / "_anechoic"
            control.mkdir()
            selection = NonCallableMock(
                spec_set=[
                    'root', 'control_root', 'control_relative',
                    'manifest_sha256'
                ],
                root=root, control_root=control,
                control_relative=Path("_anechoic"),
                manifest_sha256="a" * 64,
            )
            result = subprocess.CompletedProcess([], 1, stdout=b"", stderr=b"compiler failed")
            orchestrator = NonCallableMock(
                spec_set=[
                    'run_worker'
                ],
                run_worker=Mock(return_value=result))
            os.environ.pop(switch, None)
            for setting, expected in ((None, 15), ("1", 15), ("0", None)):
                if setting is not None:
                    os.environ[switch] = setting
                with self.subTest(setting=setting), self.assertRaisesRegex(RuntimeError, "compiler failed"):
                    with run_manifest_runtime(selection, orchestrator=orchestrator):
                        self.fail("A failed compiler must not yield")
                self.assertEqual(orchestrator.run_worker.call_args.kwargs["timeout"], expected)

    def _assert_watcher_filter(self, control, builders):
        before = len(builders)
        path = control / "AN-S-2-DOM-COMPONENT_MANIFEST--component.md"
        path.write_text("---\ninvalid: [\n---\n")
        self._wait_for(lambda: len(builders) > before)
        self._wait_for(lambda: builders[-1].poll() is not None)
        before = len(builders)
        for name in ("01_draft", "02_ready", "09_archived", "000_draft", "099_archived"):
            folder = control / name
            folder.mkdir(exist_ok=True)
            (folder / "AN-S-2-SPEC-COMPONENT_SEED_MANIFEST--seed.md").write_text("ignored")
        time.sleep(2.1)
        self.assertEqual(len(builders), before)

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
        subprocess.run([sys.executable, "-B", "-c", """
from pathlib import Path
import sys
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model
generation, fingerprint, digest = Path.cwd(), *sys.argv[1:]
with (open_admitted_model(generation, fingerprint, digest) as first,
      open_admitted_model(generation, fingerprint, digest) as second):
    assert {'Task', 'Subtask', 'Sub-epic', 'Epic', 'Version'} <= set(first.ticket_labels)
    assert first._types['Component Manifest'] is not second._types['Component Manifest']
assert not any('FEATURE_FORMAL_MODEL_GENERATOR' in name for name in sys.modules)
""", bound_model.fingerprint, hashlib.sha256((generation / "model.json").read_bytes()).hexdigest()],
            cwd=generation, env={**os.environ, "PYTHONPATH": str(ENGINE)}, check=True)
        return descriptor

    def _assert_worker(self, client, instance, kind, status):
        def matching():
            return any(run["kind"] == kind and run["status"] == status
                       for run in client.get("/jobs/worker-runs", params={"instance_id": instance}).json()["result"]["latest"])

        self._wait_for(matching)
        runs = client.get("/jobs/worker-runs", params={"instance_id": instance}).json()["result"]["latest"]
        run = next(run for run in runs if run["kind"] == kind)
        self.assertTrue(run["id"])
        self.assertIsInstance(run["pid"], int)
        self.assertGreater(run["pid"], 0)
        self.assertEqual(status, run["status"])

    def _assert_refresh(self, active, control, ontology, component, original, failed, descriptor, generation):
        initial = read_structure(active)
        self.assertEqual("Engine Studio", initial.component("C14").name)
        version = int(initial.component("C14").ref.rsplit("@", 1)[1])
        changed = original.replace(f"version: {version}", f"version: {version + 1}", 1).replace("Engine Studio", "Updated Studio")
        component.write_text(changed, encoding="utf-8")
        self._wait_for(lambda: read_structure(active).component("C14").ref == f"AN-S-3039@{version + 1}")
        valid = read_structure(active)
        admitted_model = (generation / "model.json").read_bytes()
        self.assertEqual("Updated Studio", valid.component("C14").name)
        self.assertEqual("Engine Studio", initial.component("C14").name)
        self.assertEqual(f"AN-S-3039@{version}", initial.component("C14").ref)
        with self.assertRaises(TypeError):
            initial.components["C14"] = valid.component("C14")
        component.write_text(changed.replace("C14", "invalid"), encoding="utf-8")
        self.assertTrue(failed.wait(15), "Invalid source was not compiled")
        self.assertEqual(valid, read_structure(active))
        self.assertEqual(admitted_model, (generation / "model.json").read_bytes())
        component.write_text(changed.replace(f"version: {version + 1}", f"version: {version + 2}", 1).replace(
            "Updated Studio", "Recovered Studio"), encoding="utf-8")
        self._wait_for(lambda: read_structure(active).component("C14").ref == f"AN-S-3039@{version + 2}")
        self.assertEqual("Recovered Studio", read_structure(active).component("C14").name)
        self.assertEqual("Updated Studio", valid.component("C14").name)
        claim = control / ontology / "AN-S-3109-SPEC--declare-component-manifest.md"
        revision = claim.read_text(encoding="utf-8")
        revised, count = re.subn(r"(?m)^  version: (\d+)$",
                                 lambda match: f"  version: {int(match[1]) + 1}", revision)
        self.assertEqual(count, 1)
        claim.write_text(revised, encoding="utf-8")
        component.write_text(changed.replace(f"version: {version + 1}", f"version: {version + 3}", 1), encoding="utf-8")
        self._wait_for(lambda: read_structure(active).component("C14").ref == f"AN-S-3039@{version + 3}")
        self.assertEqual(descriptor["model_sha256"], read_structure(active).model_sha256)

    def test_startup_rejects_tampered_generation_before_yield(self):
        for target in ("descriptor", "module", "structure", "fingerprint"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                *_, selection = _runtime_fixture(root)
                generations = []
                real_popen = subprocess.Popen

                def record_process(*args, _popen=real_popen, _generations=generations,
                                   _target=target, **kwargs):
                    process = _popen(*args, **kwargs)
                    command = args[0]
                    if "--build-model" not in command:
                        return process
                    generation = Path(command[command.index("--build-model") - 1])
                    _generations.append(generation)
                    communicate = process.communicate

                    def tamper(*args, bound_target=_target, **kwargs):
                        stdout, stderr = communicate(*args, **kwargs)
                        if bound_target in {"structure", "fingerprint"}:
                            result = json.loads(stdout)
                            if bound_target == "structure":
                                result["structure"]["components"] = []
                            else:
                                result["structure"]["model_sha256"] = "b" * 64
                            return json.dumps(result).encode(), stderr
                        path = (generation / "model.json" if bound_target == "descriptor" else
                                generation / "anechoic_runtime_model/component_manifest.py")
                        path.write_bytes(path.read_bytes() + b"\n")
                        return stdout, stderr

                    process.communicate = tamper
                    return process

                with (patch.dict("os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}),
                      patch.object(subprocess, "Popen", side_effect=record_process)):
                    with self.assertRaisesRegex(ValueError, "model (descriptor |module )?hash mismatch|components must be an object"):
                        with run_manifest_runtime(selection):
                            self.fail("A tampered generation must not be yielded")
                self.assertEqual(1, len(generations))
                self.assertFalse(generations[0].exists())

    def test_real_compiler_reloads_and_keeps_last_valid_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            control, ontology, component, original, model, selection = _runtime_fixture(root)
            failed, processes, builders, record_process = _runtime_observers()
            with (patch.dict("os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}),
                  patch.object(subprocess, "Popen", side_effect=record_process)):
                with run_manifest_runtime(selection) as (generation, active, bound_model):
                    descriptor = self._assert_generation(generation, model, bound_model, builders, processes)
                    self._assert_watcher_filter(control, builders)
                    failed.clear()
                    self._assert_refresh(active, control, ontology, component, original, failed, descriptor, generation)
                previous_builders = len(builders)
                with run_manifest_runtime(selection) as (_, active, bound_model):
                    self.assertEqual(previous_builders + 1, len(builders))
                    self.assertEqual([], processes)
                    self.assertNotEqual(descriptor["model_sha256"], read_structure(active).model_sha256)

    def test_kernel_reports_worker_outcomes(self):
        with tempfile.TemporaryDirectory(prefix="c62-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            _, _, component, original, _, selection = _runtime_fixture(root)
            environment = {**{**os.environ, "PYTHONPATH": str(ENGINE)}, "ANECHOIC_RUNTIME_NAMESPACE": "docker",
                           "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(ROOT / ".anechoic_tmp/workbench/extensions")}
            with kernel_process(root, selection, environment) as (process, client, instance, log):
                wait_ready(process, client, log, root / "kernel.sock")
                self._assert_worker(client, instance, "model_build", "completed")
                generation, = (root / ".anechoic_tmp/manifest_runtime").glob("generation-*")
                active = generation / "structure.json"
                initial = read_structure(active)
                version = int(initial.component("C14").ref.rsplit("@", 1)[1])
                revised = original.replace(f"version: {version}", f"version: {version + 1}", 1)
                component.write_text(revised, encoding="utf-8")
                self._wait_for(lambda: read_structure(active).component("C14").ref.endswith(f"@{version + 1}"))
                self._assert_worker(client, instance, "structure_refresh", "completed")
                accepted = active.read_bytes()
                model = (generation / "model.json").read_bytes()
                component.write_text(revised.replace("C14", "invalid"), encoding="utf-8")
                self._assert_worker(client, instance, "structure_refresh", "failed")
                self.assertEqual(accepted, active.read_bytes())
                self.assertEqual(
                    model, (generation / "model.json").read_bytes()
                )
                component.write_text(
                    original.replace(
                        f"version: {version}", f"version: {version + 2}", 1
                    ),
                    encoding="utf-8",
                )
                self._wait_for(
                    lambda: (
                        read_structure(active)
                        .component("C14")
                        .ref.endswith(f"@{version + 2}")
                    )
                )
                self._assert_worker(
                    client, instance, "structure_refresh", "completed"
                )

    def test_kernel_rejects_changed_binding(self):
        with tempfile.TemporaryDirectory(prefix="c62-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            *_, selection = _runtime_fixture(root)
            with kernel_process(root, selection, {**os.environ, "PYTHONPATH": str(ENGINE)}, digest="b" * 64) as (process, _, _, log):
                process.wait(timeout=30)
                log.seek(0)
                self.assertNotEqual(0, process.returncode)
                self.assertIn("Project binding changed", log.read())


if __name__ == "__main__":
    unittest.main()
