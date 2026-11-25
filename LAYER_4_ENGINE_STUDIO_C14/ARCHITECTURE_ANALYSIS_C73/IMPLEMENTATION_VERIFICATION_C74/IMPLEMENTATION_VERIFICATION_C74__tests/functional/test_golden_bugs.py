"""Check frozen historical inputs and bounded Lean demonstrations."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

CORPUS = Path(__file__).parent / 'golden_bugs'


class GoldenBugsTests(unittest.TestCase):
    def cases(self):
        paths = sorted(CORPUS.glob('*/case.json'))
        self.assertTrue(paths, 'Golden bug corpus is empty')
        return paths

    def test_historical_fixtures(self):
        for path in self.cases():
            with self.subTest(case=path.parent.name):
                case = json.loads(path.read_text(encoding='utf-8'))
                for field in ('title', 'invariant', 'scope'):
                    self.assertTrue(case[field].strip(), field)
                if 'analyzer' in case:
                    self.assertEqual(case['analyzer'], 'analyze.py')
                    self.assertTrue((path.parent / 'analyze.py').is_file())
                for version in ('before', 'fixed'):
                    record = case[version]
                    self.assertTrue(record['revision'].strip())
                    self.assertTrue(record['source'])
                    fixture = (path.parent / record['fixture']).resolve()
                    self.assertTrue(fixture.is_relative_to(path.parent.resolve()))
                    raw = fixture.read_bytes()
                    self.assertTrue(raw, str(fixture))
                    self.assertEqual(sha256(raw).hexdigest(), record['sha256'])
                self.assertTrue(case['checks'], 'No Lean checks')

    def test_editor_case_reuses_rule(self):
        lean = os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable is missing')
        analyzer = CORPUS / 'e2e-editor-before-query' / 'analyze.py'
        body = """test('different scenario', async ({ page }) => {
  const queryBox = page.getByRole('textbox', { name: 'Query editor' });
  await queryBox.click();
  await page.keyboard.insertText('SELECT 42');
  CHECK
  await page.getByRole('button', { name: 'Run Cmd+Enter' }).click();
});"""
        variants = {
            '': 'findings',
            "await expect(queryBox).toHaveText('SELECT 41');": 'findings',
            "await expect(queryBox).toHaveText('SELECT 42');": 'clear',
            'await expect(queryBox).toHaveText(sql);': 'unresolved',
            "if (condition) await expect(queryBox).toHaveText('SELECT 42');": 'unresolved',
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'different.spec.ts'
            for check, expected in variants.items():
                with self.subTest(check=check):
                    path.write_text(body.replace('CHECK', check), encoding='utf-8')
                    run = subprocess.run([sys.executable, '-B', str(analyzer), temp, '--lean', lean,
                                          '--file', path.name, '--title', 'different scenario'],
                                         capture_output=True, text=True, check=True, timeout=30)
                    result = json.loads(run.stdout)
                    self.assertEqual(bool(result['findings']), expected == 'findings', result)
                    self.assertEqual(bool(result['unresolved']), expected == 'unresolved', result)
            for changed in (body.replace('const queryBox', 'let queryBox'),
                            body.replace("await page.keyboard.insertText('SELECT 42');",
                                         "await replaceSql(page, 'SELECT 42');")):
                path.write_text(changed.replace('CHECK', "await expect(queryBox).toHaveText('SELECT 42');"), encoding='utf-8')
                run = subprocess.run([sys.executable, '-B', str(analyzer), temp, '--lean', lean,
                                      '--file', path.name, '--title', 'different scenario'],
                                     capture_output=True, text=True, check=True, timeout=30)
                self.assertTrue(json.loads(run.stdout)['unresolved'], run.stdout)

    def test_release_port_domain(self):
        lean = os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable is missing')
        case = CORPUS / 'release-test-fixed-port'
        metadata = json.loads((case / 'case.json').read_text(encoding='utf-8'))
        fixed = (case / metadata['fixed']['fixture']).read_text(encoding='utf-8')
        original = '1 <= port <= 65535'
        self.assertIn(original, fixed)
        variants = {
            original: None,
            '1024 <= port <= 65535': 'rejects valid port 1',
            '0 <= port <= 65535': 'accepts invalid port 0',
        }
        with tempfile.TemporaryDirectory() as temp:
            relative = 'moved/release_port_test.py'
            path = Path(temp) / relative
            path.parent.mkdir(parents=True)
            for bounds, expected in variants.items():
                with self.subTest(bounds=bounds):
                    path.write_text(fixed.replace(original, bounds), encoding='utf-8')
                    run = subprocess.run([sys.executable, '-B', str(case / 'analyze.py'),
                                          temp, '--lean', lean, '--file', relative], capture_output=True,
                                         text=True, check=True, timeout=30)
                    result = json.loads(run.stdout)
                    self.assertFalse(result['unresolved'], result)
                    self.assertEqual(len(result['findings']), int(expected is not None), result)
                    if expected:
                        self.assertEqual(result['findings'][0]['path'], relative)
                        self.assertIn(expected, result['findings'][0]['detail'])

    def test_case_local_controls(self):
        for case, script in (
            ('local-release-result', 'test_analyze.py'),
            ('saved-query-stale-table-rebuild', 'test_analyze.py'),
            ('workflow-guard-validation', 'check_scenarios.py'),
        ):
            with self.subTest(case=case):
                run = subprocess.run([sys.executable, '-B', str(CORPUS / case / script)],
                                     capture_output=True, text=True, check=False, timeout=120)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_frozen_lean(self):
        lean = os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable is missing; install Lean or set LEAN_BIN')
        for path in self.cases():
            case = json.loads(path.read_text(encoding='utf-8'))
            for check in case['checks']:
                with self.subTest(case=path.parent.name, check=check['file']):
                    proof = (path.parent / check['file']).resolve()
                    self.assertTrue(proof.is_relative_to(path.parent.resolve()))
                    self.assertEqual(proof.suffix, '.lean')
                    result = subprocess.run([lean, str(proof)], capture_output=True, text=True, check=False, timeout=120)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    if 'stdout_suffix' in check:
                        self.assertTrue(result.stdout.endswith(check['stdout_suffix']), result.stdout)


if __name__ == '__main__':
    unittest.main()
