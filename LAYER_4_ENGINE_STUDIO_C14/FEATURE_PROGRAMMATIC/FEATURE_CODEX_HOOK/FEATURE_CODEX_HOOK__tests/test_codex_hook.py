
"""Exercise the Codex command-hook boundary without an installed plugin."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HOOK = Path(__file__).resolve().parents[1] / "codex_hook.py"


def invoke(event):
    completed = subprocess.run(
        [sys.executable, "-B", str(HOOK)], input=event, text=True, capture_output=True, check=True
    )
    return json.loads(completed.stdout)


class CodexHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve() / "example"
        self.project.mkdir()
        (self.project / ".git").mkdir()
        self.event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "mcp__anechoic__query_run",
            "session_id": "codex-session-123",
            "cwd": str(self.project),
            "tool_input": {
                "project_root": str(self.project),
                "sql": "SELECT 1",
                "session_id": "native-argument",
            },
        }

    def decision(self, event):
        return invoke(json.dumps(event))["hookSpecificOutput"]

    def test_injects_session_and_preserves_native_arguments(self):
        result = self.decision(self.event)
        self.assertEqual("allow", result["permissionDecision"])
        self.assertEqual(
            {**self.event["tool_input"], "caller_context": {"session_id": "codex-session-123"}},
            result["updatedInput"],
        )

    def test_matching_existing_context_is_preserved(self):
        self.event["tool_input"]["caller_context"] = {"session_id": "codex-session-123", "other": 4}
        result = self.decision(self.event)
        self.assertEqual(self.event["tool_input"], result["updatedInput"])

    def test_resolves_nearest_git_root(self):
        del self.event["tool_input"]["project_root"]
        subdir = self.project / "subdir"
        subdir.mkdir()
        nested = subdir / "nested"
        nested.mkdir()
        (nested / ".git").write_text("gitdir: /worktree/gitdir\n")
        for folder, root in ((self.project, self.project), (subdir, self.project), (nested, nested)):
            with self.subTest(folder=folder):
                result = self.decision({**self.event, "cwd": str(folder)})
                self.assertEqual("allow", result["permissionDecision"])
                self.assertEqual(str(root), result["updatedInput"]["project_root"])

    def test_subdirectory_accepts_only_canonical_explicit_root(self):
        child = self.project / "child"
        child.mkdir()
        self.event["cwd"] = str(child)
        self.assertEqual("allow", self.decision(self.event)["permissionDecision"])
        self.event["tool_input"]["project_root"] = str(child)
        self.assertEqual("deny", self.decision(self.event)["permissionDecision"])

    def test_rejects_missing_root_and_unsafe_marker(self):
        del self.event["tool_input"]["project_root"]
        outside = Path(self.temp.name).resolve() / "outside"
        outside.mkdir()
        self.assertEqual("deny", self.decision({**self.event, "cwd": str(outside)})["permissionDecision"])
        child = self.project / "child"
        child.mkdir()
        (child / ".git").symlink_to(self.project / ".git")
        self.assertEqual("deny", self.decision({**self.event, "cwd": str(child)})["permissionDecision"])
        self.assertEqual("deny", self.decision({**self.event, "cwd": str(child / "missing")})["permissionDecision"])

    def test_conflicting_project_root_is_denied(self):
        self.event["tool_input"]["project_root"] = str(self.project.with_name("another"))
        self.assertEqual("deny", self.decision(self.event)["permissionDecision"])

    def test_missing_or_invalid_session_folder_is_denied(self):
        del self.event["cwd"]
        self.assertEqual("deny", self.decision(self.event)["permissionDecision"])
        for folder in (None, "", "relative/project", str(self.project / "bad\x00path")):
            with self.subTest(folder=folder):
                result = self.decision({**self.event, "cwd": folder})
                self.assertEqual("deny", result["permissionDecision"])

    def test_conflicting_session_is_denied(self):
        self.event["tool_input"]["caller_context"] = {"session_id": "another-session"}
        self.assertEqual("deny", self.decision(self.event)["permissionDecision"])

    def test_missing_or_invalid_context_is_denied(self):
        for key, value in (("session_id", None), ("session_id", ""), ("tool_input", None)):
            with self.subTest(key=key, value=value):
                changed = {**self.event, key: value}
                self.assertEqual("deny", self.decision(changed)["permissionDecision"])
        for key, value in (("project_root", None), ("project_root", ""), ("caller_context", None)):
            with self.subTest(key=key, value=value):
                changed = {**self.event, "tool_input": {**self.event["tool_input"], key: value}}
                self.assertEqual("deny", self.decision(changed)["permissionDecision"])

    def test_other_servers_are_untouched(self):
        result = invoke(json.dumps({**self.event, "cwd": None, "tool_name": "mcp__other__query_run"}))
        self.assertEqual({}, result)

    def test_invalid_json_is_denied(self):
        self.assertEqual("deny", invoke("{")["hookSpecificOutput"]["permissionDecision"])

    def test_large_deep_and_non_unicode_input_is_denied(self):
        for raw in (
            b" " * (32 * 1024 * 1024 + 1),
            b"[" * 1200 + b"]" * 1200,
            b'"\xff"',
            b"{" + b'"v":' + b"1" * 5000 + b"}",
        ):
            with self.subTest(size=len(raw)):
                result = subprocess.run(
                    [sys.executable, "-B", str(HOOK)], input=raw, capture_output=True, check=True
                )
                self.assertEqual(
                    "deny", json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]
                )


if __name__ == "__main__":
    unittest.main()
