"""Compiled Role directories derive only from adopted order declarations."""
from pathlib import Path
import json
import tempfile
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_layout__pub import compile_role_folders  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.legacy_candidate_schema__pub import compile_candidate_schema, load_candidate_schema  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_lifecycle_formal_placement import role_source, native_body, status_rule


def order(role, number):
    return f'Atom/(.Header.Context.Role := {role}) >| (Role Order Number == {number})'


class RoleDirectoryTests(unittest.TestCase):
    def test_source_order_controls_encoding_and_keeps_gaps(self):
        records = [(order('Concern', 4), 'CA-R-887@3'),
                   (order('"Analysis and Advisory"', 2), 'CA-R-90@7'),
                   (order('Operations', 9), 'CA-R-654321@2'),
                   (order('Plan', 13), 'CA-R-5001@1')]
        result = compile_role_folders(records)
        self.assertEqual(('04_concern', 'CA-R-887@3'), result['Concern'])
        self.assertEqual(('02_analysis_and_advisory', 'CA-R-90@7'), result['Analysis and Advisory'])
        self.assertEqual(('09_operations', 'CA-R-654321@2'), result['Operations'])
        self.assertEqual(('13_plan', 'CA-R-5001@1'), result['Plan'])
        self.assertFalse(any(folder.startswith('08_') for folder, _ in result.values()))

    def test_duplicate_and_malformed_order_claims_fail(self):
        for records in [
            [(order('Concern', 1), 'A'), (order('Concern', 2), 'B')],
            [(order('Concern', 1), 'A'), (order('Plan', 1), 'B')],
            [(order('Concern', 'not_a_number'), 'A')],
            [('Atom/(.Header.Context.Role := Concern) >| (Role Order Number = 1)', 'A')],
        ]:
            with self.subTest(records=records), self.assertRaises(ValueError):
                compile_role_folders(records)


class RoleDirectorySourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.orders = [('Concern', 4), ('Analysis and Advisory', 2), ('Operations', 9), ('Plan', 13)]
        self.generic = {'kind': 'role_root'}
        self.status = (status_rule('draft', 'role', 'draft'), status_rule('archived', 'role', 'archived'),
                       status_rule('*', 'container', '<lowercase status>'), status_rule('active', 'container', ''))

    def write_sources(self, *, orders=None, generic=True):
        statements = self.orders if orders is None else orders
        for path in self.root.glob('CA-R-80*.md'):
            path.unlink()
        selected = dict(statements)
        for index, (role, _) in enumerate(self.orders):
            role_source(self.root, role, selected.get(role), f'CA-R-80{index}')
        rules = ((self.generic,) if generic else ()) + self.status
        (self.root / 'CA-D-7913.md').write_text(
            '---\natom_id: CA-D-7913\nrole: Delivery\nform: File Layout\nstatus: Active\nversion: 2\n'
            'topics:\n  main_subject: ANECHOIC_MODEL <+ Carrier\n---\n' + native_body(rules))

    def test_generic_delivery_and_role_orders_compile_from_arbitrary_pins(self):
        self.write_sources()
        payload = json.loads(compile_candidate_schema(self.root))
        asset = self.root.parent / (self.root.name + '-role-schema.json')
        self.addCleanup(asset.unlink, missing_ok=True)
        asset.write_text(json.dumps(payload))
        rules = load_candidate_schema(asset).placement
        self.assertEqual('04_concern', rules.role_folder('Concern'))
        self.assertEqual('02_analysis_and_advisory', rules.role_folder('Analysis and Advisory'))
        self.assertEqual('09_operations', rules.role_folder('Operations'))
        self.assertEqual('13_plan', rules.role_folder('Plan'))
        with self.assertRaises(ValueError):
            rules.role_folder('Delivery')
        self.assertFalse(any(folder.startswith('08_') for folder in rules.role_folders.values()))
        self.assertEqual({('CA-R-800', 1), ('CA-R-801', 1), ('CA-R-802', 1), ('CA-R-803', 1), ('CA-D-7913', 2)},
                         {(pin['atom_id'], pin['version']) for pin in rules.sources})

    def test_missing_role_order_or_generic_delivery_fails(self):
        for orders, generic in [(self.orders[:-1], True), (self.orders, False)]:
            with self.subTest(orders=orders, generic=generic):
                self.write_sources(orders=orders, generic=generic)
                with self.assertRaises(ValueError):
                    compile_candidate_schema(self.root)


if __name__ == '__main__':
    unittest.main()
