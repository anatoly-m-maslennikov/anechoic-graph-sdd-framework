"""Verify interrupted release-owned Git checkpoints."""
from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _git_checkpoint,
    _project_path,
)


from .local_release_state import atomic_write
from .release_support import _read_version


class ReleaseGitCheckpoints:
    def _check_resume_head(self, *, allow_fix=False):
        if self.head is None:
            return
        result = self.runner(("git", "rev-parse", "--verify", "HEAD"), self.root)
        head = result.stdout.strip()
        if result.returncode != 0:
            raise LocalReleaseError("local-release-head-commit-unavailable")
        if head == self.head:
            return
        if allow_fix and self.runner(("git", "merge-base", "--is-ancestor", self.head, head), self.root).returncode == 0:
            return
        if self._checkpoint_commit_matches(head):
            self.head = head
            self.journal.data["head"] = head
            self.journal.save()
            return
        raise LocalReleaseError("local-release-resume-head-changed")

    def _checkpoint_paths(self, phase):
        return {"validate inputs": (".",), "static tests": ("version.toml",),
                "build package": ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58"),
                "install project runtime": (self.installed.relative_to(self.root).as_posix(),),
                "start mcp": (".agents/skills/ane",)}.get(phase, ())

    def _checkpoint_commit_matches(self, head):
        data = self.journal.data
        phase = data.get("working")
        paths = self._checkpoint_paths(phase)
        if not paths or data.get("checkpoint") == phase:
            return False
        commit = self.runner(("git", "show", "-s", "--format=%P%n%s", head), self.root)
        if commit.returncode or commit.stdout.splitlines() != [self.head, f"chore(release): simple local {phase}"]:
            return False
        files = self.runner(("git", "diff", "--name-only", "-z", self.head, head), self.root)
        return files.returncode == 0 and all(
            any(Path(name).is_relative_to(path) for path in paths) for name in files.stdout.split("\x00") if name
        )

    def _run_git_checkpoint(self, phase, *, interrupted):
        paths = self._checkpoint_paths(phase)
        head = self.head
        if interrupted and paths and head is not None:
            names = self.runner(("git", "diff", "--cached", "--name-only", "-z"), self.root)
            if names.returncode != 0:
                raise LocalReleaseError("local-release-index-check-unavailable")
            staged = tuple(Path(name) for name in names.stdout.split("\x00") if name)
            if staged:
                if not all(any(name.is_relative_to(path) for path in paths) for name in staged):
                    raise LocalReleaseError("local-release-resume-index-changed")
                if self.runner(("git", "diff", "--quiet", "--", *map(str, staged)), self.root).returncode != 0:
                    raise LocalReleaseError("local-release-resume-index-changed")
                head = None
        return _git_checkpoint(self.root, self.runner, phase, paths, head)

    def _bump_version(self):
        self.failed_step = "bump_candidate_version"
        pinned = self.journal.data.get("version")
        if pinned is None:
            version_path, output = _read_version(self.root)
            pinned = [version_path.read_text(encoding="utf-8"), output]
            self.journal.data["version"] = pinned
            self.journal.save()
        path = _project_path(self.root, Path("version.toml"), label="version-path", require_exists=True)
        current = path.read_text(encoding="utf-8")
        if current == pinned[0]:
            atomic_write(path, pinned[1])
        elif current != pinned[1]:
            raise LocalReleaseError("local-release-resume-version-changed")

    def _assert_version(self):
        path = _project_path(self.root, Path("version.toml"), label="version-path", require_exists=True)
        if path.read_text(encoding="utf-8") != self.journal.data["version"][1]:
            raise LocalReleaseError("local-release-resume-version-changed")
