"""Exercise formal-only comparison through its public CLI."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
BASE = Path('_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43')
MANIFEST = BASE / '_SPEC/AN-S-3059-SPEC-COMPONENT_MANIFEST--declare-workbench-backend.md'
CONTRACT = BASE / 'FEATURE_WORKBENCH_BACKEND_C45/AN-S-3185-SWD-COMPONENT_CONTRACT--run-one-read-only-workbench-query.md'
SOLUTION = BASE / 'FEATURE_WORKBENCH_BACKEND_C45/01_TIER_1_ARCHITECTURE/AN-S-3371-DES-DECISION--run-one-validated-read-only-workbench-query.md'
MODULE = 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.backend_http_compare'


class FormalHttpTests(unittest.TestCase):
    def test_live_and_mutated_specs(self):
        lean = os.environ.get('LEAN_BIN', 'lean')
        if not shutil.which(lean):
            self.skipTest('Lean unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in (MANIFEST, CONTRACT, SOLUTION):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            def run():
                result = subprocess.run([sys.executable, '-m', MODULE, '--root', str(root),
                                         '--lean', lean, '--formal-only'],
                                        capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 1, result.stderr)
                return json.loads(result.stdout)
            report = run()
            self.assertEqual(report['status'], 'unresolved')
            self.assertEqual({r['status'] for r in report['manifest_contract']}, {'match'})
            self.assertIn('AN-S-3185@11', report['solution_contract']['declared_pins'])
            self.assertEqual(report['manifest_unmodeled_count'], 2)
            self.assertEqual(len(report['manifest_solution']), 7)
            self.assertEqual(len(report['contract_solution']), 25)
            manifest = root / MANIFEST
            original = manifest.read_text()
            marker = "'tool_api': {\n                        'transport': 'http',"
            self.assertIn(marker, original)
            manifest.write_text(original.replace(marker, marker.replace("'http'", "'stdio'")))
            report = run()
            self.assertEqual(report['status'], 'mismatch')
            protocol = next(r for r in report['manifest_contract']
                            if r['check'] == 'interface.protocol')
            self.assertEqual((protocol['manifest'], protocol['contract'], protocol['status']),
                             (['stdio'], ['http'], 'mismatch'))
            manifest.write_text(original.replace("'failure_fields': ['code', 'message', 'tool_result'],", ''))
            report = run()
            self.assertEqual(next(r for r in report['manifest_contract']
                                  if r['check'] == 'error_handling.error_fields')['status'], 'unresolved')
            manifest.write_text(original)
            contract = root / CONTRACT
            text = contract.read_text().replace('                "arguments",\n', '')
            contract.write_text(text)
            report = run()
            self.assertEqual(next(r for r in report['manifest_contract']
                                  if r['check'] == 'input_format.fields')['status'], 'mismatch')


if __name__ == '__main__':
    unittest.main()
