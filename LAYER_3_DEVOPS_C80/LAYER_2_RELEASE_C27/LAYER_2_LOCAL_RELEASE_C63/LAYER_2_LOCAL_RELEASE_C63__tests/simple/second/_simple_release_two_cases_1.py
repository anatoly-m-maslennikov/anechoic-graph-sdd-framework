"""Mocked local release cases."""

import stat

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)


class SimpleReleaseTwoCases1:
    def test_unsafe_product_descendant_refuses_before_any_clear(self):
        (self.product / "linked.txt").symlink_to(self.installed / "old.txt")
        self._assert_input_refused("unsafe-product")

    def test_invalid_version_refuses_before_tests_or_replacement(self):
        version = self.root / "version.toml"
        version.write_text('[framework]\nversion = "invalid"\n')
        self._assert_input_refused("invalid-version", "bump_candidate_version")
        self.assertIn('version = "invalid"', version.read_text())

    def test_release_preserves_launcher_runtime_config_and_methodology_archive(
        self,
    ):
        launcher = self.runtime / "start_mcp.py"
        launcher.write_bytes(b"existing launcher\n")
        state = self.runtime / "project_mcp_state.json"
        state.write_text("retain this runtime state\n", encoding="utf-8")
        archive = (
            self.installed / "SUPERLAYER_1_METHODOLOGY_SOURCES/retained.md"
        )
        archive.parent.mkdir()
        archive.write_text(
            "retain this methodology source\n", encoding="utf-8"
        )
        runner, _ = self._runner()
        result = run_local_release(
            self.root, run_id="launcher-state", runner=runner
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(
            self.engine_bootstrap.read_bytes(), launcher.read_bytes()
        )
        self.assertEqual(0o755, stat.S_IMODE(launcher.stat().st_mode))
        self.assertEqual(
            "keep = true\n", (self.runtime / "config.toml").read_text()
        )
        self.assertEqual("retain this runtime state\n", state.read_text())
        self.assertEqual(
            "retain this methodology source\n", archive.read_text()
        )
        self.start_container.assert_called_once()

    def test_four_component_local_version_increments_without_rollover(self):
        (self.root / "version.toml").write_text(
            '[framework]\nversion = "0.4.1.9"\n', encoding="utf-8"
        )
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="version", runner=runner)
        self.assertEqual("completed", result["outcome"])
        self.assertIn(
            'version = "0.4.1.10"', (self.root / "version.toml").read_text()
        )

    def test_workbench_node_dependencies_are_not_packaged(self):
        frontend = self.root / (
            "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/"
            "FEATURE_IWE_CONSOLE_FRONTEND"
        )
        dependencies = frontend / "node_modules/.bin"
        dependencies.mkdir(parents=True)
        (frontend / "package.json").write_text('{"name":"workbench"}')
        (dependencies / "vite").symlink_to("../vite/bin/vite.js")
        runner, _ = self._runner()
        result = run_local_release(
            self.root, run_id="frontend-dependencies", runner=runner
        )
        self.assertEqual("completed", result["outcome"])
        packaged = (
            self.runtime
            / "simple_local_release/package"
            / frontend.relative_to(self.root)
        )
        self.assertTrue((packaged / "package.json").is_file())
        self.assertFalse((packaged / "node_modules").exists())

    def test_preserved_ds_store_directories_do_not_block_replacement(self):
        kept, removed = (
            path.relative_to(self.control) for path in self.native_sources
        )
        self.native_sources[1].unlink()
        retained = (
            self.root / kept.parts[0],
            self.root / kept.parent,
            self.installed / "obsolete",
            self.runtime
            / "simple_local_release/package/LAYER_4_ENGINE_STUDIO_C14",
        )
        for directory in retained:
            directory.mkdir(parents=True, exist_ok=True)
            (directory / ".DS_Store").write_bytes(b"ignored")
            (directory / "obsolete.txt").write_text("old", encoding="utf-8")
        runner, _ = self._runner()
        result = run_local_release(self.root, run_id="ds-store", runner=runner)
        self.assertEqual("completed", result["outcome"])
        for directory in retained:
            self.assertEqual(
                b"ignored", (directory / ".DS_Store").read_bytes()
            )
            self.assertFalse((directory / "obsolete.txt").exists())
        self.assertTrue((self.root / kept).is_file())
        for target in (self.root, self.installed):
            self.assertFalse((target / removed).exists())
