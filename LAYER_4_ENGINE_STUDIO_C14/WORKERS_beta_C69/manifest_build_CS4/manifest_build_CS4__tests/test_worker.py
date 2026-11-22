from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import signal
import time


from .manifest_build_CS4__tests__shared import fixture, run_worker

ENGINE = Path(__file__).resolve().parents[3]


class BuildTests(unittest.TestCase):
    def test_cli_build_and_verify_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = fixture(directory)
            env = os.environ.copy()
            env['PYTHONPATH'] = str(ENGINE)
            result = subprocess.run([sys.executable, "-B", '-m', 'WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared',
                                     '--output-dir', str(output)], input=json.dumps(binding),
                                    text=True, capture_output=True, env=env)
            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(binding['manifest_sha256'], receipt['manifest_sha256'])
            self.assertEqual(receipt['structure_sha256'], sha256((output / 'structure.json').read_bytes()).hexdigest())
            self.assertEqual(binding['manifest_sha256'], json.loads((output / 'structure.json').read_bytes())['project']['sha256'])
            descriptor = (output / 'model.json').read_bytes()
            self.assertEqual(receipt['model_descriptor_sha256'], sha256(descriptor).hexdigest())
            model = json.loads(descriptor)
            self.assertEqual(receipt['model_sha256'], model['model_sha256'])
            for module, digest in model['modules'].items():
                self.assertEqual(digest, sha256((output / 'anechoic_runtime_model' / module).read_bytes()).hexdigest())

    def test_project_root_manifest_uses_project_relative_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            root_manifest = Path(binding['root']) / manifest.name
            manifest.rename(root_manifest)
            binding['manifest_path'] = root_manifest.name
            result = run_worker(binding, output)
            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(binding['manifest_sha256'], receipt['manifest_sha256'])
            self.assertEqual(binding['manifest_sha256'], json.loads((output / 'structure.json').read_bytes())['project']['sha256'])

    def test_changed_pin_leaves_output_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            env = os.environ.copy()
            env['PYTHONPATH'] = str(ENGINE)
            process = subprocess.Popen([sys.executable, "-B", '-m', 'WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared',
                                        '--output-dir', str(output)], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            process.stdin.write(json.dumps(binding))
            process.stdin.close()
            process.stdin = None
            stopped = None
            deadline = time.monotonic() + 10
            try:
                while time.monotonic() < deadline and process.poll() is None:
                    if list(output.parent.glob('.manifest-build-*')):
                        try:
                            os.kill(process.pid, signal.SIGSTOP)
                            stopped = process.pid
                        except ProcessLookupError:
                            pass
                        break
                    time.sleep(0.001)
                self.assertIsNotNone(stopped, 'Compiler process was not observed')
                manifest.write_bytes(manifest.read_bytes() + b'\n')
                os.kill(stopped, signal.SIGCONT)
                stopped = None
                stdout, stderr = process.communicate(timeout=30)
                self.assertNotEqual(0, process.returncode, stdout + stderr)
            finally:
                if stopped:
                    os.kill(stopped, signal.SIGCONT)
                if process.poll() is None:
                    process.kill()
                    process.communicate()
            self.assertEqual([], list(output.iterdir()))

    def test_rejects_symlinked_manifest_and_control(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            target = manifest.with_suffix('.target')
            manifest.rename(target)
            manifest.symlink_to(target)
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            manifest.unlink()
            target.rename(manifest)
            control = manifest.parent
            moved = control.with_name('moved-control')
            control.rename(moved)
            control.symlink_to(moved, target_is_directory=True)
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            self.assertEqual([], list(output.iterdir()))

    def test_rejects_nonempty_output(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = fixture(directory)
            (output / 'keep').write_text('keep')
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            self.assertEqual('keep', (output / 'keep').read_text())


if __name__ == '__main__':
    unittest.main()
