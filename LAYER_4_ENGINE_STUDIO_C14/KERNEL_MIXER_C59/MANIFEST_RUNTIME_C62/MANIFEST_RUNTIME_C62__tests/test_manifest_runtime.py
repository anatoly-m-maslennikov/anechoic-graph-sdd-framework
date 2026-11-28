"""Exercise the Kernel with the real compiler and source watcher."""

from unittest.mock import NonCallableMock

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.MANIFEST_RUNTIME_C62__shared \
    import run_manifest_runtime  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure__shared import (
    read_structure,
)

from .kernel_probe import (
    kernel_process,
    wait_ready,
)  # noqa: E402


from .manifest_runtime_fixtures import (
    _runtime_fixture,
    _runtime_observers,
    _tamper_recorder,
)
from .manifest_runtime_assertions import ManifestRuntimeAssertions


ROOT = Path(__file__).resolve().parents[4]
ENGINE = ROOT / "LAYER_4_ENGINE_STUDIO_C14"
PROGRAMMATIC = ENGINE / "FEATURE_PROGRAMMATIC"


class ManifestRuntimeTests(ManifestRuntimeAssertions, unittest.TestCase):
    def test_test_image_mode_controls_current_startup_compiler_wait(self):
        switch = "ANECHOIC_TEST_IMAGE_DEADLINES"
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.dict(os.environ, {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}),
        ):
            root = Path(temporary).resolve()
            control = root / "_anechoic"
            control.mkdir()
            selection = NonCallableMock(
                spec_set=[
                    "root",
                    "control_root",
                    "control_relative",
                    "manifest_sha256",
                ],
                root=root,
                control_root=control,
                control_relative=Path("_anechoic"),
                manifest_sha256="a" * 64,
            )
            result = subprocess.CompletedProcess(
                [], 1, stdout=b"", stderr=b"compiler failed"
            )
            orchestrator = NonCallableMock(
                spec_set=["run_worker"], run_worker=Mock(return_value=result)
            )
            os.environ.pop(switch, None)
            for setting, expected in ((None, 15), ("1", 15), ("0", None)):
                if setting is not None:
                    os.environ[switch] = setting
                with (
                    self.subTest(setting=setting),
                    self.assertRaisesRegex(RuntimeError, "compiler failed"),
                ):
                    with run_manifest_runtime(
                        selection, orchestrator=orchestrator
                    ):
                        self.fail("A failed compiler must not yield")
                self.assertEqual(
                    orchestrator.run_worker.call_args.kwargs["timeout"],
                    expected,
                )

    def test_startup_rejects_tampered_generation_before_yield(self):
        for target in ("descriptor", "module", "structure", "fingerprint"):
            with (
                self.subTest(target=target),
                tempfile.TemporaryDirectory() as temporary,
            ):
                root = Path(temporary).resolve()
                *_, selection = _runtime_fixture(root)
                generations = []
                record_process = _tamper_recorder(target, generations)

                with (
                    patch.dict(
                        "os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}
                    ),
                    patch.object(
                        subprocess, "Popen", side_effect=record_process
                    ),
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "model (descriptor |module )?hash mismatch|"
                        "components must be an object",
                    ):
                        with run_manifest_runtime(selection):
                            self.fail(
                                "A tampered generation must not be yielded"
                            )
                self.assertEqual(1, len(generations))
                self.assertFalse(generations[0].exists())

    def test_real_compiler_reloads_and_keeps_last_valid_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            control, ontology, component, original, model, selection = (
                _runtime_fixture(root)
            )
            failed, processes, builders, record_process = _runtime_observers()
            with (
                patch.dict(
                    "os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}
                ),
                patch.object(subprocess, "Popen", side_effect=record_process),
            ):
                with run_manifest_runtime(selection) as (
                    generation,
                    active,
                    bound_model,
                ):
                    descriptor = self._assert_generation(
                        generation, model, bound_model, builders, processes
                    )
                    self._assert_watcher_filter(control, builders)
                    failed.clear()
                    self._assert_refresh(
                        active,
                        control,
                        ontology,
                        component,
                        original,
                        failed,
                        descriptor,
                        generation,
                    )
                previous_builders = len(builders)
                with run_manifest_runtime(selection) as (
                    _,
                    active,
                    bound_model,
                ):
                    self.assertEqual(previous_builders + 1, len(builders))
                    self.assertEqual([], processes)
                    self.assertNotEqual(
                        descriptor["model_sha256"],
                        read_structure(active).model_sha256,
                    )

    def test_kernel_reports_worker_outcomes(self):
        with tempfile.TemporaryDirectory(
            prefix="c62-", dir="/tmp"
        ) as temporary:
            root = Path(temporary).resolve()
            _, _, component, original, _, selection = _runtime_fixture(root)
            environment = {
                **{**os.environ, "PYTHONPATH": str(ENGINE)},
                "ANECHOIC_RUNTIME_NAMESPACE": "docker",
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(
                    ROOT / ".anechoic_tmp/workbench/extensions"
                ),
            }
            with kernel_process(root, selection, environment) as (
                process,
                client,
                instance,
                log,
            ):
                wait_ready(process, client, log, root / "kernel.sock")
                self._assert_worker(
                    client, instance, "model_build", "completed"
                )
                (generation,) = (root / ".anechoic_tmp/manifest_runtime").glob(
                    "generation-*"
                )
                self._check_worker_changes(
                    client, instance, generation, component, original
                )

    def test_kernel_rejects_changed_binding(self):
        with tempfile.TemporaryDirectory(
            prefix="c62-", dir="/tmp"
        ) as temporary:
            root = Path(temporary).resolve()
            *_, selection = _runtime_fixture(root)
            with kernel_process(
                root,
                selection,
                {**os.environ, "PYTHONPATH": str(ENGINE)},
                digest="b" * 64,
            ) as (process, _, _, log):
                process.wait(timeout=30)
                log.seek(0)
                self.assertNotEqual(0, process.returncode)
                self.assertIn("Project binding changed", log.read())


if __name__ == "__main__":
    unittest.main()
