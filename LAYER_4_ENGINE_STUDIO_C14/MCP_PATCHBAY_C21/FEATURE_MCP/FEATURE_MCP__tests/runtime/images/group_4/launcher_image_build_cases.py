"""Long image build contracts shared with the focused test module."""

import json
import os
from pathlib import Path
import subprocess
from unittest.mock import patch

from ..group_5.launcher_images_test_support import FRAMEWORK_VERSION
from ..group_5.launcher_images_test_support import IMAGE_ID
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
    TOOL_REGISTRY,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    ImageError,
)


def _packaged_executor(assertions, payloads, assets, builds, identity):
    def execute(argv, **_kwargs):
        current_identity = identity[0]
        if "ls" in argv or "prune" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "build" in argv:
            builds.append(argv)
            context = Path(argv[-1])
            assertions.assertEqual(
                payloads,
                {path: (context / path).read_bytes() for path in assets},
            )
            Path(argv[argv.index("--iidfile") + 1]).write_text(
                IMAGE_ID, encoding="ascii"
            )
            return subprocess.CompletedProcess(argv, 0, "", "")
        return subprocess.CompletedProcess(
            argv,
            0,
            json.dumps([
                {
                    "Id": IMAGE_ID,
                    "Created": "2026-10-21T14:15:16Z",
                    "Os": "linux",
                    "Architecture": "amd64",
                    "Config": {
                        "Labels": {
                            "org.anechoic.runtime.schema": "1",
                            (
                                'org.anechoic.runtime.fingerp'
                                'rint'
                            ): current_identity.fingerprint,
                            (
                                'org.opencontainers.image.ver'
                                'sion'
                            ): current_identity.version,
                        }
                    },
                }
            ]),
            "",
        )

    return execute


def _private_executor(identity, calls):
    def execute(argv, **kwargs):
        argv = tuple(argv)
        calls.append((argv, kwargs))
        if "ls" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "build" in argv:
            iidfile = Path(argv[argv.index("--iidfile") + 1])
            iidfile.write_text(IMAGE_ID + "\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "", "")
        inspection = json.dumps([
            {
                "Id": IMAGE_ID,
                "Created": "2026-10-21T14:15:16.987654321Z",
                "RepoTags": [],
                "Os": "linux",
                "Architecture": "amd64",
                "Config": {
                    "Labels": {
                        "org.anechoic.runtime.schema": "1",
                        (
                            'org.anechoic.runtime.fingerp'
                            'rint'
                        ): identity.fingerprint,
                        "org.opencontainers.image.version": FRAMEWORK_VERSION,
                    }
                },
            }
        ])
        return subprocess.CompletedProcess(argv, 0, inspection, "")

    return execute


class _ImageBuildCases:
    def test_packaged_assets_can_build_without_resolving_a_predecessor(
        self,
    ) -> None:
        source = self.source_fixture()
        assets = (TOOL_REGISTRY,)
        payloads = {
            path: json.dumps({"asset": Path(path).stem}).encode()
            for path in assets
        }
        for path, payload in payloads.items():
            (source / path).write_bytes(payload)
        builds = []
        identity = []
        executor = _packaged_executor(self, payloads, assets, builds, identity)
        manager = self.manager(source, executor)
        manager.build_temp_root = self.fixture_root / "builds"
        manager.build_temp_root.mkdir()
        with patch.object(
            manager,
            "_refresh_model",
            side_effect=AssertionError("asset refresh invoked"),
        ):
            identity.append(manager.identity(use_packaged_assets=True))
            with self.assertRaises(ImageError) as refused:
                manager.resolve(
                    build_if_missing=False, use_packaged_assets=True
                )
            self.assertEqual("IMAGE_REFUSED", refused.exception.code)
            self.assertEqual([], builds)
            self.assertEqual(
                IMAGE_ID, manager.resolve(use_packaged_assets=True)
            )
        self.assertEqual(1, len(builds))

    def test_build_uses_private_sibling_buildx_client_state_only_for_that_subprocess(
        self,
    ) -> None:
        source = self.source_fixture()
        manager = self.manager(source, lambda *_a, **_k: None)
        identity = manager.identity()
        calls = []
        client = {
            "HOME": "/synthetic-home",
            "PATH": "/synthetic-bin",
            "DOCKER_CONFIG": "/synthetic-docker-config",
        }
        caller = dict(client, AWS_SECRET_ACCESS_KEY="synthetic-private-secret")

        executor = _private_executor(identity, calls)
        manager = self.manager(source, executor)
        with patch.dict(os.environ, caller, clear=True):
            self.assertEqual(IMAGE_ID, manager.resolve())
        self.assertEqual(identity, manager.identity())
        build, build_kwargs = next(
            (call for call in calls if "build" in call[0])
        )
        state = Path(build_kwargs["env"]["BUILDX_CONFIG"])
        self.assertEqual(
            build[build.index("--iidfile") + 1], str(state.parent / "image.id")
        )
        self.assertEqual("buildx", state.name)
        self.assertTrue(state.is_dir())
        self.assertEqual(
            dict(client, BUILDX_CONFIG=str(state)), build_kwargs["env"]
        )
        self.assertNotIn(
            "synthetic-private-secret", build_kwargs["env"].values()
        )
        self.assertNotIn(str(state), build)
        self.assertNotIn(str(state), " ".join(build))
        self._assert_private_prune_order(calls, build, build_kwargs)

    def _assert_private_prune_order(self, calls, build, build_kwargs):
        prune = (
            "docker",
            "buildx",
            "prune",
            "--force",
            "--max-used-space",
            "4GB",
            "--min-free-space",
            "2GB",
        )
        prune_index = next(
            i for i, (command, _) in enumerate(calls) if command == prune
        )
        build_index = next(
            i for i, (command, _) in enumerate(calls) if command == build
        )
        self.assertEqual(build_index - 1, prune_index)
        self.assertEqual(build_kwargs, calls[prune_index][1])
        for command, kwargs in calls:
            if "build" not in command and command != prune:
                self.assertNotIn("env", kwargs)
