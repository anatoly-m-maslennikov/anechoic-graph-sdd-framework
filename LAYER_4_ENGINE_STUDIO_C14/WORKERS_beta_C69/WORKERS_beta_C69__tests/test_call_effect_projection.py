"""Check graph-backed Lean effects against small trusted runtime fixtures."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ENGINE = Path(__file__).resolve().parents[2]
FRONTEND = ENGINE / 'IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND'
PY_HELPER = '''_count = 0
def mutate():
    global _count
    _count = 1
    _count = 0
def emit():
    print('event')
def value():
    return 42
def fail():
    raise ValueError('sentinel')
'''
PY_CALLER = '''from pkg.helper import mutate as update, emit, value, fail
def start():
    update()
    emit()
def silent():
    value()
def forward():
    return value()
def abort():
    fail()
    emit()
def cycle():
    cycle()
def dynamic(callback):
    callback()
'''
JS_HELPER = '''let count = 0;
export function mutate() { count = 1; count = 0; }
export function emit() { console.log('event'); }
export const value = () => 42;
export function read() { return count; }
'''
JS_CALLER = '''import * as dep from './pkg/helper.mjs';
export function start() { dep.mutate(); dep.emit(); }
export function silent() { dep.value(); }
export const forward = () => dep.value();
export function cycle() { cycle(); }
export function dynamic(callback) { callback(); }
'''


@unittest.skipUnless(shutil.which('lean'), 'Lean is unavailable')
class CallEffectProjectionTest(unittest.TestCase):
    def project(self, root):
        request = json.dumps({'root': str(root), 'config': {'python_roots': ['.']}})
        result = subprocess.run([sys.executable, '-B', '-P', '-m', 'WORKERS_beta_C69.realization_graph'],
                                input=request, text=True, capture_output=True, check=True, timeout=60)
        rows = json.loads(result.stdout)['state_effect_findings']
        return {(row[1], row[3]): (row[6], json.loads(row[8]), json.loads(row[9])) for row in rows}

    def assert_calls(self, findings, caller, helper):
        expected = {'start': ('hasEffects', ['write', 'write', 'output']),
                    'silent': ('deadEnd', []), 'forward': ('hasEffects', ['output']),
                    'cycle': ('unresolved', []), 'dynamic': ('unresolved', [])}
        for name, (status, kinds) in expected.items():
            with self.subTest(caller=caller, name=name):
                actual, events, violations = findings[caller, name]
                self.assertEqual((status, kinds, []), (actual, [e['kind'] for e in events], violations))
                self.assertEqual([helper] * len(kinds), [e['sourcePath'] for e in events])
        self.assertEqual(['pkg', 'pkg'], [e['name'] for e in findings[caller, 'start'][1][:2]])

    def test_python_call_chain(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'pkg').mkdir()
            (root / 'pkg/helper.py').write_text(PY_HELPER)
            (root / 'main.py').write_text(PY_CALLER)
            findings = self.project(root)
            self.assert_calls(findings, 'main.py', 'pkg/helper.py')
            self.assertEqual(('hasEffects', [{'kind': 'output', 'target': '', 'name': '',
                                            'line': 11, 'sourcePath': 'pkg/helper.py'}], []),
                             findings['main.py', 'abort'])
            runtime = subprocess.check_output([sys.executable, '-B', '-c',
                       'from main import start, silent, forward; from pkg import helper; '
                       'start(); assert silent() is None; print(forward(), helper._count)'], cwd=root, text=True)
            self.assertEqual('event\n42 0\n', runtime)

    @unittest.skipUnless(shutil.which('node') and (FRONTEND / 'node_modules/typescript').is_dir(),
                         'Framework web parser is unavailable')
    def test_web_call_chain(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'pkg').mkdir()
            (root / 'pkg/helper.mjs').write_text(JS_HELPER)
            for caller in ('main.mjs', 'main.ts'):
                (root / caller).write_text(JS_CALLER)
            findings = self.project(root)
            for caller in ('main.mjs', 'main.ts'):
                self.assert_calls(findings, caller, 'pkg/helper.mjs')
            runtime = subprocess.check_output(['node', '--input-type=module', '-e',
                       "import { start, silent, forward } from './main.mjs'; "
                       "import { read } from './pkg/helper.mjs'; "
                       'start(); if (silent() !== undefined) process.exit(1); console.log(forward(), read());'],
                       cwd=root, text=True)
            self.assertEqual('event\n42 0\n', runtime)
