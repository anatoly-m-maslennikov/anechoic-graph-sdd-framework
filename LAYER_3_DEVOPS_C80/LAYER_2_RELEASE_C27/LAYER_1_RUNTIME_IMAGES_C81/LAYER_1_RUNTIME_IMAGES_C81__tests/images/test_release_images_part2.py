"""Verify release image admission and immutable Docker identities."""

import shutil
import subprocess
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81 import release_images as images
from LAYER_1_RUNTIME_IMAGES_C81 import runtime_build


from ._release_image_fixture import ReleaseImageFixture


class ReleaseImagesTests(ReleaseImageFixture):
    def test_build_only_uses_checkout_and_cleans_staging(self):
        provenance = {**self.provenance, "project_root": str(self.package)}

        def manager(
            source,
            temporary,
            *,
            project_root,
            build_provenance,
            source_provider,
        ):
            (temporary / ".DS_Store").touch()
            self.manager = images.ImageManager(
                source,
                project_root=project_root,
                build_temp_root=temporary,
                build_provenance=build_provenance,
                executor=self.docker,
                source_provider=source_provider,
            )
            return self.manager

        with (
            patch.object(
                runtime_build, "read_release_selection", return_value=object()
            ),
            patch.object(
                runtime_build,
                "release_image_provenance",
                return_value=provenance,
            ),
            patch.object(
                runtime_build,
                "_native_release_sources",
                side_effect=lambda _: {
                    p.relative_to(self.package): p
                    for layer in (
                        "LAYER_1_META_ONTOLOGY_C9",
                        "LAYER_2_META_METHODOLOGY_C58",
                    )
                    for p in (self.package / layer).rglob("*.md")
                },
            ),
            patch.object(runtime_build, "_image_manager", side_effect=manager),
        ):
            result = runtime_build.build_image(self.package, run_id="build-1")
        self._assert_build_result(result)

    def _assert_build_result(self, result):
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(result["image_id"], self.image)
        self.assertEqual(
            result["fingerprint"],
            self.labels["org.anechoic.runtime.fingerprint"],
        )
        self.assertEqual(result["version"], "1.2.3")
        prune, build = self.commands[:2]
        self.assertEqual(
            prune[0],
            [
                "docker",
                "buildx",
                "prune",
                "--force",
                "--max-used-space",
                "4GB",
                "--min-free-space",
                "2GB",
            ],
        )
        self.assertEqual(build[0][:2], ["docker", "build"])
        self.assertEqual(prune[1:], build[1:])
        self.assertEqual(
            list(
                (self.package / ".anechoic_tmp/simple_local_release").iterdir()
            ),
            [],
        )
        self.assertEqual(
            self.tags, {"anechoic-runtime:test-" + self.image[7:]}
        )

    def test_build_only_cleans_staging_after_failure(self):
        provenance = {**self.provenance, "project_root": str(self.package)}
        with (
            patch.object(
                runtime_build, "read_release_selection", return_value=object()
            ),
            patch.object(
                runtime_build,
                "release_image_provenance",
                return_value=provenance,
            ),
            patch.object(
                runtime_build,
                "_image_manager",
                side_effect=RuntimeError("failed"),
            ),
        ):
            with self.assertRaises(RuntimeError):
                runtime_build.build_image(self.package, run_id="build-1")
        self.assertEqual(
            list(
                (self.package / ".anechoic_tmp/simple_local_release").iterdir()
            ),
            [],
        )

    def test_prune_failure_prevents_build(self):
        manager = self.make_manager()

        def fail_prune(argv, **kwargs):
            if argv[:3] == ["docker", "buildx", "prune"]:
                return subprocess.CompletedProcess(argv, 1)
            return self.docker(argv, **kwargs)

        manager.executor = fail_prune
        with self.assertRaisesRegex(
            RuntimeError, "Docker image operation failed"
        ):
            manager.resolve()
        self.assertEqual([], self.build_args)

    def test_build_and_installed_admission_bind_exact_package_and_labels(self):
        manager = self.make_manager()
        fingerprint = manager.identity(use_packaged_assets=True).fingerprint
        self.assertEqual(self.image, manager.resolve(use_packaged_assets=True))
        self.assertEqual(
            fingerprint, self.labels["org.anechoic.runtime.fingerprint"]
        )
        self.assertEqual(
            self.provenance["project_id"], self.labels["org.anechoic.project"]
        )
        installed = self.root / "installed"
        shutil.copytree(self.package, installed)
        manager = self.make_manager(installed, provenance=False)
        self.commands.clear()
        self.assertEqual(
            self.image,
            manager.resolve(explicit_id=self.image, build_if_missing=False),
        )
        self.assertFalse(
            any(
                command[0][:3] == ["docker", "buildx", "prune"]
                for command in self.commands
            )
        )
        (
            installed / "LAYER_3_DEVOPS_C80/"
            "LAYER_1_ENVIRONMENTS_C72/engine/uv.lock"
        ).write_text("changed")
        with self.assertRaises(RuntimeError):
            manager.resolve(explicit_id=self.image, build_if_missing=False)
