"""Run available golden-bug analyzers against a supplied checkout."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


CORPUS = Path(__file__).resolve().parent / "golden_bugs"


class _ScanResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    findings: list[dict[str, Any]] = Field(default_factory=list)
    unresolved: list[dict[str, Any]] = Field(default_factory=list)
    gaps: list[dict[str, Any]] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)


def scan(checkout, corpus=CORPUS):
    result = _ScanResult()
    lean = os.environ.get("LEAN_BIN") or shutil.which("lean") or "lean"
    for case in sorted(path for path in corpus.iterdir() if path.is_dir()):
        try:
            metadata = json.loads((case / "case.json").read_text(encoding="utf-8"))
            if not isinstance(metadata, dict):
                raise ValueError("Case metadata must be a JSON object")
            analyzer = metadata.get("analyzer")
            if analyzer is None:
                result.gaps.append({"case": case.name, "detail": "No checkout analyzer declared"})
                continue
            if analyzer != "analyze.py" or not (case / analyzer).is_file():
                raise ValueError("Declared analyzer must be an existing analyze.py")
            process = subprocess.run(
                [sys.executable, "-B", str(case / analyzer), str(checkout), "--lean", lean],
                capture_output=True, text=True, timeout=45,
            )
            if process.returncode:
                raise ValueError(f"Analyzer exited {process.returncode}: {process.stderr.strip() or process.stdout.strip()}")
            output = json.loads(process.stdout)
            if not isinstance(output, dict) or not all(isinstance(output.get(k), list) for k in ("findings", "unresolved")):
                raise ValueError("Analyzer output must contain findings and unresolved lists")
            if not all(isinstance(item, dict) and isinstance(item.get("path"), str) and isinstance(item.get("detail"), str) for item in output["findings"]):
                raise ValueError("Each finding must contain string path and detail")
            for item in output["findings"]:
                finding = {"case": case.name, "path": item["path"], "detail": item["detail"]}
                if finding not in result.findings:
                    result.findings.append(finding)
            result.unresolved.extend({"case": case.name, "result": item} for item in output["unresolved"])
        except (OSError, ValueError, TypeError, subprocess.TimeoutExpired) as exc:
            result.unresolved.append({"case": case.name, "result": {"detail": str(exc)}})
    result.counts = {key: len(getattr(result, key)) for key in ("findings", "unresolved", "gaps")}
    return result.model_dump()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", required=True, type=Path, help="Existing historical checkout to scan")
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    if not checkout.is_dir():
        parser.error("--checkout must be an existing directory")
    print(json.dumps(scan(checkout), indent=2))


if __name__ == "__main__":
    main()
