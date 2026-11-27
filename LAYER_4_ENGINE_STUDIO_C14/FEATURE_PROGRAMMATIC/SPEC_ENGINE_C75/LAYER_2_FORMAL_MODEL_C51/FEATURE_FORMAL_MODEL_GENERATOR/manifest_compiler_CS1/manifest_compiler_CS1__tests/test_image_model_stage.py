"""Check guarded Model staging and the pinned predecessor selection."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.manifest_compiler_CS1__shared import (
    bounded_run, previous_claims, stage_model,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ReadContext

ROOT = Path(__file__).resolve().parents[7]
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
    def test_bundled_model_validates_previous_image(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1 import image_model_stage as stage
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            details = [{"Id": IMAGE_ID, "Os": "linux", "Config": {"Labels": {"org.anechoic.runtime.schema": "1"}}}]
            with (patch.object(stage, "_run", return_value="fingerprint") as compile_model,
                  patch.object(stage, "bounded_run", return_value=subprocess.CompletedProcess([], 0, json.dumps(details), "")) as docker):
                self.assertEqual(stage.stage_model(project, project, 5, None), "fingerprint")
                self.assertEqual(stage.stage_model(project, project, 5, IMAGE_ID), "fingerprint")
                docker.assert_called_once()
                with self.assertRaisesRegex(ValueError, "immutable image ID"):
                    stage.stage_model(project, project, 5, "")
                docker.return_value = subprocess.CompletedProcess([], 1, "", "")
                with self.assertRaisesRegex(ValueError, "unavailable"):
                    stage.stage_model(project, project, 5, IMAGE_ID)
                details[0]["Config"]["Labels"] = {}
                docker.return_value = subprocess.CompletedProcess([], 0, json.dumps(details), "")
                with self.assertRaisesRegex(ValueError, "not an admitted runtime image"):
                    stage.stage_model(project, project, 5, IMAGE_ID)
                self.assertEqual(compile_model.call_count, 2)
            (project / ".anechoic_tmp").mkdir()
            (project / ONTOLOGY).mkdir()
            with self.assertRaisesRegex(ValueError, "immutable image ID"):
                stage.stage_model(project, project, 5, "")

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
            continuant = source / '_DOM' / 'CONT'
            continuant.mkdir(parents=True)
            (continuant / 'continuant.md').write_bytes(b'continuant')

            def compile_model(command, **kwargs):
                self.assertEqual((Path(command[-1]) / ONTOLOGY / "claim.md").read_bytes(), b"claim")
                self.assertEqual((Path(command[-1]) / ONTOLOGY / '_DOM' / 'CONT' / 'continuant.md').read_bytes(), b'continuant')
                return subprocess.CompletedProcess(command, 0, "fingerprint\n")

            with patch.object(subprocess, "run", side_effect=compile_model):
                self.assertEqual(stage_model(project, project, 5, None), "fingerprint")
                (source / "claim.md").write_bytes(b"other")
                with self.assertRaisesRegex(ValueError, "Duplicate"):
                    stage_model(project, project, 5, None)

    def test_staging_flattens_relocated_c9(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            (project / ".anechoic_tmp").mkdir()
            spec = project / "ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_SPEC"
            spec.mkdir(parents=True)
            (spec / "claim.md").write_bytes(b"claim")

            def compile_model(command, **kwargs):
                self.assertEqual((Path(command[-1]) / ONTOLOGY / "claim.md").read_bytes(), b"claim")
                return subprocess.CompletedProcess(command, 0, "fingerprint\n")

            with patch.object(subprocess, "run", side_effect=compile_model):
                self.assertEqual(stage_model(project, project, 5, None), "fingerprint")

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


def test_selector_and_staged_parity_for_continuant_and_typed_properties():
    from hashlib import sha256
    from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND import native_model_selector as selector
    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1 import image_model_stage as stage

    def source(identifier, lens, template, concern='', body=''):
        return (f'---\natom_family: SPEC\natom_id: {identifier}\n{concern}'
                f'structure:\n  container:\n    component: C9\n  tier: 2\n'
                f'context:\n  lens: {lens}\n  template: {template}\n'
                f'state:\n  status: active\n  version: 1\n  updated_at: 2026-11-20T00:00:00Z\n---\n{body}')
    with tempfile.TemporaryDirectory() as temporary:
        project = Path(temporary).resolve()
        (project / '.anechoic_tmp').mkdir()
        component = project / ONTOLOGY
        cont = component / '_DOM' / 'CONT'
        des = component / '_DES'
        cont.mkdir(parents=True)
        des.mkdir()
        files = {
            cont / 'cont.md': source('AN-S-1', 'DOM/CONT', 'manifest_node',
                'concern:\n  subject: Graph\n  path: Model\n  relation: is_contained_by\n'),
            des / 'property.md': source('AN-S-2', 'DES', 'manifest_property'),
            component / 'legacy.md': source('AN-S-3', 'SPEC', 'manifest_node',
                body='## Claim scope\n\nMODEL//ANECHOIC <+ Graph\n'),
            des / 'excluded.md': source('AN-S-4', 'DES', 'other'),
            cont / 'inactive.md': source('AN-S-5', 'DOM/CONT', 'manifest_node',
                'concern:\n  subject: Graph\n  path: Model\n  relation: is_contained_by\n').replace('status: active', 'status: draft'),
        }
        for path, content in files.items():
            path.write_text(content)
        expected = sorted([[p.name, sha256(content.encode()).hexdigest()] for p, content in files.items()
                           if p.name not in {'excluded.md', 'inactive.md'}])
        class Store:
            def replace(self, rows, *args, **kwargs):
                self.rows = rows
            def run(self, query, **kwargs):
                assert '"header.status"' in query and '"header.subject" IS NOT NULL' in query
                names = sorted(Path(row['source_path']).name for row in self.rows
                               if row['header_json']['status'] == 'active' and row['header_json']['subject'] is not None)
                return {'rows': [(name,) for name in names], 'has_more': False}
            def close(self):
                pass
        types = (lambda rows: None, lambda *args: None, lambda *args: None, Store)
        with patch.object(selector, 'ENGINE_ROOT', ROOT / ENGINE), patch.object(selector, '_workbench_types', return_value=types):
            assert selector.select_claims(component) == expected
        beta_engine = project / 'beta_engine'
        (beta_engine / 'KERNEL_MIXER_beta_C67').mkdir(parents=True)
        extensions = os.environ.get('ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY',
                                    str(ROOT / '.anechoic_tmp/workbench/extensions'))
        with (patch.object(selector, 'ENGINE_ROOT', beta_engine),
              patch.dict(os.environ, {'ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY': extensions})):
            assert selector.select_claims(component) == expected

        def compile_model(command, **kwargs):
            staged = Path(command[-1]) / ONTOLOGY
            assert (staged / '_DOM' / 'CONT' / 'cont.md').exists()
            assert (staged / '_DES' / 'property.md').exists()
            (staged.parent / 'model.json').write_text(json.dumps({'declarations': [
                ['cont.md@1', '', ''], ['cont.md@1', '', ''],
                ['property.md@1', '', ''], ['legacy.md@1', '', '']]}))
            return subprocess.CompletedProcess(command, 0, 'fingerprint\n')
        with (patch.object(stage, 'previous_claims', return_value=expected),
              patch.object(subprocess, 'run', side_effect=compile_model)):
            assert stage_model(project, project, 5, IMAGE_ID) == 'fingerprint'
