"""Beta Next release image closure, admission, and promotion checks."""

from pathlib import Path
import shutil
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81 import release_images as images
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import _BETA_REQUIRED
from ._release_image_fixture import ReleaseImageFixture


_SELECTOR = Path("LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml")
_ENGINE = Path("LAYER_4_ENGINE_STUDIO_C14")
_API = _ENGINE / "API_MIXER_beta_C91"
_API_ENTRY = _API / "API_MIXER_beta_C91__shared.py"
_C68 = _ENGINE / "ORCHESTRATOR_beta_C68"
_C70 = _ENGINE / "WORKBENCH_BACKEND_beta_C70"
_NEXT_INPUTS = (_C68 / "project_peer_owner.py", _C68 / "shared_peer_owner.py", _API_ENTRY, _API / "shared_runtime.py")


class BetaReleaseImagesTests(ReleaseImageFixture):
    def write_input(self, relative, text="source"):
        path = self.package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def write_beta_next_inputs(self):
        for relative in _BETA_REQUIRED:
            self.write_input(relative, "beta input")

    def test_beta_next_selects_candidate_roles_and_excludes_c70(self):
        self.write_beta_next_inputs()
        self.write_input(_API / "route.py")
        self.write_input(_C70 / "query_run.json")
        manager = self.make_manager()
        current = manager.identity()
        self.assertEqual("current", current.stack)
        self.assertFalse(any(Path(path).is_relative_to(_API) for path, _, _ in current.manifest))

        self.write_input(_SELECTOR, 'stack = "beta"\n')
        with self.assertRaisesRegex(ValueError, "invalid project.toml"):
            manager.resolve()
        self.assertEqual([], self.commands)

        self.write_input(_SELECTOR, 'stack = "beta_next"\n')
        next_identity = manager.identity()
        paths = {path for path, _, _ in next_identity.manifest}
        self.assertEqual("beta_next", next_identity.stack)
        common = {path for path, _, _ in current.manifest} - {images.TOOL_REGISTRY}
        self.assertEqual(common | set(_BETA_REQUIRED) | {_SELECTOR.as_posix(), (_API / "route.py").as_posix()}, paths)
        self.assertNotEqual(current.fingerprint, next_identity.fingerprint)
        self.write_input(_C70 / "query_run.json", "excluded change")
        self.assertEqual(next_identity, manager.identity())
        shutil.rmtree(self.package / _C70)
        self.assertEqual(next_identity, manager.identity())
        for relative in (*_NEXT_INPUTS, _API / "route.py"):
            with self.subTest(affected=relative):
                self.write_input(relative, "candidate change")
                self.assertNotEqual(next_identity.fingerprint, manager.identity().fingerprint)
                self.write_input(relative, "beta input" if relative in _NEXT_INPUTS else "source")

    def test_beta_next_build_admission_and_promotion_use_its_stack(self):
        for relative in _BETA_REQUIRED:
            if Path(relative) not in _NEXT_INPUTS:
                self.write_input(relative)
        self.write_input(_SELECTOR, 'stack = "beta_next"\n')
        self.write_input(_API / "route.py")
        manager = self.make_manager()
        for relative in _NEXT_INPUTS:
            with self.subTest(required=relative):
                with self.assertRaises(ValueError) as error:
                    manager.resolve()
                self.assertIn(f"image input unavailable: {relative.as_posix()}", str(error.exception))
            self.write_input(relative)
        self.assertEqual([], self.commands)

        self.assertEqual(self.image, manager.resolve())
        self.assertEqual("beta_next", self.build_args[self.build_args.index("--target") + 1])
        self.assertEqual("beta_next", self.labels["org.anechoic.runtime.stack"])
        self.assertEqual(manager.identity().fingerprint, self.labels["org.anechoic.runtime.fingerprint"])
        self.assertEqual(self.provenance["head_commit"], self.labels["org.anechoic.source.head_commit"])
        self.assertTrue({relative.as_posix() for relative in _NEXT_INPUTS} <= self.captured)
        self.assertFalse(any(Path(path).is_relative_to(_C70) for path in self.captured))
        next_tag = "anechoic-runtime:beta-next-" + self.image[7:]
        beta_tag = "anechoic-runtime:beta-" + self.image[7:]
        self.assertEqual({next_tag}, self.tags)
        self.tags.add(beta_tag)
        self.assertEqual("anechoic-runtime:prod-" + self.image[7:], manager.mark_production_image(self.image))
        self.assertNotIn(next_tag, self.tags)
        self.assertIn(beta_tag, self.tags)

        installed = self.make_manager(provenance=False)
        self.assertEqual(self.image, installed.resolve(explicit_id=self.image, build_if_missing=False))
        for value in ("beta", None):
            with self.subTest(stack=value):
                self.labels["org.anechoic.runtime.stack"] = value
                with self.assertRaisesRegex(RuntimeError, "image admission failed"):
                    installed.resolve(explicit_id=self.image, build_if_missing=False)

    def test_beta_next_closure_build_and_installed_admission(self):
        self.write_input(_SELECTOR, 'stack = "beta_next"\n')
        self.write_beta_next_inputs()
        current_kernel = self.package / images.ENGINE / "KERNEL_MIXER_C59/current.py"
        current_kernel.parent.mkdir(parents=True)
        current_kernel.write_text("current")
        frontend = self.package / images.ENGINE / "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/source.js"
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
        self.assertEqual("beta_next", self.build_args[self.build_args.index("--target") + 1])
        self.assertEqual(paths, self.captured)
        next_tag = "anechoic-runtime:beta-next-" + self.image[7:]
        test_tag = "anechoic-runtime:test-" + self.image[7:]
        self.assertEqual({next_tag}, self.tags)
        self.tags.add(test_tag)
        self.assertEqual("anechoic-runtime:prod-" + self.image[7:], manager.mark_production_image(self.image))
        self.assertNotIn(next_tag, self.tags)
        self.assertIn(test_tag, self.tags)
        installed = self.root / "installed"
        shutil.copytree(self.package, installed)
        manager = self.make_manager(installed, provenance=False)
        self.assertEqual(self.image, manager.resolve(explicit_id=self.image, build_if_missing=False))
        (installed / _BETA_REQUIRED[-1]).write_text("tampered")
        with self.assertRaises(RuntimeError):
            manager.resolve(explicit_id=self.image, build_if_missing=False)

    def test_beta_next_candidate_tag_collision_fails_closed(self):
        self.write_input(_SELECTOR, 'stack = "beta_next"\n')
        self.write_beta_next_inputs()
        manager = self.make_manager()
        original = manager._tag_images
        def collision(tag):
            return {"sha256:" + "f" * 64} if ":beta-next-" in tag else original(tag)
        with patch.object(manager, "_tag_images", side_effect=collision):
            with self.assertRaisesRegex(RuntimeError, "release image tag collision"):
                manager.resolve()
        self.assertEqual(set(), self.tags)

    def test_beta_next_promotion_does_not_remove_foreign_candidate_tag(self):
        self.write_input(_SELECTOR, 'stack = "beta_next"\n')
        self.write_beta_next_inputs()
        manager = self.make_manager()
        manager.resolve()
        original = manager._tag_images
        def foreign(tag):
            return {"sha256:" + "f" * 64} if ":beta-next-" in tag else original(tag)
        with patch.object(manager, "_tag_images", side_effect=foreign):
            manager.mark_production_image(self.image)
        self.assertIn("anechoic-runtime:beta-next-" + self.image[7:], self.tags)

    def test_beta_next_missing_required_inputs_fail_before_docker(self):
        self.write_input(_SELECTOR, 'stack = "beta_next"\n')
        self.write_beta_next_inputs()
        manager = self.make_manager()
        for relative in _BETA_REQUIRED:
            path = self.package / relative
            path.unlink()
            with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, "image input unavailable"):
                manager.resolve()
            path.write_text("beta input")
        self.assertEqual([], self.build_args)

