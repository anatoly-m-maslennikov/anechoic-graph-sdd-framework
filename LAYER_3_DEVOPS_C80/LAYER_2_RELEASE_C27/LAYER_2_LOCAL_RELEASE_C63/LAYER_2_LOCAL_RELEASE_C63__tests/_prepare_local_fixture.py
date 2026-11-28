"Prepare a real temporary Git checkout without touching the source repository."

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)


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
    parameters={'note': 'préfixé', 'project_mcp': {'http_port': 35001}, \
'shared_mcp': {'http_port': 35001}},
))
```

## Example

```python
ProjectManifest(parameters={'project_mcp': {'http_port': 35001}})
```
"""


def _git(root, *args):
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    env.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_OPTIONAL_LOCKS="0",
    )
    return subprocess.run(
        ("git", "-c", f"core.hooksPath={os.devnull}", *args),
        cwd=root,
        env=env,
        capture_output=True,
        check=True,
        timeout=30,
    ).stdout


class PrepareLocalFixture:
    def setUp(self):
        parent = Path(
            self.enterContext(TemporaryDirectory(prefix="ane-prepare-test-"))
        ).resolve()
        self.root = parent / "source"
        self.root.mkdir()
        self.scratch = parent / "temporary"
        self.scratch.mkdir()
        (self.root / "_anechoic_anechoic").mkdir()
        (self.root / "_anechoic_anechoic/control.txt").write_text(
            "control", encoding="utf-8"
        )
        (self.root / _MANIFEST).write_text(_CLAIM, encoding="utf-8")
        for name in ("edit.txt", "delete.txt", "unrelated.txt"):
            (self.root / name).write_text("base", encoding="utf-8")
        (self.root / "version.toml").write_text(
            '[framework]\nversion = "1.2.3"\n'
        )
        _git(self.root, "init", "--quiet", "--template=")
        _git(self.root, "config", "user.name", "Anechoic Test")
        _git(
            self.root, "config", "user.email", "anechoic-test@example.invalid"
        )
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "--quiet", "-m", "base")
        self.base = _git(self.root, "rev-parse", "HEAD").decode().strip()

    def prepare(self, run_id, paths, *, port=39002, base=None):
        argv = [
            sys.executable,
            "-B",
            str(_CLI),
            "prepare-local",
            "--project-root",
            str(self.root),
            "--run-id",
            run_id,
            "--base",
            base or self.base,
            "--port",
            str(port),
        ]
        for path in paths:
            argv.extend(("--changed-path", path))
        result = subprocess.run(
            argv,
            env={**os.environ, "TMPDIR": str(self.scratch)},
            capture_output=True,
            timeout=60,
        )
        self.assertIn(result.returncode, (0, 1), result.stderr)
        reply = json.loads(result.stdout)
        self.assertEqual(
            result.returncode == 0, reply.get("outcome") == "completed", reply
        )
        return reply

    def assert_prepared_selection(
        self, prepared, checkout, source_head, source_index
    ):
        selection = read_release_selection(checkout)
        self.assertEqual(
            39002, selection.parameters["project_mcp"]["http_port"]
        )
        self.assertEqual(
            35001, selection.parameters["shared_mcp"]["http_port"]
        )
        self.assertIn(
            "ProjectManifest(parameters={'project_mcp': "
            "{'http_port': 35001}})",
            (checkout / _MANIFEST).read_text(encoding="utf-8"),
        )
        self.assertEqual(
            prepared["manifest_sha256"],
            sha256((checkout / _MANIFEST).read_bytes()).hexdigest(),
        )
        self.assertEqual(
            _CLAIM, (self.root / _MANIFEST).read_text(encoding="utf-8")
        )
        self.assertEqual(source_head, _git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(source_index, (self.root / ".git/index").read_bytes())

    def assert_prepared_checkout(self, prepared, checkout, addition):
        self.assertFalse(checkout.is_relative_to(self.root))
        self.assertEqual(0o700, checkout.parent.stat().st_mode & 0o777)
        self.assertEqual(
            prepared["revision"],
            _git(checkout, "rev-parse", "HEAD").decode().strip(),
        )
        self.assertEqual(
            self.base, _git(checkout, "rev-parse", "HEAD^").decode().strip()
        )
        self.assertEqual(b"", _git(checkout, "status", "--porcelain"))
        self.assertEqual(b"", _git(checkout, "remote"))
        self.assertEqual(
            {"edit.txt", "delete.txt", addition.name, _MANIFEST},
            set(
                _git(
                    checkout,
                    "diff-tree",
                    "--no-commit-id",
                    "--name-only",
                    "-r",
                    "HEAD",
                )
                .decode()
                .splitlines()
            ),
        )
        self.assertEqual(
            b"requested edit", (checkout / "edit.txt").read_bytes()
        )
        self.assertEqual(
            b"explicit addition", (checkout / addition.name).read_bytes()
        )
        self.assertEqual(
            0o755, (checkout / addition.name).stat().st_mode & 0o777
        )
        self.assertEqual(b"base", (checkout / "unrelated.txt").read_bytes())
        for name in ("delete.txt", "later.txt", ".env.local"):
            self.assertFalse((checkout / name).exists())
