import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .WORKERS_beta_C69__tests__shared import generation_fixture


class GenerationProfilerTests(unittest.TestCase):
    def test_real_worker_and_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            binding, _, _ = generation_fixture(temporary)
            path = Path(temporary) / 'binding.json'
            path.write_text(json.dumps(binding))
            script = Path(__file__).with_name('profile_generation.py')
            env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
            result = subprocess.run([sys.executable, '-B', str(script), '--project-root', binding['root']],
                                    capture_output=True, text=True, env=env)
            directory = Path(result.stdout.strip().splitlines()[0])
            self.assertTrue(directory.is_relative_to(Path(binding['root']) / '.anechoic_tmp' / 'beta-profile'))
            report = json.loads((directory / 'report.json').read_text())
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual('ok', report['status'])
            self.assertTrue((directory / 'worker.pstats').is_file())
            stages = {entry['stage']: entry for entry in report['stages']}
            for name in ('capture_prepare', 'capture_finish', 'manifest_build_CS4__shared', 'realization_graph'):
                self.assertGreaterEqual(stages[name]['wall_seconds'], 0)
                self.assertGreaterEqual(stages[name]['worker_cpu_seconds'], 0)
            self.assertIn('atoms', report['snapshot_counts'])
            self.assertTrue((directory / 'generation' / 'model.json').is_file())
            for child in ('manifest_build_CS4__shared', 'realization_graph'):
                self.assertTrue((directory / (child + '.pstats')).is_file())
                self.assertTrue((directory / (child + '-children.json')).is_file())

    def test_failure_writes_diagnostics(self):
        with tempfile.TemporaryDirectory() as temporary:
            binding, _, _ = generation_fixture(temporary)
            binding['manifest_sha256'] = '0' * 64
            path = Path(temporary) / 'bad-binding.json'
            path.write_text(json.dumps(binding))
            script = Path(__file__).with_name('profile_generation.py')
            result = subprocess.run([sys.executable, '-B', str(script), '--binding', str(path)],
                                    capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            directory = Path(result.stdout.strip().splitlines()[0])
            self.assertEqual('failed', json.loads((directory / 'report.json').read_text())['status'])
            self.assertIn('Manifest', (directory / 'failure.txt').read_text())
            self.assertTrue((directory / 'worker.pstats').is_file())


if __name__ == '__main__':
    unittest.main()
