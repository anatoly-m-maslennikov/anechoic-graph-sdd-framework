"""Replay declared golden-bug analyzers on their exact historical revisions."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

if not __package__:
    directory = Path(__file__).resolve().parent
    engine = next(
        parent
        for parent in directory.parents
        if parent.name == "LAYER_4_ENGINE_STUDIO_C14"
    )
    sys.path.insert(0, str(engine))
    __package__ = ".".join(directory.relative_to(engine).parts)

from .historical_checkout_scan import CORPUS, scan


def git(*args, cwd=None):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
        timeout=300,
    ).stdout.strip()


class _CaseCollection(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    cases: list[dict[str, Any]] = Field(default_factory=list)
    gaps: list[dict[str, Any]] = Field(default_factory=list)


def collect_cases(case_id):
    result = _CaseCollection()
    for case in sorted(path for path in CORPUS.iterdir() if path.is_dir()):
        if case_id and case.name != case_id:
            continue
        try:
            metadata = json.loads(
                (case / "case.json").read_text(encoding="utf-8")
            )
            if not isinstance(metadata, dict):
                raise ValueError("Case metadata must be an object")
            if not metadata.get("analyzer"):
                result.gaps.append(
                    {
                        "case": case.name,
                        "detail": "No checkout analyzer declared",
                    }
                )
                continue
            revisions = {
                side: metadata[side]["revision"]
                for side in ("before", "fixed")
            }
            if not all(
                isinstance(rev, str) and re.fullmatch(r"[0-9a-f]{40}", rev)
                for rev in revisions.values()
            ):
                raise ValueError(
                    "Both revisions must be exact 40-character Git hashes"
                )
            result.cases.append({"case": case.name, "revisions": revisions})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            result.gaps.append({"case": case.name, "detail": str(exc)})
    if case_id and not result.cases and not result.gaps:
        raise ValueError("Unknown case ID")

    return result.model_dump()


def _replay_revision(case, side, revision, checkout):
    try:
        git(
            "-c",
            "core.hooksPath=/dev/null",
            "checkout",
            "--detach",
            "--force",
            revision,
            cwd=checkout,
        )
        scanned = scan(checkout)
        target = [
            item
            for item in scanned["findings"]
            if item["case"] == case["case"]
        ]
        unresolved = [
            item
            for item in scanned["unresolved"]
            if item["case"] == case["case"]
        ]
        extra = [
            item
            for item in scanned["findings"]
            if item["case"] != case["case"]
        ]
        case[side] = {
            "findings": target,
            "unresolved": unresolved,
            "extra_indications": len(extra),
            "extra_findings": extra,
            "total_findings": len(scanned["findings"]),
            "other_unresolved": sum(
                item["case"] != case["case"] for item in scanned["unresolved"]
            ),
        }
    except (OSError, subprocess.SubprocessError) as exc:
        case[side] = {
            "findings": [],
            "unresolved": [{"detail": str(exc)}],
            "extra_indications": 0,
            "other_unresolved": 0,
        }


def _run_replay(result, repo_arg):
    try:
        repo = git(
            "-C",
            str(repo_arg if repo_arg.is_dir() else repo_arg.parent),
            "rev-parse",
            "--show-toplevel",
        )
        scratch = Path.home() / ".bb" / "thread-storage"
        with tempfile.TemporaryDirectory(
            prefix="historical-replay-", dir=scratch
        ) as tmp:
            checkout = Path(tmp) / "checkout"
            git(
                "clone", "--shared", "--no-checkout", "--", repo, str(checkout)
            )
            git("sparse-checkout", "init", "--no-cone", cwd=checkout)
            git(
                "sparse-checkout",
                "set",
                "--no-cone",
                "/LAYER_*/",
                "/SUPERLAYER_*/",
                cwd=checkout,
            )
            for case in result["cases"]:
                for side, revision in case["revisions"].items():
                    _replay_revision(case, side, revision, checkout)

    except (OSError, subprocess.SubprocessError) as exc:
        result["runner_error"] = str(exc)


def _summarize(result):
    cases = result["cases"]
    hits = sum(
        bool(c.get("before", {}).get("findings"))
        and not c["before"]["unresolved"]
        for c in cases
    )
    result["old_recall"] = {"hits": hits, "cases": len(cases)}
    observations = [
        c[side]
        for c in cases
        for side in ("before", "fixed")
        if side in c and "total_findings" in c[side]
    ]
    result["max_total_findings"] = max(
        (item["total_findings"] for item in observations), default=None
    )
    result["max_extra_indications"] = max(
        (item["extra_indications"] for item in observations), default=None
    )
    success = (
        bool(cases)
        and not result.get("runner_error")
        and all(
            c.get("before", {}).get("findings")
            and not c["before"]["unresolved"]
            and "fixed" in c
            and not c["fixed"]["findings"]
            and not c["fixed"]["unresolved"]
            for c in cases
        )
    )
    print(json.dumps(result, indent=2))
    return 0 if success else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="Replay only this case ID")
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve(),
        help="Source Git repository",
    )
    args = parser.parse_args()
    try:
        result = collect_cases(args.case)
    except ValueError as exc:
        parser.error(str(exc))

    _run_replay(result, args.repo)
    return _summarize(result)


if __name__ == "__main__":
    raise SystemExit(main())
