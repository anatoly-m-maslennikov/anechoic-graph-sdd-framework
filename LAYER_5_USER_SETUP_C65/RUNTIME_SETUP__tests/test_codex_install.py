import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from RUNTIME_SETUP__tests.RUNTIME_SETUP__tests__shared import ROOT
from RUNTIME_SETUP__shared import HOOK_SOURCE, MATCHER, install_codex


ENDPOINT = "http://127.0.0.1:8765/mcp"


class FakeCodex:
    def __init__(self):
        self.calls = []

    def __call__(self, args, *, cwd, env, **kwargs):
        self.calls.append((args, cwd, env["CODEX_HOME"], kwargs))
        (cwd / "config.toml").write_text(
            '[mcp_servers.anechoic]\nurl = "' + args[-1] + '"\n',
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(args, 0)


class CodexInstallTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.uv_patch = patch.object(shutil, "which", return_value="/mock/uv")
        self.uv_patch.start()
        self.addCleanup(self.uv_patch.stop)

    def test_install_preserves_other_hooks_and_is_idempotent(self):
        home = self.root / "codex home"
        home.mkdir()
        original = {
            "description": "Keep me",
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Bash",
                        "hooks": [{"type": "command", "command": "echo keep"}],
                    }
                ],
                "Stop": [
                    {"hooks": [{"type": "command", "command": "echo stop"}]}
                ],
            },
        }
        (home / "hooks.json").write_text(
            json.dumps(original), encoding="utf-8"
        )
        fake = FakeCodex()
        first = install_codex(ROOT, ENDPOINT, codex_home=home, executor=fake)
        self.check_hooks(home, original)
        self.check_registration_call(fake, home)
        self.assertTrue(first["mcp_registered"])
        self.assertIn("/hooks", first["approval"])
        before = (home / "hooks.json").read_bytes()
        second = install_codex(ROOT, ENDPOINT, codex_home=home, executor=fake)
        self.assertFalse(
            any(
                second[key]
                for key in ("mcp_registered", "hook_changed", "hooks_changed")
            )
        )
        self.assertEqual((home / "hooks.json").read_bytes(), before)
        self.assertEqual(len(fake.calls), 1)

    def check_hooks(self, home, original):
        hooks = json.loads((home / "hooks.json").read_text())
        self.assertEqual(hooks["description"], original["description"])
        self.assertEqual(hooks["hooks"]["Stop"], original["hooks"]["Stop"])
        self.assertEqual(
            hooks["hooks"]["PreToolUse"][0], original["hooks"]["PreToolUse"][0]
        )
        group = hooks["hooks"]["PreToolUse"][1]
        self.assertEqual(group["matcher"], MATCHER)
        self.assertIn("--managed-python", group["hooks"][0]["command"])
        self.assertIn("--no-env-file", group["hooks"][0]["command"])
        self.assertEqual(
            (home / "anechoic" / "codex_hook.py").read_bytes(),
            (ROOT / HOOK_SOURCE).read_bytes(),
        )

    def check_registration_call(self, fake, home):
        self.assertEqual(
            fake.calls,
            [
                (
                    ["codex", "mcp", "add", "anechoic", "--url", ENDPOINT],
                    home,
                    str(home),
                    {
                        "check": True,
                        "capture_output": True,
                        "text": True,
                        "timeout": 30,
                    },
                )
            ],
        )

    def test_existing_matching_server_is_not_replaced(self):
        (self.root / "config.toml").write_text(
            '[mcp_servers.anechoic]\nurl = "' + ENDPOINT + '"\n',
            encoding="utf-8",
        )
        fake = FakeCodex()
        result = install_codex(
            ROOT, ENDPOINT, codex_home=self.root, executor=fake
        )
        self.assertFalse(result["mcp_registered"])
        self.assertFalse(fake.calls)

    def test_non_loopback_endpoint_rejected_before_writes(self):
        endpoints = [
            "https://example.com:8765/mcp",
            "http://127.0.0.1/mcp",
            "http://user@127.0.0.1:8765/mcp",
            "http://127.0.0.1:8765/mcp?x=1",
        ]
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                home = self.root / "home"
                with self.assertRaises(ValueError):
                    install_codex(
                        ROOT, endpoint, codex_home=home, executor=FakeCodex()
                    )
                self.assertFalse(home.exists())

    def test_server_conflict_preserves_existing_files(self):
        config = self.root / "config.toml"
        config.write_text(
            '[mcp_servers.anechoic]\nurl = "http://127.0.0.1:99/mcp"\n'
        )
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            install_codex(
                ROOT, ENDPOINT, codex_home=self.root, executor=FakeCodex()
            )
        self.assertFalse((self.root / "hooks.json").exists())
        self.assertIn("127.0.0.1:99", config.read_text())

    def test_symlink_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        for target in ("hooks.json", "config.toml", "anechoic"):
            with self.subTest(target=target):
                home = self.root / ("home-" + target)
                home.mkdir()
                (home / target).symlink_to(outside, target_is_directory=True)
                with self.assertRaisesRegex(ValueError, "Unsafe"):
                    install_codex(
                        ROOT, ENDPOINT, codex_home=home, executor=FakeCodex()
                    )
                self.assertEqual(list(outside.iterdir()), [])

    def test_conflicting_script_and_handler_are_not_overwritten(self):
        hook_dir = self.root / "anechoic"
        hook_dir.mkdir()
        script = hook_dir / "codex_hook.py"
        script.write_text("existing")
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            install_codex(
                ROOT, ENDPOINT, codex_home=self.root, executor=FakeCodex()
            )
        self.assertEqual(script.read_text(), "existing")
        script.unlink()
        hooks = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": MATCHER,
                        "hooks": [
                            {"type": "command", "command": f"python {script}"}
                        ],
                    }
                ]
            }
        }
        (self.root / "hooks.json").write_text(json.dumps(hooks))
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            install_codex(
                ROOT, ENDPOINT, codex_home=self.root, executor=FakeCodex()
            )
        self.assertEqual(
            json.loads((self.root / "hooks.json").read_text()), hooks
        )

    def test_real_codex_cli_and_hook_in_isolated_home(self):
        self.uv_patch.stop()
        uv = shutil.which("uv")
        if os.name == "nt" or not shutil.which("codex") or not uv:
            self.skipTest("requires Codex, uv and a POSIX shell")
        probe = subprocess.run(
            [uv, "python", "find", "--managed-python", "3.14"],
            capture_output=True,
            text=True,
        )
        if probe.returncode:
            self.skipTest("requires an installed uv-managed Python 3.14")
        result = install_codex(ROOT, ENDPOINT, codex_home=self.root)
        self.assertTrue(result["mcp_registered"])
        hooks = json.loads((self.root / "hooks.json").read_text())
        command = hooks["hooks"]["PreToolUse"][-1]["hooks"][0]["command"]
        project = self.root / "project"
        nested = project / "nested"
        nested.mkdir(parents=True)
        (project / ".git").mkdir()
        event = {
            "tool_name": "mcp__anechoic__test",
            "tool_input": {},
            "session_id": "test-session",
            "cwd": str(nested),
        }
        env = os.environ.copy()
        env["UV_PYTHON_DOWNLOADS"] = "never"
        run = subprocess.run(
            shlex.split(command),
            cwd=self.root,
            env=env,
            input=json.dumps(event),
            capture_output=True,
            text=True,
            check=True,
        )
        updated = json.loads(run.stdout)["hookSpecificOutput"]["updatedInput"]
        self.assertEqual(
            updated,
            {
                "project_root": str(project.resolve()),
                "caller_context": {"session_id": "test-session"},
            },
        )

    def test_inline_hook_conflict_is_not_duplicated(self):
        hook_path = self.root / "anechoic" / "codex_hook.py"
        config = self.root / "config.toml"
        config.write_text(
            '[[hooks.PreToolUse]]\nmatcher = "' + MATCHER + '"\n'
            '[[hooks.PreToolUse.hooks]]\ntype = "command"\n'
            'command = "python ' + str(hook_path) + '"\n',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "inline"):
            install_codex(
                ROOT, ENDPOINT, codex_home=self.root, executor=FakeCodex()
            )
        self.assertFalse((self.root / "hooks.json").exists())

    def test_failed_registration_does_not_write_hooks(self):
        def fail(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0])

        with self.assertRaises(subprocess.CalledProcessError):
            install_codex(ROOT, ENDPOINT, codex_home=self.root, executor=fail)
        self.assertFalse((self.root / "hooks.json").exists())
        self.assertFalse((self.root / "anechoic" / "codex_hook.py").exists())

    def test_hook_script_symlink_is_rejected(self):
        hook_dir = self.root / "anechoic"
        hook_dir.mkdir()
        outside = self.root / "outside"
        outside.write_text("unchanged")
        (hook_dir / "codex_hook.py").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            install_codex(
                ROOT, ENDPOINT, codex_home=self.root, executor=FakeCodex()
            )
        self.assertEqual(outside.read_text(), "unchanged")


if __name__ == "__main__":
    unittest.main()
