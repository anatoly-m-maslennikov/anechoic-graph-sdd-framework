from pathlib import Path
import sys
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from ATOM_LIFECYCLE.atom_population import validate_atom_population
from ATOM_LIFECYCLE.common import InputError
from ATOM_LIFECYCLE.source import SourcePin, SourceSelectionError


def pin(version, status, summary='Same'):
    name = f'CA-R-1@{version}' + ('-draft' if status == 'Draft' else '')
    return SourcePin(Path(name + '.md'), 'CA-R-1', name, version, status, 'digest',
                     f'---\natom_id: CA-R-1\n---\n## Summary\n\n{summary}\n'.encode(), {})


class PopulationTests(unittest.TestCase):
    def validate(self, peers, *, version=3, status='Active', summary='Same', replaced=()):
        with patch('ATOM_LIFECYCLE.atom_population.select_all_revisions', return_value=peers):
            return validate_atom_population(object(), atom_id='CA-R-1', version=version,
                                            status=status, summary=summary, replaced=replaced)

    def test_uniqueness_and_exact_replacement(self):
        old, draft = pin(1, 'Archived'), pin(3, 'Draft')
        with self.assertRaises(InputError):
            self.validate((old, draft))
        self.assertEqual((old, draft), self.validate((old, draft), replaced=(draft,)))
        with self.assertRaises(SourceSelectionError):
            self.validate((old,), replaced=(draft,))

    def test_summary_applies_only_to_published_revisions(self):
        old, draft = pin(1, 'Archived', 'Other'), pin(2, 'Draft', 'Different')
        with self.assertRaises(InputError):
            self.validate((old, draft))
        self.validate((old, draft), status='Draft')
        self.validate((draft,), status='Active')


if __name__ == '__main__':
    unittest.main()
