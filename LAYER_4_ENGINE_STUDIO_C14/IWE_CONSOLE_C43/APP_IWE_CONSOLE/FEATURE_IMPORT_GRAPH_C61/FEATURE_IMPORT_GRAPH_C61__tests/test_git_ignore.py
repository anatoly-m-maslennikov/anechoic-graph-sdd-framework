from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import git_ignored


class GitIgnoreTests(unittest.TestCase):
    def test_matches_git_for_nested_root_and_linked_worktree(self):
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            repo = base / "repo"
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            (repo / "project").mkdir()
            (repo / ".gitignore").write_text("*.py\n!keep.py\nblocked/\n")
            (repo / "project" / ".gitignore").write_text("!nested.py\n")
            (repo / "project" / "tracked.py").write_text("")
            subprocess.run(["git", "-C", str(repo), "add", "-f", "."], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "initial"], check=True)
            (repo / ".git" / "info" / "exclude").write_text("excluded.txt\n")
            worktree = base / "worktree"
            subprocess.run(["git", "-C", str(repo), "worktree", "add", "-qb", "other", str(worktree)], check=True)
            names = {"ignored.py", "keep.py", "nested.py", "tracked.py", "excluded.txt", "blocked/keep.py"}
            for root in (repo / "project", worktree / "project"):
                result = subprocess.run(
                    ["git", "-C", str(root), "check-ignore", "--stdin", "-z"],
                    input=("\0".join(sorted(names)) + "\0").encode(),
                    capture_output=True, check=False,
                )
                self.assertIn(result.returncode, (0, 1))
                expected = {item.decode() for item in result.stdout.split(b"\0") if item}
                self.assertEqual(git_ignored(root, names), expected)
            self.assertEqual(git_ignored(base, names), set())
