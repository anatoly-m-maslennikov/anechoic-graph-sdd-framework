"""Exercise the supervisor with the real compiler, hosts, and source watcher."""

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
sys.path[:0] = [str(ROOT), str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS"),
                str(ENGINE / "IWE_CONSOLE_C43")]

from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import load_native_model  # noqa: E402
from native_project_selection import resolve_native_project  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62 import runtime  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import read_structure  # noqa: E402


class ManifestRuntimeTests(unittest.TestCase):
    def test_unresponsive_host_retains_published_snapshot(self):
        with (tempfile.TemporaryDirectory() as temporary,
              subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE) as host,
              patch.object(runtime, "_TIMEOUT", 0.1)):
            active = Path(temporary) / "structure.json"
            active.write_bytes(b"last good")
            with self.assertRaisesRegex(RuntimeError, "did not respond"):
                runtime._publish(host, active, b"x" * (1024 * 1024))
            self.assertNotEqual(host.wait(timeout=1), 0)
            self.assertEqual(active.read_bytes(), b"last good")

    def test_real_hosts_reload_and_keep_last_valid_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
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
            model = load_native_model()
            selection = resolve_native_project(root, control.name, validate_manifest=model.validate_manifest)
            failed = Event()
            real_compile = runtime._compile
            processes = []
            real_popen = subprocess.Popen

            def compile_checked(*args, **kwargs):
                try:
                    return real_compile(*args, **kwargs)
                except RuntimeError:
                    failed.set()
                    raise

            def record_process(*args, **kwargs):
                process = real_popen(*args, **kwargs)
                if any("_host_pkg" in str(arg) for arg in args[0]):
                    processes.append(process)
                return process

            def wait_for(predicate):
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    if predicate():
                        return
                    time.sleep(0.05)
                self.fail("Timed out waiting for a Structure update")

            with (patch.dict("os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}),
                  patch.object(runtime, "_compile", side_effect=compile_checked),
                  patch.object(runtime.subprocess, "Popen", side_effect=record_process)):
                with runtime.run_manifest_runtime(selection) as (generation, active):
                    self.assertEqual(2, len(processes))
                    self.assertNotEqual(processes[0].pid, processes[1].pid)
                    self.assertTrue(all(process.poll() is None for process in processes))
                    descriptor = json.loads((generation / "model.json").read_text())
                    self.assertNotEqual(model.fingerprint, descriptor["model_sha256"])
                    declared = {subject for _, subject, _ in descriptor["declarations"]}
                    self.assertIn("MODEL//ANECHOIC <+ Node//Artifact//Atom", declared)
                    self.assertEqual(len(declared), len(descriptor["declarations"]))
                    module = generation / "anechoic_runtime_model" / "component_manifest.py"
                    self.assertEqual(descriptor["modules"][module.name], hashlib.sha256(module.read_bytes()).hexdigest())
                    subprocess.run([sys.executable, "-c", """
from pathlib import Path
from anechoic_runtime_model.component_manifest import ComponentManifest
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.compiler import load_generation_model
assert ComponentManifest.__name__ == 'ComponentManifest'
model = load_generation_model(Path.cwd())
assert {'Task', 'Subtask', 'Sub-epic', 'Epic', 'Version'} <= set(model.ticket_labels)
"""], cwd=generation, env=runtime._environment(), check=True)
                    initial = read_structure(active)
                    self.assertEqual("Engine Studio", initial.component("C14").name)
                    self.assertEqual("AN-S-3039@1", initial.component("C14").ref)
                    changed = original.replace("version: 1", "version: 2").replace("Engine Studio", "Updated Studio")
                    component.write_text(changed, encoding="utf-8")
                    wait_for(lambda: read_structure(active).component("C14").ref == "AN-S-3039@2")
                    valid = read_structure(active)
                    self.assertEqual("Updated Studio", valid.component("C14").name)
                    self.assertEqual("Engine Studio", initial.component("C14").name)
                    self.assertEqual("AN-S-3039@1", initial.component("C14").ref)
                    with self.assertRaises(TypeError):
                        initial.components["C14"] = valid.component("C14")
                    component.write_text(changed.replace("C14", "invalid"), encoding="utf-8")
                    self.assertTrue(failed.wait(15), "Invalid source was not compiled")
                    self.assertEqual(valid, read_structure(active))
                    component.write_text(changed.replace("version: 2", "version: 3").replace(
                        "Updated Studio", "Recovered Studio"), encoding="utf-8")
                    wait_for(lambda: read_structure(active).component("C14").ref == "AN-S-3039@3")
                    self.assertEqual("Recovered Studio", read_structure(active).component("C14").name)
                    self.assertEqual("Updated Studio", valid.component("C14").name)
                    claim = control / ontology / "AN-S-3109-SPEC--declare-component-manifest.md"
                    revision = claim.read_text(encoding="utf-8")
                    revised, count = re.subn(r"(?m)^  version: (\d+)$",
                                             lambda match: f"  version: {int(match[1]) + 1}", revision)
                    self.assertEqual(count, 1)
                    claim.write_text(revised, encoding="utf-8")
                    component.write_text(changed.replace("version: 2", "version: 4"), encoding="utf-8")
                    wait_for(lambda: read_structure(active).component("C14").ref == "AN-S-3039@4")
                    self.assertEqual(descriptor["model_sha256"], read_structure(active).model_sha256)
                self.assertTrue(all(process.poll() is not None for process in processes))
                with runtime.run_manifest_runtime(selection) as (_, active):
                    self.assertEqual(4, len(processes))
                    self.assertNotEqual(descriptor["model_sha256"], read_structure(active).model_sha256)


if __name__ == "__main__":
    unittest.main()
