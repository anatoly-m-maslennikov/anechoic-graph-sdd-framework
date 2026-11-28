"""Temporary Local Release resume fixtures and cases."""

import json
import os
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63 import (
    local_release_package_phases as package_phases,
)


class LocalReleaseResumeCases2:
    def test_resume_reuses_static_after_functional_failure_and_keeps_version(
        self,
    ):
        runner, calls = self._runner()
        failed = self.release(
            self.failed_gate(runner, "functional"), image_mode="existing"
        )
        self.assertEqual(
            ("failed", "functional_tests"),
            (failed["outcome"], failed["failed_step"]),
            failed,
        )
        self.assertEqual(
            ["preflight", "static", "functional"], self.gates(calls)
        )
        self.start_container.assert_not_called()
        self.image_factory.assert_not_called()
        version = (self.root / "version.toml").read_text()

        runner, calls = self._runner()
        result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("existing", result["image_mode"])
        self.assertEqual(
            ["functional", "image-tests", "canary"], self.gates(calls)
        )
        self.assert_same_candidate_version(version)
        self.start_container.assert_called_once()

    def test_resume_after_version_write_keeps_the_already_selected_version(
        self,
    ):
        replace = os.replace

        def interrupt_after_write(source, target, **kwargs):
            replace(source, target, **kwargs)
            if target == self.root / "version.toml":
                raise KeyboardInterrupt

        runner, calls = self._runner()
        with patch("os.replace", side_effect=interrupt_after_write):
            interrupted = self.release(runner)
        self.assertEqual(
            ("failed", "bump_candidate_version", "KeyboardInterrupt"),
            (
                interrupted["outcome"],
                interrupted["failed_step"],
                interrupted["error_type"],
            ),
            interrupted,
        )
        self.assertEqual(["preflight"], self.gates(calls))
        version = (self.root / "version.toml").read_text()

        calls.clear()
        result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(
            ["static", "functional", "image-tests", "canary"],
            self.gates(calls),
        )
        self.assert_same_candidate_version(version)

    def test_resume_rebuilds_changed_package_before_repeating_image_gate(self):
        runner, calls = self._runner()
        failed = self.release(self.failed_gate(runner, "image-tests"))
        self.assertEqual(
            ("failed", "verify_candidate_image"),
            (failed["outcome"], failed["failed_step"]),
            failed,
        )
        state = (
            self.root
            / f".anechoic_runtime/simple_local_release/runs/{self.run_id}/state.json"
        )
        package = (
            self.root / json.loads(state.read_text())["staging"] / "package"
        )
        (package / "version.toml").write_text("changed after preparation\n")
        version = (self.root / "version.toml").read_text()

        runner, calls = self._runner()
        with patch.object(
            package_phases, "build_package", wraps=package_phases.build_package
        ) as build:
            result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        build.assert_called_once()
        self.assertEqual(["image-tests", "canary"], self.gates(calls))
        self.assert_same_candidate_version(version)
        installed_package = self.runtime / "simple_local_release/package"
        self.assertEqual(
            version, (installed_package / "version.toml").read_text()
        )

    def test_interrupted_copies_and_install_resume_before_start(self):
        runner, _ = self._runner()
        copy_tree = package_phases._copy_tree
        incomplete = self.installed / self.native_sources[0].relative_to(
            self.control
        )

        def interrupt_copy(source, target, **options):
            copy_tree(source, target, **options)
            if target == self.installed:
                incomplete.unlink()
                raise KeyboardInterrupt

        with patch.object(
            package_phases, "_copy_tree", side_effect=interrupt_copy
        ):
            copied = self.release(runner)
        self.assertEqual(
            "copy_product_to_installed_framework",
            copied["failed_step"],
            copied,
        )
        self.assertFalse(incomplete.exists())

        real_install = package_phases._install_bootstrap
        with patch.object(
            package_phases, "_install_bootstrap", side_effect=KeyboardInterrupt
        ):
            interrupted = self.release(runner, resume=True)
        self.assertEqual(
            ("failed", "install_project_runtime", "KeyboardInterrupt"),
            (
                interrupted["outcome"],
                interrupted["failed_step"],
                interrupted["error_type"],
            ),
            interrupted,
        )
        self.assertEqual(
            self.native_sources[0].read_bytes(), incomplete.read_bytes()
        )
        self.start_container.assert_not_called()
        self.assertFalse((self.runtime / "start_mcp.py").exists())
        installed_package = self.runtime / "simple_local_release/package"
        target = installed_package / "version.toml"
        version = (self.root / "version.toml").read_text()
        self.assertEqual(version, target.read_text())

        self._assert_copy_resume(real_install, target, version)

    def _assert_copy_resume(self, real_install, target, version):
        runner, calls = self._runner()
        with (
            patch.object(
                package_phases, "_install_bootstrap", wraps=real_install
            ) as install,
            patch.object(
                package_phases,
                "copy_product",
                wraps=package_phases.copy_product,
            ) as copy,
        ):
            result = self.release(runner, resume=True)

        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual([], self.gates(calls))
        install.assert_called_once()
        copy.assert_not_called()
        self.assertEqual(version, target.read_text())
        self.assertTrue((self.runtime / "start_mcp.py").is_file())
        self.assertEqual(
            "keep = true\n", (self.runtime / "config.toml").read_text()
        )
        self.assert_same_candidate_version(version)
        self.start_container.assert_called_once()
