"""Bounded Node/Autoform comparison, using Autoform's numeric proof harness."""

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


# The two aliases observe one array. The packed return exposes mutation,
# output computation, restoration and the subsequent silent observation.
SOURCE = '''function indexTrace(a, b) {
  let state = [];
  state.push(a);
  let alias = state;
  alias[0] = b;
  let mutation = state[0];
  let output = state[0] + 1;
  alias[0] = a;
  let restored = state[0];
  let silent = state[0];
  return mutation * 1000 + output * 100 + restored * 10 + silent;
}'''


@unittest.skipUnless(os.environ.get('AUTOFORM_CHECKOUT'), 'Set AUTOFORM_CHECKOUT for the Autoform canary')
class AutoformNodeStateTests(unittest.TestCase):
    def test_node_observations_are_kernel_proved(self):
        checkout = Path(os.environ['AUTOFORM_CHECKOUT']).resolve(strict=True)
        with TemporaryDirectory(prefix='anechoic-node-effects-') as tmp:
            test = Path(tmp) / 'test_state.py'
            test.write_text('''from test_source_numeric import CASES, SOURCES, numeric_env
from test_source_numeric import test_joern_native_numeric as prove_numeric

def test_state(tmp_path, numeric_env, monkeypatch):
    monkeypatch.setitem(SOURCES, 'js', ('JAVASCRIPT', 'numbers.js', %r))
    monkeypatch.setitem(CASES, 'js', [('indexTrace', [1, 2]), ('indexTrace', [3, 4])])
    prove_numeric('js', tmp_path, numeric_env)
''' % SOURCE)
            env = dict(os.environ, AUTOFORM_TEST_JOERN='1', AUTOFORM_REQUIRE_LEAN='1')
            env['PYTHONPATH'] = str(checkout / 'tests') + os.pathsep + env.get('PYTHONPATH', '')
            subprocess.run([sys.executable, '-m', 'pytest', '-q', test], cwd=checkout,
                           env=env, check=True, timeout=900)
