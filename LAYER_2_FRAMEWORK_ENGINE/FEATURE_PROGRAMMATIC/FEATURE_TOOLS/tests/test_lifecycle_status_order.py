"""Status order declarations and Delivery templates compile into placement."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from ATOM_LIFECYCLE.candidate_schema import compile_candidate_schema, load_candidate_schema  # noqa: E402

from test_lifecycle_formal_placement import role_source, native_body, status_rule, carrier


def status_path(name, path, *, plan=False):
    base = 'container' if path.startswith('<container>') else 'role'
    folder = path.rsplit('/', 1)[-1] if '/' in path else ''
    return status_rule(name.lower(), base, folder, 'plan' if plan else None)


class StatusOrderPlacementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.orders = {'Draft': 7, 'Active': 12, 'Backlog': 14, 'Done': 31, 'Archived': 115}
        self.write_requirements()
        self.delivery('CA-D-881', 'CAPRMEDIO_MODEL <+ Carrier',
                      {'kind': 'role_root'})
        prefix = 'CAPRMEDIO_MODEL <+ Atom.Header.State.Status >| Status Group := '
        self.delivery('CA-D-882', prefix + 'Draft', status_path('Draft', '<owning scope unit>/<role folder>/<status folder>'))
        self.delivery('CA-D-883', prefix + 'Archived', status_path('Archived', '<owning scope unit>/<role folder>/<status folder>'))
        self.delivery('CA-D-884', prefix + 'Current', [status_rule('*', 'container', '<status folder>'), status_path('Active', '<container>')])
        self.delivery('CA-D-885',
                      'CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.State.Status >| Status Group := Backlog',
                      status_path('Backlog', '<owning scope unit>/<role folder>/<status folder>', plan=True))

    def write_requirements(self, orders=None):
        orders = self.orders if orders is None else orders
        role_source(self.root, 'Plan', 3, 'CA-R-71591')
        code = ('from caprmedio.formal_claims import declare_entity\n'
                'declare_entity(entity_name="Status", relation_name="IS_PROPERTY_OF", '
                f'base_path="Atom.Header.State", allowed_values={tuple(orders)!r}, status_order_numbers={orders!r})')
        (self.root / 'CA-R-71593.md').write_text(carrier('CA-R-71593', 'Requirement', 'Active',
            f'## Claim\n### Formal Claim\n```python\n{code}\n```\n',
            'CAPRMEDIO_MODEL <+ Atom.Header.State.Status'))

    def delivery(self, atom_id, subject, claim):
        (self.root / f'{atom_id}.md').write_text(
            f'---\natom_id: {atom_id}\nrole: Delivery\nform: File Layout\nstatus: Active\nversion: 2\n'
            f'topics:\n  main_subject: {json.dumps(subject)}\n---\n' +
            native_body(claim if isinstance(claim, (tuple, list)) else (claim,)))

    def compile(self):
        asset = self.root.parent / (self.root.name + '-status-order.json')
        self.addCleanup(asset.unlink, missing_ok=True)
        asset.write_bytes(compile_candidate_schema(self.root))
        return load_candidate_schema(asset).placement

    def test_order_numbers_derive_role_and_container_folders(self):
        rules = self.compile()
        for status, expected in {'Draft': ('role', '007_draft'), 'Backlog': ('role', '014_backlog'),
                                 'Active': ('container', ''), 'Done': ('container', '031_done'),
                                 'Archived': ('role', '115_archived')}.items():
            with self.subTest(status=status):
                self.assertEqual(expected, rules.placement('Plan', status))
        self.assertIn('CA-R-71593', {pin['atom_id'] for pin in rules.sources})

    def test_missing_or_duplicate_status_number_fails(self):
        for orders in [{key: value for key, value in self.orders.items() if key != 'Backlog'},
                       {**self.orders, 'Done': self.orders['Draft']}]:
            with self.subTest(orders=orders):
                self.write_requirements(orders)
                with self.assertRaises(ValueError):
                    self.compile()


if __name__ == '__main__':
    unittest.main()
