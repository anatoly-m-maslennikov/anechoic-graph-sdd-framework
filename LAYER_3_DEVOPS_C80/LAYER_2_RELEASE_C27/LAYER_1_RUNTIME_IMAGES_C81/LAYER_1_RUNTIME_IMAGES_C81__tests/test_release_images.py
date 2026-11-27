"""Verify release image admission and immutable Docker identities."""

from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81 import release_images as images


from ._release_image_fixture import ReleaseImageFixture


class ReleaseImagesTests(ReleaseImageFixture):
    def test_delivery_sources_are_fingerprinted_and_copied(self):
        manager = self.make_manager()
        before = manager.identity()
        path = self.package / "LAYER_2_META_METHODOLOGY_C58/AN-S-1-source.md"
        path.write_text("updated source")
        self.assertNotEqual(before.fingerprint, manager.identity().fingerprint)
        manager.resolve()
        for layer in (
            "LAYER_1_META_ONTOLOGY_C9",
            "LAYER_2_META_METHODOLOGY_C58",
        ):
            self.assertIn(layer + "/AN-S-1-source.md", self.captured)

    def test_delivery_sources_are_required(self):
        manager = self.make_manager()
        (self.package / "LAYER_1_META_ONTOLOGY_C9/AN-S-1-source.md").unlink()
        with self.assertRaisesRegex(
            ValueError, "delivery sources unavailable"
        ):
            manager.identity()

    def test_license_edits_keep_the_runtime_fingerprint(self):
        from LAYER_1_RUNTIME_IMAGES_C81.release_image_identity import (
            LICENSE_INPUTS,
        )

        manager = self.make_manager()
        baseline = manager.identity()
        for relative in LICENSE_INPUTS:
            with self.subTest(relative=relative):
                (self.package / relative).write_text("Updated notice\n")
                updated = manager.identity()
                self.assertEqual(baseline.fingerprint, updated.fingerprint)
                self.assertNotEqual(baseline.manifest, updated.manifest)
                baseline = updated

    def test_registry_identity_uses_backend_asset(self):
        expected = (
            "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/"
            "FEATURE_IWE_CONSOLE_BACKEND/tool_registry.json"
        )
        self.assertEqual(expected, images.TOOL_REGISTRY)
        manager = self.make_manager()
        before = manager.identity(use_packaged_assets=True)
        self.assertEqual(
            [expected],
            [
                path
                for path, _, _ in before.manifest
                if path.endswith("tool_registry.json")
            ],
        )
        (self.package / expected).write_text("changed")
        self.assertNotEqual(
            before.fingerprint,
            manager.identity(use_packaged_assets=True).fingerprint,
        )

    def test_current_stack_excludes_beta_components_and_fingerprints_selector(
        self,
    ):
        manager = self.make_manager()
        baseline = manager.identity()
        beta = (
            self.package
            / images.ENGINE
            / "COMPONENT_beta_C123"
            / "nested"
            / "source.py"
        )
        beta.parent.mkdir(parents=True)
        beta.write_text("beta")
        self.assertEqual(baseline, manager.identity())
        selector = (
            self.package
            / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
        )
        selector.write_text('stack = "current"\n')
        selected = manager.identity()
        self.assertNotEqual(baseline.fingerprint, selected.fingerprint)
        self.assertIn(
            "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml",
            [path for path, _, _ in selected.manifest],
        )
        beta.write_text("changed")
        self.assertEqual(selected, manager.identity())
        manager.resolve()
        self.assertFalse(
            any("COMPONENT_beta_C123" in path for path in self.captured)
        )
        self.assertIn(
            "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml",
            self.captured,
        )
        self.assertNotIn("--target", self.build_args)

    def test_invalid_and_retired_selectors_fail_before_docker(self):
        manager = self.make_manager()
        selector = (
            self.package
            / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
        )
        for contents, message in (
            (b'stack = "beta"\n', "invalid project.toml"),
            (b'stack = "other"\n', "invalid project.toml"),
            (b'stack = "current"\nextra = 1\n', "invalid project.toml"),
            (b'stack = ["current"]\n', "invalid project.toml"),
            (b"\xff", "invalid project.toml"),
            (b" " * 65537, "invalid project.toml"),
        ):
            with self.subTest(contents=contents[:40]):
                selector.write_bytes(contents)
                with self.assertRaisesRegex(ValueError, message):
                    manager.resolve()
        selector.unlink()
        selector.symlink_to(self.package / "version.toml")
        with self.assertRaisesRegex(ValueError, "invalid project.toml"):
            manager.resolve()
        selector.unlink()
        selector.parent.rmdir()
        selector.parent.symlink_to(self.package, target_is_directory=True)
        (self.package / "project.toml").write_text('stack = "current"\n')
        with self.assertRaisesRegex(ValueError, "invalid project.toml"):
            manager.resolve()
        self.assertEqual({}, self.labels)
        self.assertEqual([], self.commands)

    def test_selector_change_during_inventory_fails(self):
        manager = self.make_manager()
        selector = (
            self.package
            / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
        )
        selector.write_text('stack = "current"\n')
        original_files = manager._files

        def change_selector():
            result = original_files()
            selector.write_text('stack = "current" # changed\n')
            return result

        with patch.object(manager, "_files", side_effect=change_selector):
            with self.assertRaisesRegex(
                ValueError, "image stack selection changed"
            ):
                manager.resolve()
        self.assertEqual([], self.build_args)
