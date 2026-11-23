"""Exercise the existing source builder with a fixture-only Docker executor."""

from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from MCP_PATCHBAY_C21.FEATURE_MCP.docker import candidate_image_cli as docker
from MCP_PATCHBAY_C21.FEATURE_MCP.docker import docker__shared as runtime_images
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import DOCKERFILE, _REQUIRED
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import FINGERPRINT_LABEL, SCHEMA_LABEL

IMAGE = "sha256:" + "a" * 64
FRAMEWORK_VERSION = "0.4.4.9"


class CurrentSourceImageBuildTests(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[4] / ".anechoic_tmp/tests/image-build"
        parent.mkdir(parents=True, exist_ok=True)
        directory = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for relative in (*_REQUIRED, *(f"{layer}/AN-S-1-source.md" for layer in
                          ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58"))):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            content = (
                f'[framework]\nversion = "{FRAMEWORK_VERSION}"\n'
                if relative == "version.toml" else "fixture-current-code"
            )
            path.write_text(content, encoding="utf-8")

    def _build_executor(self, labels, commands, tags):
        def execute(argv, **_kwargs):
            commands.append(argv)
            if argv[:3] == ["docker", "image", "tag"]:
                tags.add(argv[-1])
                return subprocess.CompletedProcess(argv, 0, "")
            if argv[:3] == ["docker", "image", "inspect"] and argv[-1].startswith("anechoic-runtime:"):
                if argv[-1] not in tags:
                    return subprocess.CompletedProcess(argv, 1, "")
                return subprocess.CompletedProcess(
                    argv, 0, json.dumps([{"Id": IMAGE, "Created": "2026-10-21T14:15:16.987654321Z",
                                          "RepoTags": [argv[-1]], "Config": {"Labels": labels},
                                          "Os": "linux", "Architecture": "arm64"}])
                )
            if argv[:2] == ["docker", "build"]:
                for index, argument in enumerate(argv):
                    if argument == "--label":
                        key, value = argv[index + 1].split("=", 1)
                        labels[key] = value
                context = Path(argv[-1])
                self.assertEqual("fixture-current-code", (context / DOCKERFILE).read_text())
                Path(argv[argv.index("--iidfile") + 1]).write_text(IMAGE)
                return subprocess.CompletedProcess(argv, 0, "")
            if argv[:3] == ["docker", "image", "inspect"]:
                value = {
                    "Id": IMAGE,
                    "Created": "2026-10-21T14:15:16.987654321Z",
                    "RepoTags": [],
                    "Config": {"Labels": labels},
                    "Os": "linux",
                    "Architecture": "arm64"
                    if docker.ImageManager(self.root, project_root=self.root).platform == "linux/arm64"
                    else "amd64",
                }
                return subprocess.CompletedProcess(argv, 0, json.dumps([value]))
            return subprocess.CompletedProcess(argv, 0, "")

        return execute

    def test_real_builder_copies_current_bytes_and_passes_actual_immutable_id(self):
        labels, commands, tags = {}, [], set()

        execute = self._build_executor(labels, commands, tags)

        with (
            patch.object(docker, "_bounded_run", side_effect=execute),
            patch.object(runtime_images, "_compile_tool_registry", return_value=b'{"schema_version":1}\n'),
            patch.object(runtime_images.ImageManager, "_refresh_model", return_value="a" * 64),
        ):
            scratch = self.root / ".anechoic_tmp/tests/full-suite-integration/attempt-test"
            scratch.mkdir(parents=True)
            attempt = "a" * 32
            self.assertEqual(IMAGE, docker._build_image(self.root, scratch, attempt, use_packaged_assets=False))
            docker._remove_owned_image(self.root, IMAGE, attempt)
        self.assertEqual("1", labels[SCHEMA_LABEL])
        self.assertEqual(64, len(labels[FINGERPRINT_LABEL]))
        self.assertEqual(FRAMEWORK_VERSION, labels["org.opencontainers.image.version"])
        self.assertEqual(32, len(labels[docker.ATTEMPT_LABEL]))
        self.assertEqual(1, sum(argv[:2] == ["docker", "build"] for argv in commands))
        self.assertEqual(["docker", "image", "rm", IMAGE], commands[-1])
        expected = "anechoic-runtime:0.4.4.9-test-2026-10-21_14-15-16Z-aaaaaaaaaaaa"
        self.assertEqual(["docker", "image", "tag", IMAGE, expected],
                         next(argv for argv in commands if argv[:3] == ["docker", "image", "tag"]))
        self.assertEqual([expected], [argv[-1] for argv in commands
                                      if argv[:3] == ["docker", "image", "ls"]])

    def test_cli_validates_paths_and_immutable_image(self):
        from contextlib import redirect_stderr, redirect_stdout
        import io

        scratch = self.root / ".anechoic_tmp/tests/full-suite-integration/attempt-test"
        scratch.mkdir(parents=True)
        attempt = "a" * 32
        with patch.object(docker, "_build_image", return_value=IMAGE) as build, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(0, docker.main(["build", "--project-root", str(self.root), "--scratch", str(scratch), "--attempt", attempt, "--packaged-assets"]))
        self.assertEqual(IMAGE + "\n", output.getvalue())
        build.assert_called_once_with(self.root, scratch, attempt, use_packaged_assets=True)
        with patch.object(docker, "_remove_owned_image") as cleanup, redirect_stdout(io.StringIO()) as output:
            self.assertEqual(0, docker.main(["cleanup", "--project-root", str(self.root), "--image", IMAGE, "--attempt", attempt]))
        self.assertEqual("", output.getvalue())
        cleanup.assert_called_once_with(self.root, IMAGE, attempt)
        outside = self.root / "outside"
        outside.mkdir()
        link = scratch.parent / "link"
        link.symlink_to(outside, target_is_directory=True)
        for argv in (
            ["build", "--project-root", str(self.root), "--scratch", str(link), "--attempt", attempt],
            ["build", "--project-root", str(self.root), "--scratch", str(outside), "--attempt", attempt],
            ["cleanup", "--project-root", str(self.root), "--image", "latest", "--attempt", attempt],
            ["cleanup", "--project-root", str(self.root), "--image", IMAGE, "--attempt", "bad"],
        ):
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                docker.main(argv)

    def test_executor_labels_only_build_and_uses_bounded_runner(self):
        with patch.object(docker, "_bounded_run") as execute:
            docker._executor("unique-attempt")(
                ["docker", "build", "--file", "Dockerfile", "context"],
                cwd=self.root, timeout=600, env={"BUILDX_CONFIG": "private-buildx"},
            )
        self.assertEqual(
            ["docker", "build", "--label", f"{docker.ATTEMPT_LABEL}=unique-attempt",
             "--file", "Dockerfile", "context"], execute.call_args.args[0],
        )
        self.assertFalse(execute.call_args.kwargs["capture_stdout"])
        self.assertEqual("private-buildx", execute.call_args.kwargs["buildx_config"])

    def test_attributed_cleanup_is_non_force_and_does_not_touch_containers(self):
        inspection = json.dumps([{"Config": {"Labels": {docker.ATTEMPT_LABEL: "ours"}}}])
        results = [subprocess.CompletedProcess([], 0, inspection),
                   subprocess.CompletedProcess([], 0, ""), subprocess.CompletedProcess([], 0, "")]
        with patch.object(docker, "_bounded_run", side_effect=results) as execute:
            docker._remove_owned_image(self.root, IMAGE, "ours")
        commands = [call.args[0] for call in execute.call_args_list]
        self.assertEqual(["docker", "image", "rm", IMAGE], commands[-1])
        self.assertFalse(any("--force" in command or "down" in command for command in commands))

    def test_in_use_or_unattributed_image_is_retained(self):
        from contextlib import redirect_stderr
        import io

        for label, containers in (("other", ""), ("ours", "existing-container")):
            inspection = json.dumps([{"Config": {"Labels": {docker.ATTEMPT_LABEL: label}}}])
            results = [subprocess.CompletedProcess([], 0, inspection), subprocess.CompletedProcess([], 0, containers)]
            with patch.object(docker, "_bounded_run", side_effect=results) as execute, redirect_stderr(io.StringIO()) as errors:
                docker._remove_owned_image(self.root, IMAGE, "ours")
            self.assertIn("Test image cleanup", errors.getvalue())
            self.assertFalse(any(call.args[0][:3] == ["docker", "image", "rm"] for call in execute.call_args_list))


if __name__ == "__main__":
    unittest.main()
