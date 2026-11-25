"""Prepare a real temporary Git checkout without touching the source repository."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import read_release_selection


_CLI = Path(__file__).resolve().parents[2] / "release.py"
_MANIFEST = "AN-S-1-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
_CLAIM = """---
atom_family: SPEC
atom_id: AN-S-1
container: {component: C00}
tier: -1
context: {template: project_manifest, lens: SPEC}
state: {status: active, version: 1}
---

## Summary

Declare Anechoic

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name='Project Manifest', instance=ProjectManifest(
    name='Anechoic', prefix='AN',
    parameters={'note': 'préfixé', 'project_mcp': {'http_port': 35001}, 'shared_mcp': {'http_port': 35001}},
))
```

## Example

```python
ProjectManifest(parameters={'project_mcp': {'http_port': 35001}})
```
"""


def _git(root, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_OPTIONAL_LOCKS="0")
    return subprocess.run(("git", "-c", f"core.hooksPath={os.devnull}", *args), cwd=root, env=env,
                          capture_output=True, check=True, timeout=30).stdout


class PrepareLocalTests(unittest.TestCase):
    def setUp(self):
        parent = Path(self.enterContext(TemporaryDirectory(prefix="ane-prepare-test-"))).resolve()
        self.root = parent / "source"
        self.root.mkdir()
        self.scratch = parent / "temporary"
        self.scratch.mkdir()
        (self.root / "_anechoic_anechoic").mkdir()
        (self.root / "_anechoic_anechoic/control.txt").write_text("control", encoding="utf-8")
        (self.root / _MANIFEST).write_text(_CLAIM, encoding="utf-8")
        for name in ("edit.txt", "delete.txt", "unrelated.txt"):
            (self.root / name).write_text("base", encoding="utf-8")
        _git(self.root, "init", "--quiet", "--template=")
        _git(self.root, "config", "user.name", "Anechoic Test")
        _git(self.root, "config", "user.email", "anechoic-test@example.invalid")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "--quiet", "-m", "base")
        self.base = _git(self.root, "rev-parse", "HEAD").decode().strip()

    def prepare(self, run_id, paths, *, port=39002, base=None):
        argv = [sys.executable, "-B", str(_CLI), "prepare-local", "--project-root", str(self.root),
                "--run-id", run_id, "--base", base or self.base, "--port", str(port)]
        for path in paths:
            argv.extend(("--changed-path", path))
        result = subprocess.run(argv, env={**os.environ, "TMPDIR": str(self.scratch)},
                                capture_output=True, timeout=60)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        reply = json.loads(result.stdout)
        self.assertEqual(result.returncode == 0, reply.get("outcome") == "completed", reply)
        return reply

    def test_cli_pins_only_requested_bytes_and_preserves_source_git(self):
        (self.root / "later.txt").write_text("later commit", encoding="utf-8")
        _git(self.root, "add", "--", "later.txt")
        _git(self.root, "commit", "--quiet", "-m", "unselected commit")
        (self.root / "unrelated.txt").write_text("unrelated staged", encoding="utf-8")
        _git(self.root, "add", "--", "unrelated.txt")
        (self.root / "edit.txt").write_text("requested edit", encoding="utf-8")
        (self.root / "delete.txt").unlink()
        addition = self.root / "literal[1].md"
        addition.write_bytes(b"explicit addition")
        addition.chmod(0o755)
        (self.root / ".env.local").write_text("ignored fixture value", encoding="utf-8")
        source_head, source_index = _git(self.root, "rev-parse", "HEAD"), (self.root / ".git/index").read_bytes()
        prepared = self.prepare("prepare-1", ("edit.txt", "delete.txt", addition.name))
        self.assertEqual("completed", prepared["outcome"], prepared)
        checkout = Path(prepared["project_root"])
        self.assertFalse(checkout.is_relative_to(self.root))
        self.assertEqual(0o700, checkout.parent.stat().st_mode & 0o777)
        self.assertEqual(prepared["revision"], _git(checkout, "rev-parse", "HEAD").decode().strip())
        self.assertEqual(self.base, _git(checkout, "rev-parse", "HEAD^").decode().strip())
        self.assertEqual(b"", _git(checkout, "status", "--porcelain"))
        self.assertEqual(b"", _git(checkout, "remote"))
        self.assertEqual({"edit.txt", "delete.txt", addition.name, _MANIFEST},
                         set(_git(checkout, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").decode().splitlines()))
        self.assertEqual(b"requested edit", (checkout / "edit.txt").read_bytes())
        self.assertEqual(b"explicit addition", (checkout / addition.name).read_bytes())
        self.assertEqual(0o755, (checkout / addition.name).stat().st_mode & 0o777)
        self.assertEqual(b"base", (checkout / "unrelated.txt").read_bytes())
        for name in ("delete.txt", "later.txt", ".env.local"):
            self.assertFalse((checkout / name).exists())
        selection = read_release_selection(checkout)
        self.assertEqual(39002, selection.parameters["project_mcp"]["http_port"])
        self.assertEqual(35001, selection.parameters["shared_mcp"]["http_port"])
        self.assertIn("ProjectManifest(parameters={'project_mcp': {'http_port': 35001}})",
                      (checkout / _MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(prepared["manifest_sha256"], sha256((checkout / _MANIFEST).read_bytes()).hexdigest())
        self.assertEqual(_CLAIM, (self.root / _MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(source_head, _git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(source_index, (self.root / ".git/index").read_bytes())

    def test_refuses_unsafe_scope_and_existing_stage(self):
        (self.root / "link").symlink_to(self.root / "edit.txt")
        (self.root / "link-parent").symlink_to(self.root / "_anechoic_anechoic", target_is_directory=True)
        target = self.scratch / f"anechoic-local-release-{os.getuid()}" / "prepare-2"
        for path in ("../edit.txt", ".git/index", "nested/.env.stage", "link", "link-parent/control.txt"):
            with self.subTest(path=path):
                refusal = self.prepare("prepare-2", (path,))
                self.assertEqual("failed", refusal["outcome"], refusal)
                self.assertIn(str(target / "checkout"), refusal["error"])
                self.assertFalse(target.exists())
        wrong_port = self.prepare("prepare-2", ("edit.txt",), port=35001)
        self.assertIn("prepare-local-port-matches-source", wrong_port["error"])
        symbolic_revision = self.prepare("prepare-2", ("edit.txt",), base="HEAD")
        self.assertIn("prepare-local-base-invalid", symbolic_revision["error"])
        target.mkdir()
        (target / "owned-by-other-run").touch()
        duplicate = self.prepare("prepare-2", ("edit.txt",))
        self.assertIn("prepare-local-target-exists", duplicate["error"])
        self.assertTrue((target / "owned-by-other-run").is_file())
