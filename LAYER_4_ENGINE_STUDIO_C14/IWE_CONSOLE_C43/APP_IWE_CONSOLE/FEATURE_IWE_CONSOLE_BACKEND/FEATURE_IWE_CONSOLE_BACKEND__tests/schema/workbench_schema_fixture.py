"""Both Workbench schema modes and their deterministic generated asset."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


APP_ROOT = Path(__file__).resolve().parents[4]


def generate_asset(project_root: Path, script: str) -> bytes:
    launcher = Path(__file__).resolve().parents[2] / script
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "asset.json"
        subprocess.run(
            [
                sys.executable,
                "-B",
                str(launcher),
                "--project-root",
                str(project_root),
                "--output",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return output.read_bytes()


def atom(
    reference: str = "CA-R-1",
    *,
    header: dict | None = None,
    body: str = "## Summary\n\nSummary.\n",
    form: str = "Definition",
    version: int = 1,
) -> dict:
    return {
        "source_path": f"source/{reference}.md",
        "status_group": "Current",
        "id": reference,
        "ref": reference,
        "version": version,
        "status": "Active",
        "role": "Requirement",
        "form": form,
        "tier": 1,
        "updated_at": None,
        "header_json": header or {},
        "_content_bytes": body.encode("utf-8"),
        "content_markdown": body,
        "content_properties_json": [],
        "relation_edges_json": [],
        "hash": None,
    }


class WorkbenchSchemaFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.database = (
            Path(self.temporary.name) / "workbench" / "projection.duckdb"
        )


if __name__ == "__main__":
    unittest.main()
