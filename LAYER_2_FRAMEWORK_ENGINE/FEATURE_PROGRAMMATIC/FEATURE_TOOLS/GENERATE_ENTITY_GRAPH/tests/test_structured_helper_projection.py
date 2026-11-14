from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cfel_claim_constraints import extract_claim_constraints


def carrier(code, subject='Node'):
    return {'source': {'atom_id': 'CA-R-1'}, 'subjects': {'active': subject},
            'body': '## Claim\n### Formal Claim\n```python\n' + code + '\n```\n',
            'read_view': {'content_role': 'Requirement', 'type': 'Declaration'}}


class StructuredHelperProjectionTests(unittest.TestCase):
    def test_live_helpers_match_old_records_without_compiler(self):
        samples = [
            ("# model\ncomposition(container='Aspects', parts=('Product',))", 'Node'),
            ("# instances\nrelation(source='Step', name='RUNS', target='Action', target_count='1')", 'Node'),
            ("# instances\ndeliver(source='Atom//$atom', carrier='Carrier//$carrier')", 'Node'),
            ("# model\nset_value(address='Operator//Addition', value='\"+\"')", 'CAPRMEDIO_MODEL <+ CFEL <+ Operator//Addition'),
        ]
        for code, subject in samples:
            item = carrier(code, subject)
            rows, diagnostics = extract_claim_constraints(item)
            self.assertEqual(len(rows) + len(diagnostics), 1)
            self.assertFalse(any(d.get('code') == 'python-formal-claim-invalid' for d in diagnostics))


if __name__ == '__main__':
    unittest.main()
