"""Release image admission uses sealed inputs and immutable Docker identities."""

import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import NonCallableMock, patch

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
        for layer in ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58"):
            self.assertIn(layer + "/AN-S-1-source.md", self.captured)

    def test_delivery_sources_are_required(self):
        manager = self.make_manager()
        (self.package / "LAYER_1_META_ONTOLOGY_C9/AN-S-1-source.md").unlink()
        with self.assertRaisesRegex(ValueError, "delivery sources unavailable"):
            manager.identity()

    def test_license_edits_keep_the_runtime_fingerprint(self):
        from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LICENSE_INPUTS

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
        expected = "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/tool_registry.json"
        self.assertEqual(expected, images.TOOL_REGISTRY)
        manager = self.make_manager()
        before = manager.identity(use_packaged_assets=True)
        self.assertEqual([expected], [path for path, _, _ in before.manifest if path.endswith("tool_registry.json")])
        (self.package / expected).write_text("changed")
        self.assertNotEqual(before.fingerprint, manager.identity(use_packaged_assets=True).fingerprint)

    def test_current_stack_excludes_beta_components_and_fingerprints_selector(self):
        manager = self.make_manager()
        baseline = manager.identity()
        beta = self.package / images.ENGINE / "COMPONENT_beta_C123" / "nested" / "source.py"
        beta.parent.mkdir(parents=True)
        beta.write_text("beta")
        self.assertEqual(baseline, manager.identity())
        selector = self.package / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
        selector.write_text('stack = "current"\n')
        selected = manager.identity()
        self.assertNotEqual(baseline.fingerprint, selected.fingerprint)
        self.assertIn("LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml", [path for path, _, _ in selected.manifest])
        beta.write_text("changed")
        self.assertEqual(selected, manager.identity())
        manager.resolve()
        self.assertFalse(any("COMPONENT_beta_C123" in path for path in self.captured))
        self.assertIn("LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml", self.captured)
        self.assertNotIn("--target", self.build_args)

    def test_invalid_and_retired_selectors_fail_before_docker(self):
        manager = self.make_manager()
        selector = self.package / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
        for contents, message in ((b'stack = "beta"\n', "invalid project.toml"),
                                  (b'stack = "other"\n', "invalid project.toml"),
                                  (b'stack = "current"\nextra = 1\n', "invalid project.toml"),
                                  (b'stack = ["current"]\n', "invalid project.toml"),
                                  (b'\xff', "invalid project.toml"),
                                  (b' ' * 65537, "invalid project.toml")):
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
        selector = self.package / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
        selector.write_text('stack = "current"\n')
        original_files = manager._files

        def change_selector():
            result = original_files()
            selector.write_text('stack = "current" # changed\n')
            return result

        with patch.object(manager, "_files", side_effect=change_selector):
            with self.assertRaisesRegex(ValueError, "image stack selection changed"):
                manager.resolve()
        self.assertEqual([], self.build_args)

    def test_build_only_uses_checkout_and_cleans_staging(self):
        from LAYER_1_RUNTIME_IMAGES_C81 import runtime_build

        provenance = {**self.provenance, "project_root": str(self.package)}
        def manager(source, temporary, *, project_root, build_provenance, source_provider):
            (temporary / ".DS_Store").touch()
            self.manager = images.ImageManager(source, project_root=project_root, build_temp_root=temporary,
                                               build_provenance=build_provenance, executor=self.docker,
                                               source_provider=source_provider)
            return self.manager

        with (patch.object(runtime_build, "read_release_selection", return_value=object()),
              patch.object(runtime_build, "release_image_provenance", return_value=provenance),
              patch.object(runtime_build, "_native_release_sources", side_effect=lambda _: {p.relative_to(self.package): p for layer in ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58") for p in (self.package / layer).rglob("*.md")}),
              patch.object(runtime_build, "_image_manager", side_effect=manager)):
            result = runtime_build.build_image(self.package, run_id="build-1")
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(result["image_id"], self.image)
        self.assertEqual(result["fingerprint"], self.labels["org.anechoic.runtime.fingerprint"])
        self.assertEqual(result["version"], "1.2.3")
        prune, build = self.commands[:2]
        self.assertEqual(prune[0], ["docker", "buildx", "prune", "--force", "--max-used-space", "4GB", "--min-free-space", "2GB"])
        self.assertEqual(build[0][:2], ["docker", "build"])
        self.assertEqual(prune[1:], build[1:])
        self.assertEqual(list((self.package / ".anechoic_tmp/simple_local_release").iterdir()), [])
        self.assertEqual(self.tags, {"anechoic-runtime:test-" + self.image[7:]})

    def test_build_only_cleans_staging_after_failure(self):
        from LAYER_1_RUNTIME_IMAGES_C81 import runtime_build

        provenance = {**self.provenance, "project_root": str(self.package)}
        with (patch.object(runtime_build, "read_release_selection", return_value=object()),
              patch.object(runtime_build, "release_image_provenance", return_value=provenance),
              patch.object(runtime_build, "_image_manager", side_effect=RuntimeError("failed"))):
            with self.assertRaises(RuntimeError):
                runtime_build.build_image(self.package, run_id="build-1")
        self.assertEqual(list((self.package / ".anechoic_tmp/simple_local_release").iterdir()), [])

    def test_prune_failure_prevents_build(self):
        manager = self.make_manager()
        def fail_prune(argv, **kwargs):
            if argv[:3] == ["docker", "buildx", "prune"]:
                return subprocess.CompletedProcess(argv, 1)
            return self.docker(argv, **kwargs)
        manager.executor = fail_prune
        with self.assertRaisesRegex(RuntimeError, "Docker image operation failed"):
            manager.resolve()
        self.assertEqual([], self.build_args)

    def test_build_and_installed_admission_bind_exact_package_and_labels(self):
        manager = self.make_manager()
        fingerprint = manager.identity(use_packaged_assets=True).fingerprint
        self.assertEqual(self.image, manager.resolve(use_packaged_assets=True))
        self.assertEqual(fingerprint, self.labels["org.anechoic.runtime.fingerprint"])
        self.assertEqual(self.provenance["project_id"], self.labels["org.anechoic.project"])
        installed = self.root / "installed"
        shutil.copytree(self.package, installed)
        manager = self.make_manager(installed, provenance=False)
        self.commands.clear()
        self.assertEqual(self.image, manager.resolve(explicit_id=self.image, build_if_missing=False))
        self.assertFalse(any(command[0][:3] == ["docker", "buildx", "prune"] for command in self.commands))
        (installed / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock").write_text("changed")
        with self.assertRaises(RuntimeError):
            manager.resolve(explicit_id=self.image, build_if_missing=False)

    def test_secrets_runtime_and_test_folders_never_enter_context(self):
        directory = self.package / images.ENGINE
        for relative in (".env", "credentials.json", ".git/config", "area__tests/data", "secrets/data", ".venv-dev/data", ".venv-prod/data"):
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("private")
        manager = self.make_manager()
        before = manager.identity().fingerprint
        (directory / ".env").write_text("different")
        self.assertEqual(before, manager.identity().fingerprint)
        manager.resolve(use_packaged_assets=True)
        self.assertFalse(any(any(part in {".env", ".envrc", "credentials.json", ".git", ".runtime", "area__tests", "secrets"} for part in Path(p).parts) for p in self.captured))

    def test_unsupported_private_inputs_fail_closed(self):
        directory = self.package / images.ENGINE
        manager = self.make_manager()
        for relative in (".envrc", ".runtime/state"):
            with self.subTest(relative=relative):
                path = directory / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("private")
                with self.assertRaises(ValueError):
                    manager.identity()
                path.unlink()
                if path.parent != directory:
                    path.parent.rmdir()

    def test_build_removes_empty_directories_and_finder_metadata_from_the_context(self):
        manager = self.make_manager()

        def populate_context(argv, *, cwd, **kwargs):
            if argv[:3] == ["docker", "buildx", "prune"]:
                (cwd / "empty/nested").mkdir(parents=True)
                (cwd / "metadata-only/nested").mkdir(parents=True)
                for path in (cwd / ".DS_Store", cwd / images.ENGINE / ".DS_Store", cwd / "metadata-only/nested/.DS_Store"):
                    path.write_bytes(b"Finder metadata")
            if argv[:2] == ["docker", "build"]:
                self.assertFalse((cwd / "empty").exists())
                self.assertFalse((cwd / "metadata-only").exists())
            return self.docker(argv, cwd=cwd, **kwargs)

        manager.executor = populate_context
        self.assertEqual(self.image, manager.resolve())
        self.assertFalse(any(Path(path).name == ".DS_Store" for path in self.captured))

    def test_context_changes_and_wrong_image_labels_fail_closed(self):
        manager = self.make_manager()
        def mutate(argv, **kwargs):
            result = self.docker(argv, **kwargs)
            if argv[:2] == ["docker", "build"]:
                (Path(argv[-1]) / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock").write_text("tampered")
            return result
        manager.executor = mutate
        with self.assertRaises(RuntimeError):
            manager.resolve()
        manager.executor = self.docker
        manager.resolve()
        self.labels["org.anechoic.runtime.fingerprint"] = "0" * 64
        with self.assertRaises(RuntimeError):
            manager.resolve(explicit_id=self.image, build_if_missing=False)

    def test_immutable_production_tag_and_collision(self):
        manager = self.make_manager()
        manager.resolve()
        self.assertEqual({"anechoic-runtime:test-" + self.image[7:]}, self.tags)
        tag = manager.mark_production_image(self.image)
        self.assertEqual(tag, "anechoic-runtime:prod-" + self.image[7:])
        self.assertEqual({tag}, self.tags)
        self.assertEqual(tag, manager.mark_production_image(self.image))
        with self.assertRaises(ValueError):
            manager.mark_production_image("latest")
        def collision(argv, **kwargs):
            if argv[:3] == ["docker", "image", "ls"]:
                kwargs["stdout"].write(("sha256:" + "d" * 64 + "\n").encode())
                return subprocess.CompletedProcess(argv, 0)
            return self.docker(argv, **kwargs)
        manager.executor = collision
        with self.assertRaises(RuntimeError):
            manager.mark_production_image(self.image)

    def test_invalid_provenance_and_mutable_image_are_rejected(self):
        self.provenance["head_commit"] = "short"
        with self.assertRaises(ValueError):
            self.make_manager()
        self.provenance["head_commit"] = "c" * 40
        manager = self.make_manager()
        with self.assertRaises(ValueError):
            manager.resolve(explicit_id="latest", build_if_missing=False)

    def test_ready_receipt_validates_owner_duplicate_fields_and_symlinks(self):
        state = self.root / ".anechoic_runtime/project/id"
        state.mkdir(parents=True)
        control = self.root / ".anechoic_test"
        selection = NonCallableMock(
            spec_set=["root", "launcher_state", "control_root", "instance_id"],
            root=self.root, launcher_state=state, control_root=control,
            instance_id="b" * 64,
        )
        receipt = state / "ready.json"
        self.assertIsNone(images.ready_predecessor(selection))
        payload = {"project_root": str(self.root), "control_root": str(control), "project_id": selection.instance_id,
                   "readiness": True, "image_id": self.image}
        receipt.write_text(json.dumps(payload))
        self.assertEqual(self.image, images.ready_predecessor(selection))
        payload["readiness"] = False
        receipt.write_text(json.dumps(payload))
        with self.assertRaises(ValueError):
            images.ready_predecessor(selection)
        receipt.write_text('{"readiness":true,"readiness":true}')
        with self.assertRaises(ValueError):
            images.ready_predecessor(selection)
        receipt.unlink()
        receipt.symlink_to(self.root / "elsewhere")
        with self.assertRaises(ValueError):
            images.ready_predecessor(selection)


if __name__ == "__main__":
    unittest.main()
