"""Check guarded Model staging and the pinned predecessor selection."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.manifest_compiler_CS1__shared import (
    bounded_run, previous_claims, stage_model,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ReadContext

ROOT = Path(__file__).resolve().parents[6]
ENGINE = "LAYER_4_ENGINE_STUDIO_C14"
PROGRAMMATIC = ROOT / ENGINE / "FEATURE_PROGRAMMATIC"
ONTOLOGY = "LAYER_1_META_ONTOLOGY_C9"
IMAGE_ID = "sha256:" + "a" * 64


def fake_docker(root, *, valid=True, selection=None):
    log = root / "calls.jsonl"
    binary = root / "docker"
    inspected = [{"Id": IMAGE_ID, "Os": "linux", "Config": {"Labels": {"org.anechoic.runtime.schema": "1"}}}]
    binary.write_text(
        f"#!{sys.executable}\nimport json, sys\n"
        f"with open({str(log)!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        f"valid = {valid!r}\n"
        "if not valid: sys.exit(1)\n"
        f"print(json.dumps({inspected!r} if sys.argv[1:3] == ['image', 'inspect'] else {selection!r}))\n"
    )
    binary.chmod(0o700)
    return log


class ImageModelStageTests(unittest.TestCase):
    def test_previous_selector_mounts_exact_current_codecs_read_only(self):
        names = ("carrier_read__pub.py", "carrier_syntax__pub.py", "carrier_compat__pub.py",
                 "native_carrier_header__pub.py", "content_records__pub.py", "markdown_content__pub.py",
                 "source_row__pub.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            component = root / "model"
            component.mkdir()
            log = fake_docker(root, selection=[["claim.md", "hash"]])
            original_wait = subprocess.Popen.wait
            waits = []

            def record_wait(process, timeout=None):
                waits.append(timeout)
                return original_wait(process, timeout=timeout)

            with patch.dict(os.environ, {"PATH": str(root)}), patch.object(subprocess.Popen, "wait", record_wait):
                for timeout in (5, None):
                    waits.clear()
                    self.assertEqual(previous_claims(component, IMAGE_ID, timeout=timeout), [["claim.md", "hash"]])
                    self.assertEqual(len(waits), 2)
                    self.assertTrue(all(value is None if timeout is None else 0 < value <= timeout for value in waits))
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual(len(calls), 4)
            for argv in calls[1::2]:
                for name in names:
                    staged = root / name
                    source = PROGRAMMATIC / "FEATURE_TOOLS/ADAPTERS_C30" / name
                    self.assertEqual(source.read_bytes(), staged.read_bytes())
                    self.assertIn(f"type=bind,src={staged},dst=/workspace/{ENGINE}/"
                                  f"FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/{name},readonly", argv)
                self.assertIn("--read-only", argv)
                self.assertIn("--network=none", argv)

    def test_unbounded_commands_keep_the_output_limit(self):
        command = [sys.executable, "-B", "-c", "print('ok')"]
        result = bounded_run(command, cwd=ROOT, timeout=None)
        self.assertEqual((result.returncode, result.stdout), (0, "ok\n"))
        with self.assertRaisesRegex(ValueError, "stdout exceeded"):
            bounded_run(command, cwd=ROOT, timeout=None, max_output=2)

    def test_previous_ready_image_is_required_when_recorded(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = fake_docker(root, valid=False)
            with patch.dict(os.environ, {"PATH": str(root)}):
                with self.assertRaisesRegex(ValueError, "Previous ready image is unavailable"):
                    previous_claims(root, IMAGE_ID, timeout=5)
            self.assertEqual(len(log.read_text().splitlines()), 1)

    def test_staging_reads_spec_and_rejects_duplicate_filenames(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            (project / ".anechoic_tmp").mkdir()
            source = project / ONTOLOGY
            spec = source / "_SPEC"
            spec.mkdir(parents=True)
            (spec / "claim.md").write_bytes(b"claim")

            def compile_model(command, **kwargs):
                self.assertEqual((Path(command[-1]) / ONTOLOGY / "claim.md").read_bytes(), b"claim")
                return subprocess.CompletedProcess(command, 0, "fingerprint\n")

            with patch.object(subprocess, "run", side_effect=compile_model):
                self.assertEqual(stage_model(project, project, 5, None), "fingerprint")
                (source / "claim.md").write_bytes(b"other")
                with self.assertRaisesRegex(ValueError, "Duplicate"):
                    stage_model(project, project, 5, None)

    def test_staging_rejects_changed_sources_and_selector_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            (project / ".anechoic_tmp").mkdir()
            source = project / ONTOLOGY
            source.mkdir()
            claim = source / "claim.md"
            claim.write_bytes(b"claim")
            fake_docker(project, selection=[])

            def compile_model(command, **kwargs):
                (Path(command[-1]) / "model.json").write_text(
                    json.dumps({"declarations": [["claim.md@1", None, None]]}))
                return subprocess.CompletedProcess(command, 0, "f" * 64)

            with (patch.dict(os.environ, {"PATH": str(project)}),
                  patch.object(subprocess, "run", side_effect=compile_model),
                  patch.object(ReadContext, "currentness", return_value={"state": "changed"})):
                with self.assertRaisesRegex(ValueError, "selection does not match"):
                    stage_model(project, project, 5, IMAGE_ID)
                with self.assertRaisesRegex(ValueError, "sources changed"):
                    stage_model(project, project, 5, None)
