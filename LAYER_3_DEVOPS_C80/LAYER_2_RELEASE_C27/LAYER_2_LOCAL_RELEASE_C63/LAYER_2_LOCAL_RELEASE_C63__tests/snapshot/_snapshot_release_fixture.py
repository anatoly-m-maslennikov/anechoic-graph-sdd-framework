"""Explicit-target Local Release checks with real Git and simulated Docker."""

from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_snapshot_release,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests import (
    LAYER_2_LOCAL_RELEASE_C63__tests__shared as shared,
)


_SUITE = Path(
    (
        "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
        "FEATURE_PROJECT_TOOLS/test"
        "_suite__pub.py"
    )
)
_MANIFEST = Path(".anechoic_anechoic/AN-S-001-PROJECT_MANIFEST--declare.md")
_ANE = Path(".agents/skills/ane/SKILL.md")
_SETTINGS = Path(".anechoic_runtime/anechoic_runtime_settings.toml")


class SnapshotReleaseFixture(shared.SimpleReleaseFixture):
    def setUp(self):
        super().setUp()
        temporary = self.enterContext(TemporaryDirectory())
        self.source = Path(temporary).resolve()
        shutil.copytree(self.root, self.source, dirs_exist_ok=True)
        (self.source / _SUITE).parent.mkdir(parents=True)
        (self.source / _SUITE).write_text("# tool from sealed checkout\n")
        (self.source / "version.toml").write_text(
            '[framework]\nversion = "0.4.2"\n'
        )
        (self.source / _MANIFEST).write_text(
            (self.source / _MANIFEST).read_text().replace("12345", "54321")
        )
        (self.source / ".gitignore").write_text(
            (self.source / ".gitignore").read_text() + "ignored-local.txt\n"
        )
        relative = self.native_sources[0].relative_to(self.root)
        authored = (
            (self.source / relative)
            .read_text()
            .replace("Native source", "Source checkout active spec")
        )
        (self.source / relative).write_text(authored)
        self.target_layer = self.root / "LAYER_1_META_ONTOLOGY_C9"
        self.target_layer.mkdir()
        self.target_marker = self.target_layer / "local-authoring.txt"
        self.target_marker.write_text("target authoring\n")
        (self.root / _ANE).parent.mkdir(parents=True)
        (self.root / _ANE).write_text("previous tracked skill\n")
        self.source_revision, self.target_revision = [
            self.initialize_git(root) for root in (self.source, self.root)
        ]
        self.calls = []
        self.fail_phase = None
        self.on_image = None
        self.legacy_runtime = None
        self.target_manifest = (self.root / _MANIFEST).read_bytes()

    def git(self, root, *args):
        return subprocess.run(
            (
                "git",
                "-c",
                "user.name=Release Test",
                "-c",
                "user.email=release@example.invalid",
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                "commit.gpgSign=false",
                *args,
            ),
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    def initialize_git(self, root):
        self.git(root, "init", "-q")
        self.git(root, "add", "-A")
        self.git(root, "commit", "-qm", "Fixture")
        return self.git(root, "rev-parse", "HEAD").strip()

    def run_command(self, argv, cwd):
        self.assertNotEqual(
            "git", argv[0], "release runner must not invoke Git"
        )
        if "--phase" not in argv:
            self.assertEqual(self.root, cwd)
            return subprocess.CompletedProcess(argv, 0, "", "")
        phase = argv[argv.index("--phase") + 1]
        self.calls.append((phase, argv))
        self.assertEqual(self.source, cwd)
        self.assertIn(str(self.source / _SUITE), argv)
        self.assertIn(
            ("--project-root", str(self.source)),
            tuple(zip(argv, argv[1:], strict=False)),
        )
        output = ""
        if phase in {"image-tests", "canary"}:
            self.assertEqual(
                self.image_id, argv[argv.index("--candidate-image") + 1]
            )
        if phase == "image-tests" and self.on_image is not None:
            self.on_image()
        if phase == "canary":
            self.assert_release_gate(argv)
            output = (
                "ANECHOIC_CANARY_ENDPOINT "
                "http://127.0.0.1:49152/anechoic/mcp\n"
            )
        return subprocess.CompletedProcess(
            argv, int(self.fail_phase == phase), output, ""
        )

    def assert_release_gate(self, argv):
        self.assertEqual(
            self.image_id, argv[argv.index("--candidate-image") + 1]
        )
        self.assertIn(
            ("--canary-project-root", str(self.root)),
            tuple(zip(argv, argv[1:], strict=False)),
        )
        handoff = json.loads(argv[argv.index("--canary-selection") + 1])
        self.assertEqual(_MANIFEST.as_posix(), handoff["manifest_path"])
        settings = self.root / _SETTINGS
        digest = (
            sha256(settings.read_bytes()).hexdigest()
            if settings.exists()
            else None
        )
        self.assertEqual(digest, handoff["runtime_settings_sha256"])
        package = Path(argv[argv.index("--canary-package") + 1])
        self.assertTrue(
            package.is_relative_to(
                self.root / ".anechoic_tmp/simple_local_release"
            )
        )
        self.assertFalse((package / _MANIFEST).exists())
        self.assertFalse((package / "ignored-local.txt").exists())
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        if self.legacy_runtime is None:
            self.assertFalse(
                (self.runtime / "simple_local_release/package").exists()
            )
        else:
            self.assertEqual(
                "previous package", self.legacy_runtime.read_text()
            )

    def release(self, **overrides):
        options = dict(
            target_root=self.root,
            source_revision=self.source_revision,
            run_id="snapshot",
            runner=self.run_command,
        )
        return run_snapshot_release(self.source, **(options | overrides))

    def phases(self):
        return [phase for phase, _ in self.calls]

    def assert_git_unchanged(self):
        self.assertEqual(
            self.source_revision,
            self.git(self.source, "rev-parse", "HEAD").strip(),
        )
        self.assertEqual("", self.git(self.source, "status", "--porcelain"))
        self.assertEqual(
            self.target_revision,
            self.git(self.root, "rev-parse", "HEAD").strip(),
        )
        self.assertEqual(
            "", self.git(self.root, "diff", "--cached", "--name-only")
        )
        self.assertEqual(
            self.target_manifest, (self.root / _MANIFEST).read_bytes()
        )
        self.assertEqual("target authoring\n", self.target_marker.read_text())
        self.assertEqual(
            '[framework]\nversion = "0.4.1"\n',
            (self.root / "version.toml").read_text(),
        )
