"""Manifest runtime assertion stages."""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure__shared import (
    read_structure,
)

from .manifest_runtime_fixtures import ADMITTED_MODEL_PROBE

ROOT = Path(__file__).resolve().parents[4]
ENGINE = ROOT / "LAYER_4_ENGINE_STUDIO_C14"


class ManifestRuntimeAssertions:
    def _assert_watcher_filter(self, control, builders):
        before = len(builders)
        path = control / "AN-S-2-DOM-COMPONENT_MANIFEST--component.md"
        path.write_text("---\ninvalid: [\n---\n")
        self._wait_for(lambda: len(builders) > before)
        self._wait_for(lambda: builders[-1].poll() is not None)
        before = len(builders)
        for name in (
            "01_draft",
            "02_ready",
            "09_archived",
            "000_draft",
            "099_archived",
        ):
            folder = control / name
            folder.mkdir(exist_ok=True)
            (
                folder / "AN-S-2-SPEC-COMPONENT_SEED_MANIFEST--seed.md"
            ).write_text("ignored")
        time.sleep(2.1)
        self.assertEqual(len(builders), before)

    def _wait_for(self, predicate):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(0.05)
        self.fail("Timed out waiting for a Structure update")

    def _assert_generation(
        self, generation, model, bound_model, builders, processes
    ):
        self.assertEqual(1, len(builders))
        self.assertEqual(0, builders[0].poll())
        self.assertEqual([], processes)
        descriptor = json.loads((generation / "model.json").read_text())
        self.assertNotEqual(model.fingerprint, descriptor["model_sha256"])
        self.assertEqual(bound_model.fingerprint, descriptor["model_sha256"])
        declared = {subject for _, subject, _ in descriptor["declarations"]}
        self.assertIn("MODEL//ANECHOIC <+ Node//Artifact//Atom", declared)
        self.assertEqual(len(declared), len(descriptor["declarations"]))
        module = (
            generation / "anechoic_runtime_model" / "component_manifest.py"
        )
        self.assertEqual(
            descriptor["modules"][module.name],
            hashlib.sha256(module.read_bytes()).hexdigest(),
        )
        subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                ADMITTED_MODEL_PROBE,
                bound_model.fingerprint,
                hashlib.sha256(
                    (generation / "model.json").read_bytes()
                ).hexdigest(),
            ],
            cwd=generation,
            env={**os.environ, "PYTHONPATH": str(ENGINE)},
            check=True,
        )
        return descriptor

    def _assert_worker(self, client, instance, kind, status):
        def matching():
            return any(
                run["kind"] == kind and run["status"] == status
                for run in client.get(
                    "/jobs/worker-runs", params={"instance_id": instance}
                ).json()["result"]["latest"]
            )

        self._wait_for(matching)
        runs = client.get(
            "/jobs/worker-runs", params={"instance_id": instance}
        ).json()["result"]["latest"]
        run = next(run for run in runs if run["kind"] == kind)
        self.assertTrue(run["id"])
        self.assertIsInstance(run["pid"], int)
        self.assertGreater(run["pid"], 0)
        self.assertEqual(status, run["status"])

    def _assert_refresh(
        self,
        active,
        control,
        ontology,
        component,
        original,
        failed,
        descriptor,
        generation,
    ):
        version, changed, valid = self._prepare_refresh(
            active, component, original, failed, generation
        )
        self._assert_refresh_recovery(
            active,
            control,
            ontology,
            component,
            descriptor,
            version,
            changed,
            valid,
        )

    def _prepare_refresh(
        self, active, component, original, failed, generation
    ):
        initial = read_structure(active)
        self.assertEqual("Engine Studio", initial.component("C14").name)
        version = int(initial.component("C14").ref.rsplit("@", 1)[1])
        changed = original.replace(
            f"version: {version}", f"version: {version + 1}", 1
        ).replace("Engine Studio", "Updated Studio")
        component.write_text(changed, encoding="utf-8")
        self._wait_for(
            lambda: (
                read_structure(active).component("C14").ref
                == f"AN-S-3039@{version + 1}"
            )
        )
        valid = read_structure(active)
        admitted_model = (generation / "model.json").read_bytes()
        self.assertEqual("Updated Studio", valid.component("C14").name)
        self.assertEqual("Engine Studio", initial.component("C14").name)
        self.assertEqual(f"AN-S-3039@{version}", initial.component("C14").ref)
        with self.assertRaises(TypeError):
            initial.components["C14"] = valid.component("C14")
        component.write_text(
            changed.replace("C14", "invalid"), encoding="utf-8"
        )
        self.assertTrue(failed.wait(15), "Invalid source was not compiled")
        self.assertEqual(valid, read_structure(active))
        self.assertEqual(
            admitted_model, (generation / "model.json").read_bytes()
        )
        return version, changed, valid

    def _assert_refresh_recovery(
        self,
        active,
        control,
        ontology,
        component,
        descriptor,
        version,
        changed,
        valid,
    ):
        component.write_text(
            changed.replace(
                f"version: {version + 1}", f"version: {version + 2}", 1
            ).replace("Updated Studio", "Recovered Studio"),
            encoding="utf-8",
        )
        self._wait_for(
            lambda: (
                read_structure(active).component("C14").ref
                == f"AN-S-3039@{version + 2}"
            )
        )
        self.assertEqual(
            "Recovered Studio", read_structure(active).component("C14").name
        )
        self.assertEqual("Updated Studio", valid.component("C14").name)
        self._assert_ontology_refresh(
            active, control, ontology, component, descriptor, version, changed
        )

    def _assert_ontology_refresh(
        self,
        active,
        control,
        ontology,
        component,
        descriptor,
        version,
        changed,
    ):
        claim = (
            control
            / ontology
            / "AN-S-3109-SPEC--declare-component-manifest.md"
        )
        revision = claim.read_text(encoding="utf-8")
        revised, count = re.subn(
            r"(?m)^  version: (\d+)$",
            lambda match: f"  version: {int(match[1]) + 1}",
            revision,
        )
        self.assertEqual(count, 1)
        claim.write_text(revised, encoding="utf-8")
        component.write_text(
            changed.replace(
                f"version: {version + 1}", f"version: {version + 3}", 1
            ),
            encoding="utf-8",
        )
        self._wait_for(
            lambda: (
                read_structure(active).component("C14").ref
                == f"AN-S-3039@{version + 3}"
            )
        )
        self.assertEqual(
            descriptor["model_sha256"], read_structure(active).model_sha256
        )

    def _check_worker_changes(
        self, client, instance, generation, component, original
    ):
        active = generation / "structure.json"
        initial = read_structure(active)
        version = int(initial.component("C14").ref.rsplit("@", 1)[1])
        revised = original.replace(
            f"version: {version}", f"version: {version + 1}", 1
        )
        component.write_text(revised, encoding="utf-8")
        self._wait_for(
            lambda: (
                read_structure(active)
                .component("C14")
                .ref.endswith(f"@{version + 1}")
            )
        )
        self._assert_worker(client, instance, "structure_refresh", "completed")
        self._check_worker_recovery(
            client,
            instance,
            generation,
            component,
            original,
            active,
            version,
            revised,
        )

    def _check_worker_recovery(
        self,
        client,
        instance,
        generation,
        component,
        original,
        active,
        version,
        revised,
    ):
        accepted = active.read_bytes()
        model = (generation / "model.json").read_bytes()
        component.write_text(
            revised.replace("C14", "invalid"), encoding="utf-8"
        )
        self._assert_worker(client, instance, "structure_refresh", "failed")
        self.assertEqual(accepted, active.read_bytes())
        self.assertEqual(model, (generation / "model.json").read_bytes())
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
        self._assert_worker(client, instance, "structure_refresh", "completed")
