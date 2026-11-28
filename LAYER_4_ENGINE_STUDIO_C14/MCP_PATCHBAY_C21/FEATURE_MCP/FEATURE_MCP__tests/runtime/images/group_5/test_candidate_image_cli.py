"""Exercise the existing source builder with a fixture-only Docker executor."""

from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from MCP_PATCHBAY_C21.FEATURE_MCP.docker import (
    docker__shared as runtime_images,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    _REQUIRED,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.cli.cli__shared import (
    candidate_image_main,
)
from ..group_3.candidate_image_cli_cases import ATTEMPT
from ..group_3.candidate_image_cli_cases import ATTEMPT_LABEL
from ..group_3.candidate_image_cli_cases import FRAMEWORK_VERSION
from ..group_3.candidate_image_cli_cases import IMAGE
from ..group_3.candidate_image_cli_cases import _CandidateImageCases
from ..group_3.candidate_image_cli_cases import docker_process


class CurrentSourceImageBuildTests(_CandidateImageCases, unittest.TestCase):
    def setUp(self):
        parent = (
            Path(__file__).resolve().parents[7]
            / ".anechoic_tmp/tests/image-build"
        )
        parent.mkdir(parents=True, exist_ok=True)
        directory = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for relative in (
            *_REQUIRED,
            *(
                f"{layer}/AN-S-1-source.md"
                for layer in (
                    "LAYER_1_META_ONTOLOGY_C9",
                    "LAYER_2_META_METHODOLOGY_C58",
                )
            ),
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            content = (
                f'[framework]\nversion = "{FRAMEWORK_VERSION}"\n'
                if relative == "version.toml"
                else "fixture-current-code"
            )
            path.write_text(content, encoding="utf-8")
        self.scratch = (
            self.root
            / ".anechoic_tmp/tests/full-suite-integration/attempt-test"
        )
        self.scratch.mkdir(parents=True)

    def build_command(self, *extra):
        return [
            "build",
            "--project-root",
            str(self.root),
            "--attempt",
            ATTEMPT,
            "--scratch",
            str(self.scratch),
            *extra,
        ]

    def cleanup_command(self):
        return [
            "cleanup",
            "--project-root",
            str(self.root),
            "--attempt",
            ATTEMPT,
            "--image",
            IMAGE,
        ]

    def test_executor_labels_only_build_and_uses_bounded_runner(self):
        with (
            patch.object(
                subprocess,
                "Popen",
                return_value=docker_process(
                    subprocess.CompletedProcess([], 0, ""), None
                ),
            ) as execute,
            patch.object(runtime_images, "ImageManager") as manager,
            redirect_stdout(io.StringIO()),
        ):
            manager.return_value._build.return_value = IMAGE
            self.assertEqual(0, candidate_image_main(self.build_command()))
            executor = manager.call_args.kwargs["executor"]
            executor(
                ["docker", "build", "--file", "Dockerfile", "context"],
                cwd=self.root,
                timeout=600,
                env={"BUILDX_CONFIG": "private-buildx"},
            )
        self.assertEqual(
            [
                "docker",
                "build",
                "--label",
                f"{ATTEMPT_LABEL}={ATTEMPT}",
                "--file",
                "Dockerfile",
                "context",
            ],
            execute.call_args.args[0],
        )
        self.assertEqual(
            subprocess.DEVNULL, execute.call_args.kwargs["stdout"]
        )
        self.assertEqual(
            "private-buildx", execute.call_args.kwargs["env"]["BUILDX_CONFIG"]
        )

    def test_attributed_cleanup_is_non_force_and_does_not_touch_containers(
        self,
    ):
        inspection = json.dumps([
            {"Config": {"Labels": {ATTEMPT_LABEL: ATTEMPT}}}
        ])
        results = iter((inspection, "", ""))
        with patch.object(
            subprocess,
            "Popen",
            side_effect=lambda argv, **kwargs: docker_process(
                subprocess.CompletedProcess(argv, 0, next(results)),
                kwargs["stdout"],
            ),
        ) as execute:
            self.assertEqual(0, candidate_image_main(self.cleanup_command()))
        commands = [call.args[0] for call in execute.call_args_list]
        self.assertEqual(["docker", "image", "rm", IMAGE], commands[-1])
        self.assertFalse(
            any(
                "--force" in command or "down" in command
                for command in commands
            )
        )

    def test_in_use_or_unattributed_image_is_retained(self):
        for label, containers in (
            ("other", ""),
            (ATTEMPT, "existing-container"),
        ):
            inspection = json.dumps([
                {"Config": {"Labels": {ATTEMPT_LABEL: label}}}
            ])
            results = iter((inspection, containers))
            with (
                patch.object(
                    subprocess,
                    "Popen",
                    side_effect=lambda argv, **kwargs: docker_process(
                        subprocess.CompletedProcess(argv, 0, next(results)),
                        kwargs["stdout"],
                    ),
                ) as execute,
                redirect_stderr(io.StringIO()) as errors,
            ):
                self.assertEqual(
                    0, candidate_image_main(self.cleanup_command())
                )
            self.assertIn("Test image cleanup", errors.getvalue())
            self.assertFalse(
                any(
                    call.args[0][:3] == ["docker", "image", "rm"]
                    for call in execute.call_args_list
                )
            )


if __name__ == "__main__":
    unittest.main()
