
"""Concrete Git, PR and subprocess boundary for one public release."""

from __future__ import annotations

from collections.abc import Callable
import json
from pathlib import Path
import subprocess
from public_release_materials import PublicReleaseError, repository_identity, validate_pr_url

Runner = Callable[[tuple[str, ...], Path], subprocess.CompletedProcess[str]]
Command = Callable[..., subprocess.CompletedProcess[str]]


def _command(
    root: Path, runner: Runner | None, argv: tuple[str, ...], *, allow_dirty_status: bool = False
) -> subprocess.CompletedProcess[str]:
    result = (
        runner(argv, root)
        if runner is not None
        else subprocess.run(
            argv,
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=3600 if argv[:2] == ("uv", "run") else 120,
        )
    )
    if not isinstance(result.returncode, int) or (
        result.returncode != 0 and not allow_dirty_status
    ):
        detail = ""
        if argv[:2] == ("uv", "run"):
            detail = "\n".join(
                f"{stream}:\n{getattr(result, stream)[-4000:]}" for stream in ("stdout", "stderr")
            )
        raise PublicReleaseError(f"public-release-command-failed: {' '.join(argv[:2])}: {detail}")
    return result


def _check_staged_environment(command: Command) -> None:
    staged = command((
        "git", "diff", "--cached", "--name-only", "--", ":(glob)**/.env*", ":(glob)**/*.env",
    ))
    if not isinstance(staged.stdout, str) or staged.stdout.strip():
        raise PublicReleaseError("public-release-staged-environment-file")


def _checkpoint(command: Command, before: str) -> None:
    command(
        (
            "git",
            "add",
            "-A",
            "--",
            ".",
            ":(exclude,glob)**/.env",
            ":(exclude,glob)**/.env*",
            ":(exclude,glob)**/*.env",
        )
    )
    _check_staged_environment(command)
    staged = command(("git", "diff", "--cached", "--quiet"), allow_dirty_status=True)
    if staged.returncode == 1:
        command(("git", "commit", "-m", f"chore(release): checkpoint before public {before}"))
    elif staged.returncode != 0:
        raise PublicReleaseError("public-release-git-status-failed")


def _repository(command: Command, slug: str) -> str:
    if command(("git", "branch", "--show-current")).stdout.strip() != "amm/dev":
        raise PublicReleaseError("public-release-requires-amm-dev")
    repository = repository_identity(
        command(("git", "remote", "get-url", "--all", "origin")).stdout, slug
    )
    push_repository = repository_identity(
        command(("git", "remote", "get-url", "--push", "--all", "origin")).stdout, slug
    )
    if push_repository != repository:
        raise PublicReleaseError("public-release-remote-mismatch")
    return repository


def _create_pr(command: Command, repository: str, description: str) -> str:
    created = command(
        (
            "gh",
            "pr",
            "create",
            "--repo",
            repository,
            "--draft",
            "--head",
            "amm/dev",
            "--base",
            "main",
            "--title",
            "ANECHOIC public release",
            "--body",
            description,
        )
    )
    return validate_pr_url(created.stdout.strip(), repository)


def _verify_pr(command: Command, repository: str, pr_url: str, head: str | None = None) -> bool:
    result = command(("gh", "pr", "view", pr_url, "--repo", repository, "--json", "url,state,headRefName,baseRefName,headRefOid,isDraft"))
    try:
        data = json.loads(result.stdout)
        valid = (data["url"], data["state"], data["headRefName"], data["baseRefName"]) == (pr_url, "OPEN", "amm/dev", "main")
        if not valid or not isinstance(data["isDraft"], bool) or (head is not None and data["headRefOid"] != head):
            raise ValueError
    except (ValueError, TypeError, KeyError) as error:
        raise PublicReleaseError("public-release-pr-mismatch") from error
    return data["isDraft"]
