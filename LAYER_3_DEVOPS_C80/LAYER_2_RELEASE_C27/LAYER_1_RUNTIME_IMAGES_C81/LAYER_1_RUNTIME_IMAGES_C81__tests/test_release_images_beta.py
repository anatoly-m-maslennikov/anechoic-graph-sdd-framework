"""Beta release image closure, admission, and promotion checks."""

import shutil
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81 import release_images as images
from ._release_image_fixture import ReleaseImageFixture


class BetaReleaseImagesTests(ReleaseImageFixture):
    def test_beta_closure_build_and_installed_admission(self):
        from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import _BETA_REQUIRED

        (self.package / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml").write_text('stack = "beta"\n')
        for relative in _BETA_REQUIRED:
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("beta input")
        current_kernel = self.package / images.ENGINE / "KERNEL_MIXER_C59/current.py"
        current_kernel.parent.mkdir(parents=True)
        current_kernel.write_text("current")
        frontend = self.package / images.ENGINE / "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/source.js"
        frontend.parent.mkdir(parents=True)
        frontend.write_text("shared frontend")
        unrelated = self.package / images.ENGINE / "OTHER_beta_C999/source.py"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("other")
        manager = self.make_manager()
        identity = manager.identity()
        paths = {path for path, _, _ in identity.manifest}
        self.assertTrue(set(_BETA_REQUIRED) <= paths)
        self.assertIn(frontend.relative_to(self.package).as_posix(), paths)
        self.assertNotIn(images.TOOL_REGISTRY, paths)
        self.assertNotIn(current_kernel.relative_to(self.package).as_posix(), paths)
        self.assertNotIn(unrelated.relative_to(self.package).as_posix(), paths)
        self.assertEqual(self.image, manager.resolve())
        self.assertEqual("beta", self.build_args[self.build_args.index("--target") + 1])
        self.assertEqual(paths, self.captured)
        beta_tag = "anechoic-runtime:beta-" + self.image[7:]
        test_tag = "anechoic-runtime:test-" + self.image[7:]
        self.assertEqual({beta_tag}, self.tags)
        self.tags.add(test_tag)
        self.assertEqual("anechoic-runtime:prod-" + self.image[7:], manager.mark_production_image(self.image))
        self.assertNotIn(beta_tag, self.tags)
        self.assertIn(test_tag, self.tags)
        installed = self.root / "installed"
        shutil.copytree(self.package, installed)
        manager = self.make_manager(installed, provenance=False)
        self.assertEqual(self.image, manager.resolve(explicit_id=self.image, build_if_missing=False))
        (installed / _BETA_REQUIRED[-1]).write_text("tampered")
        with self.assertRaises(RuntimeError):
            manager.resolve(explicit_id=self.image, build_if_missing=False)

    def test_beta_candidate_tag_collision_fails_closed(self):
        from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import _BETA_REQUIRED

        (self.package / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml").write_text('stack = "beta"\n')
        for relative in _BETA_REQUIRED:
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("beta input")
        manager = self.make_manager()
        original = manager._tag_images
        def collision(tag):
            return {"sha256:" + "f" * 64} if ":beta-" in tag else original(tag)
        with patch.object(manager, "_tag_images", side_effect=collision):
            with self.assertRaisesRegex(RuntimeError, "release image tag collision"):
                manager.resolve()
        self.assertEqual(set(), self.tags)

    def test_beta_promotion_does_not_remove_foreign_candidate_tag(self):
        from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import _BETA_REQUIRED

        (self.package / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml").write_text('stack = "beta"\n')
        for relative in _BETA_REQUIRED:
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("beta input")
        manager = self.make_manager()
        manager.resolve()
        original = manager._tag_images
        def foreign(tag):
            return {"sha256:" + "f" * 64} if ":beta-" in tag else original(tag)
        with patch.object(manager, "_tag_images", side_effect=foreign):
            manager.mark_production_image(self.image)
        self.assertIn("anechoic-runtime:beta-" + self.image[7:], self.tags)

    def test_beta_missing_required_inputs_fail_before_docker(self):
        from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import _BETA_REQUIRED

        (self.package / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml").write_text('stack = "beta"\n')
        for relative in _BETA_REQUIRED:
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("beta input")
        manager = self.make_manager()
        for relative in _BETA_REQUIRED:
            path = self.package / relative
            path.unlink()
            with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, "image input unavailable"):
                manager.resolve()
            path.write_text("beta input")
        self.assertEqual([], self.build_args)

