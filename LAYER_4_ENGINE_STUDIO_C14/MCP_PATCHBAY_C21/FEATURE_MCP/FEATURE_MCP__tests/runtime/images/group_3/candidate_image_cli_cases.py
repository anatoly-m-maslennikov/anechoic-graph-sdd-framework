"""Fixture-only CLI build contracts for candidate images."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
from unittest.mock import Mock, patch

from MCP_PATCHBAY_C21.FEATURE_MCP.docker import (
    docker__shared as runtime_images,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    DOCKERFILE,
    FINGERPRINT_LABEL,
    SCHEMA_LABEL,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.cli.cli__shared import (
    candidate_image_main,
)

IMAGE = "sha256:" + "a" * 64
FRAMEWORK_VERSION = "0.4.4.9"
ATTEMPT_LABEL = "org.anechoic.full-test-suite.attempt"
ATTEMPT = "a" * 32


def docker_process(result, stdout):
    output = None
    if stdout == subprocess.PIPE:
        reader, writer = os.pipe()
        output = os.fdopen(reader, "rb")
        with os.fdopen(writer, "wb") as stream:
            stream.write(result.stdout.encode())
    return Mock(
        stdout=output,
        wait=Mock(return_value=result.returncode),
        poll=Mock(return_value=result.returncode),
    )


class _CandidateImageCases:
    def _build_executor(self, labels, commands, tags):
        def execute(argv, **_kwargs):
            commands.append(argv)
            if argv[:3] == ["docker", "image", "tag"]:
                tags.add(argv[-1])
                return subprocess.CompletedProcess(argv, 0, "")
            if self._is_tag_inspect(argv):
                return self._tagged_inspection(argv, labels, tags)
            if argv[:2] == ["docker", "build"]:
                return self._build_result(argv, labels)
            if argv[:3] == ["docker", "image", "inspect"]:
                return self._ordinary_inspection(argv, labels)
            return subprocess.CompletedProcess(argv, 0, "")

        return execute

    @staticmethod
    def _is_tag_inspect(argv):
        return argv[:3] == ["docker", "image", "inspect"] and argv[
            -1
        ].startswith("anechoic-runtime:")

    @staticmethod
    def _tagged_inspection(argv, labels, tags):
        if argv[-1] not in tags:
            return subprocess.CompletedProcess(argv, 1, "")
        value = {
            "Id": IMAGE,
            "Created": "2026-10-21T14:15:16.987654321Z",
            "RepoTags": [argv[-1]],
            "Config": {"Labels": labels},
            "Os": "linux",
            "Architecture": "arm64",
        }
        return subprocess.CompletedProcess(argv, 0, json.dumps([value]))

    def _build_result(self, argv, labels):
        for index, argument in enumerate(argv):
            if argument == "--label":
                key, value = argv[index + 1].split("=", 1)
                labels[key] = value
        context = Path(argv[-1])
        self.assertEqual(
            "fixture-current-code", (context / DOCKERFILE).read_text()
        )
        Path(argv[argv.index("--iidfile") + 1]).write_text(IMAGE)
        return subprocess.CompletedProcess(argv, 0, "")

    def _ordinary_inspection(self, argv, labels):
        architecture = (
            "arm64"
            if runtime_images.ImageManager(
                self.root, project_root=self.root
            ).platform
            == "linux/arm64"
            else "amd64"
        )
        value = {
            "Id": IMAGE,
            "Created": "2026-10-21T14:15:16.987654321Z",
            "RepoTags": [],
            "Config": {"Labels": labels},
            "Os": "linux",
            "Architecture": architecture,
        }
        return subprocess.CompletedProcess(argv, 0, json.dumps([value]))

    def test_real_builder_copies_current_bytes_and_passes_actual_immutable_id(
        self,
    ):
        labels, commands, tags = {}, [], set()

        execute = self._build_executor(labels, commands, tags)

        with (
            patch.object(
                subprocess,
                "Popen",
                side_effect=lambda argv, **kwargs: docker_process(
                    execute(argv), kwargs["stdout"]
                ),
            ),
            patch.object(
                runtime_images,
                "_compile_tool_registry",
                return_value=b'{"schema_version":1}\n',
            ),
            patch.object(
                runtime_images.ImageManager,
                "_refresh_model",
                return_value="a" * 64,
            ),
            redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(0, candidate_image_main(self.build_command()))
            self.assertEqual(0, candidate_image_main(self.cleanup_command()))
        self._assert_real_build_outputs(labels, commands, output)

    def _assert_real_build_outputs(self, labels, commands, output):
        self.assertEqual(IMAGE + "\n", output.getvalue())
        self.assertEqual("1", labels[SCHEMA_LABEL])
        self.assertEqual(64, len(labels[FINGERPRINT_LABEL]))
        self.assertEqual(
            FRAMEWORK_VERSION, labels["org.opencontainers.image.version"]
        )
        self.assertEqual(ATTEMPT, labels[ATTEMPT_LABEL])
        self.assertEqual(
            1, sum(argv[:2] == ["docker", "build"] for argv in commands)
        )
        self.assertEqual(["docker", "image", "rm", IMAGE], commands[-1])
        expected = (
            "anechoic-runtime:0.4.4.9-test-2026-10-21_14-15-16Z-aaaaaaaaaaaa"
        )
        self.assertEqual(
            ["docker", "image", "tag", IMAGE, expected],
            next(
                argv
                for argv in commands
                if argv[:3] == ["docker", "image", "tag"]
            ),
        )
        self.assertEqual(
            [expected],
            [
                argv[-1]
                for argv in commands
                if argv[:3] == ["docker", "image", "ls"]
            ],
        )

    def test_cli_validates_paths_and_immutable_image(self):
        self._assert_packaged_build()
        self._assert_valid_cleanup()
        self._assert_invalid_paths_do_not_reach_docker()

    def _assert_packaged_build(self):
        with (
            patch.object(runtime_images, "ImageManager") as builder,
            redirect_stdout(io.StringIO()) as output,
        ):
            manager = builder.return_value
            manager._build.return_value = IMAGE
            self.assertEqual(
                0,
                candidate_image_main(self.build_command("--packaged-assets")),
            )
        self.assertEqual(IMAGE + "\n", output.getvalue())
        self.assertEqual(self.root, builder.call_args.args[0])
        self.assertEqual(
            self.scratch, builder.call_args.kwargs["build_temp_root"]
        )
        manager.identity.assert_called_once_with(use_packaged_assets=True)
        manager._build.assert_called_once_with(
            manager.identity.return_value, use_packaged_assets=True
        )

    def _assert_valid_cleanup(self):
        inspection = json.dumps([
            {"Config": {"Labels": {ATTEMPT_LABEL: ATTEMPT}}}
        ])
        results = iter((inspection, "", ""))
        with (
            patch.object(
                subprocess,
                "Popen",
                side_effect=lambda argv, **kwargs: docker_process(
                    subprocess.CompletedProcess(argv, 0, next(results)),
                    kwargs["stdout"],
                ),
            ) as cleanup,
            redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(0, candidate_image_main(self.cleanup_command()))
        self.assertEqual("", output.getvalue())
        self.assertEqual(
            ["docker", "image", "inspect", IMAGE],
            cleanup.call_args_list[0].args[0],
        )
        self.assertEqual(self.root, cleanup.call_args_list[0].kwargs["cwd"])

    def _assert_invalid_paths_do_not_reach_docker(self):
        outside = self.root / "outside"
        outside.mkdir()
        link = self.scratch.parent / "link"
        link.symlink_to(outside, target_is_directory=True)
        for argv in self._invalid_cli_inputs(outside, link):
            with (
                self.subTest(argv=argv),
                redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
                patch.object(
                    subprocess,
                    "Popen",
                    side_effect=AssertionError(
                        "invalid CLI input must not reach Docker"
                    ),
                ),
            ):
                candidate_image_main(argv)

    def _invalid_cli_inputs(self, outside, link):
        return (
            [
                "build",
                "--project-root",
                str(self.root),
                "--scratch",
                str(link),
                "--attempt",
                ATTEMPT,
            ],
            [
                "build",
                "--project-root",
                str(self.root),
                "--scratch",
                str(outside),
                "--attempt",
                ATTEMPT,
            ],
            [
                "cleanup",
                "--project-root",
                str(self.root),
                "--image",
                "latest",
                "--attempt",
                ATTEMPT,
            ],
            [
                "cleanup",
                "--project-root",
                str(self.root),
                "--image",
                IMAGE,
                "--attempt",
                "bad",
            ],
        )
