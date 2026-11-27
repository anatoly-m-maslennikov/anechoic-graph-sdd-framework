"""Verify release image admission and immutable Docker identities."""

import json
from pathlib import Path
import subprocess
from unittest.mock import NonCallableMock

from LAYER_1_RUNTIME_IMAGES_C81 import release_images as images


from ._release_image_fixture import ReleaseImageFixture


class ReleaseImagesTests(ReleaseImageFixture):
    def test_secrets_runtime_and_test_folders_never_enter_context(self):
        directory = self.package / images.ENGINE
        for relative in (
            ".env",
            "credentials.json",
            ".git/config",
            "area__tests/data",
            "secrets/data",
            ".venv-dev/data",
            ".venv-prod/data",
        ):
            path = directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("private")
        manager = self.make_manager()
        before = manager.identity().fingerprint
        (directory / ".env").write_text("different")
        self.assertEqual(before, manager.identity().fingerprint)
        manager.resolve(use_packaged_assets=True)
        self.assertFalse(
            any(
                any(
                    part
                    in {
                        ".env",
                        ".envrc",
                        "credentials.json",
                        ".git",
                        ".runtime",
                        "area__tests",
                        "secrets",
                    }
                    for part in Path(p).parts
                )
                for p in self.captured
            )
        )

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

    def test_build_removes_empty_directories_and_finder_metadata(
        self,
    ):
        manager = self.make_manager()

        def populate_context(argv, *, cwd, **kwargs):
            if argv[:3] == ["docker", "buildx", "prune"]:
                (cwd / "empty/nested").mkdir(parents=True)
                (cwd / "metadata-only/nested").mkdir(parents=True)
                for path in (
                    cwd / ".DS_Store",
                    cwd / images.ENGINE / ".DS_Store",
                    cwd / "metadata-only/nested/.DS_Store",
                ):
                    path.write_bytes(b"Finder metadata")
            if argv[:2] == ["docker", "build"]:
                self.assertFalse((cwd / "empty").exists())
                self.assertFalse((cwd / "metadata-only").exists())
            return self.docker(argv, cwd=cwd, **kwargs)

        manager.executor = populate_context
        self.assertEqual(self.image, manager.resolve())
        self.assertFalse(
            any(Path(path).name == ".DS_Store" for path in self.captured)
        )

    def test_context_changes_and_wrong_image_labels_fail_closed(self):
        manager = self.make_manager()

        def mutate(argv, **kwargs):
            result = self.docker(argv, **kwargs)
            if argv[:2] == ["docker", "build"]:
                (
                    Path(argv[-1]) / "LAYER_3_DEVOPS_C80/"
                    "LAYER_1_ENVIRONMENTS_C72/engine/uv.lock"
                ).write_text("tampered")
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
        self.assertEqual(
            {"anechoic-runtime:test-" + self.image[7:]}, self.tags
        )
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
            root=self.root,
            launcher_state=state,
            control_root=control,
            instance_id="b" * 64,
        )
        receipt = state / "ready.json"
        self.assertIsNone(images.ready_predecessor(selection))
        payload = {
            "project_root": str(self.root),
            "control_root": str(control),
            "project_id": selection.instance_id,
            "readiness": True,
            "image_id": self.image,
        }
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
