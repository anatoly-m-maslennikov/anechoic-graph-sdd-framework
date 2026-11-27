"""Check phase fingerprints for sealed and direct Local Releases."""

from hashlib import file_digest
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    phase_inputs,
)


_ENGINE = Path("LAYER_4_ENGINE_STUDIO_C14")
_CANARY = (
    _ENGINE / "FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/_release_canary.py"
)
_MCP = _ENGINE / "MCP_PATCHBAY_C21/FEATURE_MCP"
_IMAGE = _MCP / "FEATURE_MCP__tests/image/test_packaged_boundary_docker_e2e.py"
_RUNTIME = _MCP / "docker/start_mcp.py"


class ReleasePhaseInputsTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()

    def git(self, *args):
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        environment.update(
            GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1"
        )
        options = (
            "-c",
            f"core.hooksPath={os.devnull}",
            "-c",
            "user.name=Release fixture",
            "-c",
            "user.email=release@example.invalid",
            "-c",
            "commit.gpgsign=false",
        )
        return subprocess.run(
            ("git", *options, *args),
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.strip()

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "--verify", "HEAD")

    def write(self, path, text, *, root=None):
        target = (root or self.root) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def test_scopes_direct_changes_and_ignores_release_outputs(self):
        recorded = phase_inputs(self.root, self.root)
        self.write(Path("version.toml"), "version change")
        self.write(Path(".agents/skills/ane/SKILL.md"), "owned skill")
        self.write(Path("LAYER_1_META_ONTOLOGY_C9/atom.md"), "copied product")
        self.write(
            Path(
                (
                    ".anechoic_runtime/simple_local_release/runs/example/state"
                    ".json"
                )
            ),
            "journal",
        )
        self.assertEqual(recorded, phase_inputs(self.root, self.root))
        for path, domain in (
            (_CANARY, "canary"),
            (_IMAGE, "image"),
            (_RUNTIME, "runtime"),
        ):
            with self.subTest(domain=domain):
                self.write(path, "source change")
                current = phase_inputs(self.root, self.root)
                self.assertEqual(
                    {domain},
                    {
                        name
                        for name in recorded
                        if recorded[name] != current[name]
                    },
                )
                recorded = current

    def test_treats_external_runner_inputs_as_shared(self):
        runner = Path(self.enterContext(TemporaryDirectory()))
        recorded = phase_inputs(self.root, runner)
        self.write(_CANARY, "runner change", root=runner)
        current = phase_inputs(self.root, runner)
        self.assertEqual(
            {"runtime"},
            {name for name in recorded if recorded[name] != current[name]},
        )
        self.assertEqual(
            phase_inputs(self.root, self.root),
            phase_inputs(self.root, runner, external=False),
        )

    def test_environment_change_preserves_source_fingerprints(self):
        recorded = phase_inputs(self.root, self.root)
        with patch.dict(
            os.environ, {"ANECHOIC_TEST_FANOUT": "phase-input-test"}
        ):
            current = phase_inputs(self.root, self.root)
        self.assertEqual(
            {"environment"},
            {name for name in recorded if recorded[name] != current[name]},
        )

    def test_reuses_hash_only_while_file_witness_matches(self):
        path = self.root / "source.py"
        cache = {}
        path.write_bytes(b"one")
        before = path.stat()
        with patch("os.open", wraps=os.open) as opened:
            first = phase_inputs(self.root, self.root, cache=cache)
            self.assertEqual(
                first, phase_inputs(self.root, self.root, cache=cache)
            )
            self.assertEqual(
                [path], [call.args[0] for call in opened.call_args_list]
            )
            path.write_bytes(b"two")
            os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
            self.assertEqual(before.st_mtime_ns, path.stat().st_mtime_ns)
            second = phase_inputs(self.root, self.root, cache=cache)
            self.assertNotEqual(first["runtime"], second["runtime"])
            self.assertEqual(
                [path, path], [call.args[0] for call in opened.call_args_list]
            )
            path.unlink()
            third = phase_inputs(self.root, self.root, cache=cache)
        self.assertNotEqual(second["runtime"], third["runtime"])
        self.assertEqual({}, cache)

    def test_rejects_file_change_while_hashing(self):
        path = self.root / "source.py"
        path.write_bytes(b"original content")

        def digest_and_mutate(stream, algorithm):
            digest = file_digest(stream, algorithm)
            path.write_bytes(b"changed during fingerprint")
            return digest

        cache = {}
        with patch(
            "LAYER_2_LOCAL_RELEASE_C63.release_phase_inputs.file_digest",
            side_effect=digest_and_mutate,
        ):
            with self.assertRaisesRegex(
                LocalReleaseError, "local-release-source-changed"
            ):
                phase_inputs(self.root, self.root, cache=cache)
        self.assertEqual({}, cache)

    def test_rejects_file_removed_after_inventory(self):
        path = self.root / "source.py"
        path.write_bytes(b"original content")
        open_file = os.open

        def remove_before_open(candidate, flags):
            if candidate == path:
                path.unlink()
            return open_file(candidate, flags)

        with patch("os.open", side_effect=remove_before_open):
            with self.assertRaisesRegex(
                LocalReleaseError, "local-release-source-changed"
            ):
                phase_inputs(self.root, self.root, cache={})

    def test_fingerprints_pinned_git_modes_and_blobs_without_reading_worktree(
        self,
    ):
        self.git("init", "--quiet", "--template=")
        self.write(_CANARY, "pinned bytes")
        revision = self.commit("Base")
        cache = {}
        original = phase_inputs(
            self.root, self.root, revision=revision, cache=cache
        )
        self.write(_CANARY, "irrelevant worktree change")
        self.assertEqual(
            original,
            phase_inputs(self.root, self.root, revision=revision, cache=cache),
        )
        self.write(_CANARY, "pinned bytes")
        (self.root / _CANARY).chmod(0o755)
        changed_mode = self.commit("Change file mode")
        self.assertEqual(
            original, phase_inputs(self.root, self.root, revision=revision)
        )
        current = phase_inputs(self.root, self.root, revision=changed_mode)
        self.assertEqual(
            {"canary"},
            {name for name in original if original[name] != current[name]},
        )
        self.assertEqual({}, cache)

    def test_rejects_unsafe_git_entries(self):
        self.git("init", "--quiet", "--template=")
        (self.root / "source.py").symlink_to("unsafe")
        revision = self.commit("Track unresolved symlink")
        with self.assertRaisesRegex(
            LocalReleaseError, "local-release-source-entry-unsafe"
        ):
            phase_inputs(self.root, self.root, revision=revision)
