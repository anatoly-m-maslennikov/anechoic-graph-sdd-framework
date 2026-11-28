"""Check the approved C45 HTTP baseline with oasdiff 1.41.0."""

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    export_openapi,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83._package__shared \
    import load_manifest  # fmt: skip

from ..._package__shared import C45_QUERY_RUN_PIN

ROOT = Path(__file__).resolve().parents[7]
BASELINE = Path(__file__).parents[2] / "assets/c45_query_run.openapi.json"
BASELINE_DIGEST = (
    "04824b86919ea5fe7b59abb06574f783a183094f2350ae2255d1d578ce7b01d4"
)


def _breaking(executable, candidate, document):
    candidate.write_text(json.dumps(document), encoding="utf-8")
    return subprocess.run(
        [
            executable,
            "breaking",
            str(BASELINE),
            str(candidate),
            "--allow-external-refs=false",
            "--format",
            "json",
            "--fail-on",
            "ERR",
        ],
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )


class OpenAPICompatibilityTests(unittest.TestCase):
    def test_baseline_snapshot(self):
        self.assertEqual(
            hashlib.sha256(BASELINE.read_bytes()).hexdigest(), BASELINE_DIGEST
        )

    @unittest.skipUnless(
        os.environ.get("OASDIFF"), "Set OASDIFF to run this check"
    )
    def test_current_contract_and_controls(self):
        executable = os.environ["OASDIFF"]
        version = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=45,
        )
        self.assertEqual(version.stdout.strip(), "oasdiff version 1.41.0")
        manifest = load_manifest(ROOT, "C45", C45_QUERY_RUN_PIN)
        current = export_openapi(manifest, action="query_run")
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.json"
            result = _breaking(executable, candidate, current)
            self.assertEqual(
                result.returncode, 0, result.stdout + result.stderr
            )
            current["info"]["description"] = "Compatible documentation change"
            result = _breaking(executable, candidate, current)
            self.assertEqual(
                result.returncode, 0, result.stdout + result.stderr
            )
            del current["paths"]["/tools"]["post"]
            result = _breaking(executable, candidate, current)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(
            any(
                change["id"] == "api-removed-without-deprecation"
                and change["path"] == "/tools"
                and change["operation"] == "POST"
                for change in json.loads(result.stdout)
            ),
            result.stdout,
        )
