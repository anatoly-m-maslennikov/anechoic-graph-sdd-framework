"""Credential exclusion cases for runtime image tests."""

import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
from unittest.mock import patch

from ..group_1.test_runtime_images_safety import APP
from ..group_1.test_runtime_images_safety import IMAGE_ID
from ..group_1.test_runtime_images_safety import PRIVATE_MARKER
from ..group_1.test_runtime_images_safety import PROXY_ROUTING
from ..group_1.test_runtime_images_safety import _tagging_executor
from ..group_1.test_runtime_images_safety import images


class ImageCredentialCases:
    def _credential_files(self, source):
        engine = source / images.ENGINE_ROOT
        protected = set()
        for name in (
            "auth.json",
            "credentials.json",
            "token.txt",
            "token.json",
            "secrets.json",
            "secrets.txt",
        ):
            path = engine / name
            path.write_text(PRIVATE_MARKER)
            protected.add(path)
        for name in (
            "vault",
            ".vault",
            "secrets",
            ".secrets",
            "credentials",
            ".credentials",
        ):
            directory = engine / name
            directory.mkdir()
            path = directory / "unclassified-store.txt"
            path.write_text(PRIVATE_MARKER)
            protected.add(path)
        generated = engine / ".anechoic_runtime"
        generated.mkdir()
        path = generated / "generated-output.json"
        path.write_text(PRIVATE_MARKER)
        protected.add(path)

        return protected

    @staticmethod
    def _populate_source(source):
        docker = source / images.DOCKER_ROOT
        docker.mkdir(parents=True)
        (source / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine").mkdir(
            parents=True
        )
        (
            source
            / (
                "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/"
                "pyproject.toml"
            )
        ).write_text("[project]\nname='fixture'\n")
        (
            source
            / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock"
        ).write_text("version=1\n")
        (source / "version.toml").write_text(
            '[framework]\nversion = "0.4.4.9"\n'
        )
        (docker / "Dockerfile").write_text("FROM scratch\n")
        (docker / "Dockerfile.dockerignore").write_text(".git\n")
        (docker.parent / "engine.py").write_text("ENGINE=True\n")
        exporter = source / "LAYER_4_ENGINE_STUDIO_C14/API_MIXER_beta_C91"
        exporter.mkdir()
        for name in ("__init__.py", "openapi.py"):
            (exporter / name).write_text("fixture")
        for relative in images.LICENSE_INPUTS:
            (source / relative).parent.mkdir(parents=True, exist_ok=True)
            (source / relative).write_text("fixture license\n")
        for layer in (
            "LAYER_1_META_ONTOLOGY_C9",
            "LAYER_2_META_METHODOLOGY_C58",
        ):
            path = source / layer / "AN-S-1-source.md"
            path.parent.mkdir(parents=True)
            path.write_text("source")

    def _credential_fixture(self):
        model = patch.object(
            images.ImageManager, "_refresh_model", return_value="a" * 64
        )
        model.start()
        self.addCleanup(model.stop)
        tools = patch.object(
            images,
            "_compile_tool_registry",
            return_value=b'{"schema_version":1}\n',
        )
        tools.start()
        self.addCleanup(tools.stop)
        parent = APP.parents[2] / ".anechoic_tmp/launcher-epic-1829/images"
        parent.mkdir(parents=True, exist_ok=True)
        source = Path(
            tempfile.mkdtemp(prefix="image-credentials-", dir=parent)
        )
        self.addCleanup(shutil.rmtree, source, ignore_errors=True)
        self._populate_source(source)
        manager = images.ImageManager(
            source,
            executor=lambda *_a, **_k: None,
            uid=1000,
            gid=1000,
            platform="linux/amd64",
            project_root=APP.parents[2],
        )
        before = manager.identity()
        with patch.dict(os.environ, PROXY_ROUTING):
            self.assertEqual(
                before,
                manager.identity(),
                "proxy routing is not an image input",
            )
        protected = self._credential_files(source)

        return manager, before, protected

    def _credential_executor(self, before, calls):
        def executor(argv, **_kwargs):
            calls.append(tuple(argv))
            if "ls" in argv:
                return subprocess.CompletedProcess(argv, 0, "", "")
            if "build" in argv:
                context = Path(argv[-1])
                actual = {
                    path.relative_to(context).as_posix()
                    for path in context.rglob("*")
                    if path.is_file()
                }
                self.assertEqual({row.path for row in before.manifest}, actual)
                for row in before.manifest:
                    staged = context / row.path
                    self.assertEqual(row.mode, staged.stat().st_mode & 0o777)
                Path(argv[argv.index("--iidfile") + 1]).write_text(
                    IMAGE_ID + "\n"
                )
                return subprocess.CompletedProcess(
                    argv, 0, PRIVATE_MARKER, PRIVATE_MARKER
                )
            inspection = [
                {
                    "Id": IMAGE_ID,
                    "Created": "2026-10-21T14:15:16.987654321Z",
                    "RepoTags": [],
                    "Os": "linux",
                    "Architecture": "amd64",
                    "Config": {
                        "Labels": {
                            images.SCHEMA_LABEL: images.SCHEMA,
                            images.FINGERPRINT_LABEL: before.fingerprint,
                            "org.opencontainers.image.version": "0.4.4.9",
                        }
                    },
                }
            ]
            return subprocess.CompletedProcess(
                argv, 0, json.dumps(inspection), PRIVATE_MARKER
            )

        return executor

    def test_known_credential_stores_are_neither_read_hashed_nor_copied(self):
        manager, before, protected = self._credential_fixture()
        read_bytes = Path.read_bytes

        def guarded_read(path):
            self.assertNotIn(
                path, protected, "excluded store bytes must not be opened"
            )
            return read_bytes(path)

        calls = []

        executor = self._credential_executor(before, calls)

        manager.executor = _tagging_executor(executor, calls)
        with patch.object(Path, "read_bytes", guarded_read):
            self.assertEqual(before, manager.identity())
            self.assertEqual(IMAGE_ID, manager.resolve())
        self.assertEqual(1, sum("build" in call for call in calls))
        self.assertEqual(1, sum("tag" in call for call in calls))
        self.assertFalse(any("run" in call for call in calls))
