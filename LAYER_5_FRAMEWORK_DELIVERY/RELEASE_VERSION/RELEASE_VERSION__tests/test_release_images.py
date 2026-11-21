"""Release image admission uses sealed inputs and immutable Docker identities."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import release_images as images


class ReleaseImagesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.package = self.root / "package"
        self.package.mkdir()
        for relative in images._REQUIRED:
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('[framework]\nversion = "1.2.3"\n' if relative == "version.toml" else "content")
        self.build = self.root / ".anechoic_tmp/build"
        self.build.mkdir(parents=True)
        self.image = "sha256:" + "a" * 64
        self.provenance = {"project_id": "b" * 64, "project_root": str(self.root),
                           "control_root": ".anechoic_test", "project_name": "Project", "head_commit": "c" * 40}
        self.labels = {}
        self.tags = set()
        self.captured = set()

    def docker(self, argv, **kwargs):
        if argv[:2] == ["docker", "build"]:
            labels = [argv[i + 1].split("=", 1) for i, item in enumerate(argv[:-1]) if item == "--label"]
            self.labels = dict(labels)
            context = Path(argv[-1])
            self.captured = {p.relative_to(context).as_posix() for p in context.rglob("*") if p.is_file()}
            Path(argv[argv.index("--iidfile") + 1]).write_text(self.image)
        elif argv[:3] == ["docker", "image", "inspect"]:
            data = [{"Id": self.image, "Os": "linux", "Architecture": self.manager.platform.split("/")[1],
                     "Config": {"Labels": self.labels}}]
            kwargs["stdout"].write(json.dumps(data).encode())
        elif argv[:3] == ["docker", "image", "ls"]:
            if argv[-1] in self.tags:
                kwargs["stdout"].write((self.image + "\n").encode())
        elif argv[:3] == ["docker", "image", "tag"]:
            self.tags.add(argv[-1])
        elif argv[:3] == ["docker", "image", "rm"]:
            self.tags.remove(argv[-1])
        else:
            self.fail(str(argv))
        return subprocess.CompletedProcess(argv, 0)

    def make_manager(self, package=None, provenance=True):
        self.manager = images.ImageManager(package or self.package, project_root=self.root,
                                           build_temp_root=self.build, executor=self.docker,
                                           build_provenance=self.provenance if provenance else None)
        return self.manager

    def test_build_only_uses_checkout_and_cleans_staging(self):
        import local_release

        provenance = {**self.provenance, "project_root": str(self.package)}
        def manager(source, temporary, *, project_root, build_provenance):
            self.manager = images.ImageManager(source, project_root=project_root, build_temp_root=temporary,
                                               build_provenance=build_provenance, executor=self.docker)
            return self.manager

        with (patch.object(local_release, "read_release_selection", return_value=object()),
              patch.object(local_release, "release_image_provenance", return_value=provenance),
              patch.object(local_release, "_image_manager", side_effect=manager)):
            result = local_release.build_image(self.package, run_id="build-1")
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(result["image_id"], self.image)
        self.assertEqual(result["fingerprint"], self.labels["org.anechoic.runtime.fingerprint"])
        self.assertEqual(result["version"], "1.2.3")
        self.assertEqual(list((self.package / ".anechoic_tmp/simple_local_release").iterdir()), [])
        self.assertEqual(self.tags, {"anechoic-runtime:test-" + self.image[7:]})

    def test_build_only_cleans_staging_after_failure(self):
        import local_release

        provenance = {**self.provenance, "project_root": str(self.package)}
        with (patch.object(local_release, "read_release_selection", return_value=object()),
              patch.object(local_release, "release_image_provenance", return_value=provenance),
              patch.object(local_release, "_image_manager", side_effect=RuntimeError("failed"))):
            with self.assertRaises(RuntimeError):
                local_release.build_image(self.package, run_id="build-1")
        self.assertEqual(list((self.package / ".anechoic_tmp/simple_local_release").iterdir()), [])

    def test_build_and_installed_admission_bind_exact_package_and_labels(self):
        manager = self.make_manager()
        fingerprint = manager.identity(use_packaged_assets=True).fingerprint
        self.assertEqual(self.image, manager.resolve(use_packaged_assets=True))
        self.assertEqual(fingerprint, self.labels["org.anechoic.runtime.fingerprint"])
        self.assertEqual(self.provenance["project_id"], self.labels["org.anechoic.project"])
        installed = self.root / "installed"
        shutil.copytree(self.package, installed)
        manager = self.make_manager(installed, provenance=False)
        self.assertEqual(self.image, manager.resolve(explicit_id=self.image, build_if_missing=False))
        (installed / "uv.lock").write_text("changed")
        with self.assertRaises(RuntimeError):
            manager.resolve(explicit_id=self.image, build_if_missing=False)

    def test_secrets_runtime_and_test_folders_never_enter_context(self):
        directory = self.package / images.ENGINE
        for relative in (".env", "credentials.json", ".git/config", "area__tests/data", "secrets/data"):
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

    def test_context_changes_and_wrong_image_labels_fail_closed(self):
        manager = self.make_manager()
        def mutate(argv, **kwargs):
            result = self.docker(argv, **kwargs)
            if argv[:2] == ["docker", "build"]:
                (Path(argv[-1]) / "uv.lock").write_text("tampered")
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
        selection = SimpleNamespace(root=self.root, launcher_state=state, control_root=control, instance_id="b" * 64)
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
