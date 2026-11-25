"""Controls for the bounded saved-result graph model."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class SavedQueryControls(unittest.TestCase):
    def run_case(self, source, order, edges, released=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backend = root / 'FEATURE_WORKBENCH_BACKEND'
            backend.mkdir()
            (backend / 'moved.py').write_text(source)
            case = root / 'graph.json'
            case.write_text(json.dumps({'order': order, 'edges': edges, 'released': released if released is not None else []}))
            run = subprocess.run([sys.executable, '-B', str(HERE / 'analyze.py'), str(root),
                                  '--lean', os.environ.get('LEAN_BIN') or shutil.which('lean') or 'lean',
                                  '--file', 'FEATURE_WORKBENCH_BACKEND/moved.py', '--case', str(case)],
                                 capture_output=True, text=True, timeout=45, check=True)
            return json.loads(run.stdout)

    def test_graph_order_and_fan_in(self):
        fixed = (HERE / 'fixed.py.txt').read_text()
        edges = [['A', 'C'], ['B', 'C']]
        good = self.run_case(fixed, ['B', 'A', 'C'], edges)
        self.assertEqual(good, {'findings': [], 'unresolved': []})
        bad = self.run_case(fixed, ['A', 'C', 'B'], edges)
        self.assertEqual(len(bad['findings']), 1)
        self.assertIn('C reads B', bad['findings'][0]['detail'])
        self.assertEqual(bad['unresolved'], [])
        chain = self.run_case(fixed, ['A', 'B', 'C'], [['A', 'B'], ['B', 'C']])
        self.assertEqual(chain, {'findings': [], 'unresolved': []})
        cycle = self.run_case(fixed, ['A', 'B'], [['A', 'B'], ['B', 'A']])
        self.assertIn('cycle', cycle['unresolved'][0]['detail'])

    def test_historical_and_readable_effects(self):
        revision = '415fc9dcfb6dc8cc6a4e3b8e6ef7ecd60e4cabe7'
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', revision], text=True).splitlines()
        source_path = next(p for p in paths if p.endswith('/query_store.py') and 'FEATURE_WORKBENCH_BACKEND' in p)
        historical = subprocess.check_output(['git', 'show', f'{revision}:{source_path}'], text=True)
        good = self.run_case(historical, ['A', 'B'], [['A', 'B']])
        self.assertEqual(good, {'findings': [], 'unresolved': []})
        guard = '            if (selected is not None or tables is not None) and old_id != selected:'
        changed = historical.replace(guard, guard + "\n                self._connection.execute('DELETE FROM workbench_results.x')")
        self.assertEqual(self.run_case(changed, ['A', 'B'], [['A', 'B']]), good)
        reversed_guard = changed.replace('selected is not None or tables is not None', 'selected is None or tables is not None')
        self.assertTrue(self.run_case(reversed_guard, ['A', 'B'], [['A', 'B']])['unresolved'])
        with_else = changed.replace('            new_id, result = self._materialize', '            else:\n                pass\n            new_id, result = self._materialize')
        self.assertTrue(self.run_case(with_else, ['A', 'B'], [['A', 'B']])['unresolved'])
        bad = self.run_case(historical, ['B', 'A'], [['A', 'B']])
        self.assertEqual(len(bad['findings']), 1)
        self.assertEqual(bad['unresolved'], [])
        variant = """class Store:
    def prepare_result_rebuild(self):
        staged = {}
        for old_id, old in self._results.items():
            new_id, result = self._materialize(old.sql, old.preview, admitted=True)
            self._connection.execute(f'DROP TABLE workbench_results.{quote_identifier(old.table_name)}')
            self._connection.execute(f'ALTER TABLE workbench_results.{quote_identifier(result.table_name)} RENAME TO {quote_identifier(old.table_name)}')
            staged[old_id] = (new_id, result)
            result.table_name = old.table_name
        return staged
"""
        self.assertEqual(self.run_case(variant, ['A', 'B'], [['A', 'B']]), good)
        premature = variant.replace('            staged[old_id] = (new_id, result)\n            result.table_name = old.table_name', '            staged[old_id] = (new_id, result)').replace("            self._connection.execute(f'ALTER TABLE", "            result.table_name = old.table_name\n            self._connection.execute(f'ALTER TABLE")
        self.assertTrue(self.run_case(premature, ['A', 'B'], [['A', 'B']])['unresolved'])
        no_guard = historical.replace('            if old.table_name.lower() not in retained:\n                continue\n', '')
        self.assertTrue(self.run_case(no_guard, ['A', 'B'], [['A', 'B']])['unresolved'])
        stale = self.run_case(variant, ['B', 'A'], [['A', 'B']])
        self.assertEqual(len(stale['findings']), 1)
        self.assertEqual(stale['unresolved'], [])
        changed_sql = variant.replace('DROP TABLE workbench_results.', 'DELETE FROM workbench_results.')
        self.assertTrue(self.run_case(changed_sql, ['A', 'B'], [['A', 'B']])['unresolved'])
        unknown = variant.replace('            staged[old_id] = (new_id, result)', '            self.other_effect()\n            staged[old_id] = (new_id, result)')
        self.assertTrue(self.run_case(unknown, ['A', 'B'], [['A', 'B']])['unresolved'])

    def test_production_helper_and_unsupported_variants(self):
        root = next(p for p in HERE.parents if (p / '_anechoic_anechoic').is_dir())
        source = (root / 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/query_results.py').read_text()
        good = self.run_case(source, ['A', 'B'], [['A', 'B']])
        self.assertEqual(good, {'findings': [], 'unresolved': []})
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp)
            target = checkout / 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/query_results.py'
            target.parent.mkdir(parents=True)
            target.write_text(source)
            run = subprocess.run([sys.executable, '-B', str(HERE / 'analyze.py'), str(checkout),
                                  '--lean', os.environ.get('LEAN_BIN') or shutil.which('lean') or 'lean'],
                                 capture_output=True, text=True, timeout=45, check=True)
            self.assertEqual(json.loads(run.stdout), good)
            historical = checkout / 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_WORKBENCH_BACKEND/query_store.py'
            historical.parent.mkdir(parents=True)
            historical.write_text(source)
            run = subprocess.run([sys.executable, '-B', str(HERE / 'analyze.py'), str(checkout),
                                  '--lean', os.environ.get('LEAN_BIN') or shutil.which('lean') or 'lean'],
                                 capture_output=True, text=True, timeout=45, check=True)
            self.assertTrue(json.loads(run.stdout)['unresolved'])
        bind = 'f"ALTER TABLE workbench_results.{quote_identifier(result.table_name)} "'
        self.assertIn(bind, source)
        changed_sql = source.replace(bind, bind.replace('ALTER TABLE', 'DELETE FROM'), 1)
        self.assertTrue(self.run_case(changed_sql, ['A', 'B'], [['A', 'B']])['unresolved'])
        statement = '''        self._connection.execute(
            f"ALTER TABLE workbench_results.{quote_identifier(result.table_name)} "
            f"RENAME TO {quote_identifier(old.table_name)}"
        )
'''
        self.assertIn(statement, source)
        lost = self.run_case(source.replace(statement, '', 1), ['A', 'B'], [['A', 'B']])
        self.assertEqual(len(lost['findings']), 1)
        self.assertEqual(lost['unresolved'], [])
        variants = [source.replace('        return new_id, result\n', '        staged[old_id] = (new_id, result)\n        return new_id, result\n', 1),
                    source.replace('self._stage_result_replacement(old)', 'self._stage_result_replacement(old, old)', 1),
                    source.replace('return new_id, result\n', 'return result, new_id\n', 1),
                    source.replace('    def _stage_result_replacement(self, old:', '    @staticmethod\n    def _stage_result_replacement(self, old:', 1),
                    source.replace('        new_id, result = self._materialize(old.sql', '        self._stage_result_replacement = other\n        new_id, result = self._materialize(old.sql', 1)]
        for variant in variants:
            with self.subTest(variant=variants.index(variant)):
                self.assertTrue(self.run_case(variant, ['A', 'B'], [['A', 'B']])['unresolved'])

    def test_production_released_guard(self):
        root = next(p for p in HERE.parents if (p / '_anechoic_anechoic').is_dir())
        source = (root / 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/query_results.py').read_text()
        guard = '            if old.table_name.lower() not in retained:\n'
        self.assertEqual(source.count(guard), 1)
        mutant = source.replace(guard, '            if old.table_name.lower() not in retained or old.released:\n', 1)
        clean = {'findings': [], 'unresolved': []}
        self.assertEqual(self.run_case(source, ['A', 'B'], [['A', 'B']], ['A']), clean)
        self.assertEqual(self.run_case(mutant, ['A', 'B'], [['A', 'B']]), clean)
        bad = self.run_case(mutant, ['A', 'B'], [['A', 'B']], ['A'])
        self.assertEqual(bad['unresolved'], [])
        self.assertEqual(len(bad['findings']), 1)
        self.assertIn('B reads A before', bad['findings'][0]['detail'])
        for invalid in (['C'], ['A', 'A'], 'A'):
            self.assertTrue(self.run_case(mutant, ['A', 'B'], [['A', 'B']], invalid)['unresolved'])

    def test_production_reverse_iteration(self):
        root = next(p for p in HERE.parents if (p / '_anechoic_anechoic').is_dir())
        source = (root / 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/query_results.py').read_text()
        loop = 'for old_id, old in self._results.items():'
        self.assertEqual(source.count(loop), 1)
        reverse = source.replace(loop, 'for old_id, old in reversed(self._results.items()):', 1)
        self.assertEqual(self.run_case(source, ['A', 'B'], [['A', 'B']]), {'findings': [], 'unresolved': []})
        self.assertEqual(self.run_case(reverse, ['A', 'B'], []), {'findings': [], 'unresolved': []})
        bad = self.run_case(reverse, ['A', 'B'], [['A', 'B']])
        self.assertEqual(bad['unresolved'], [])
        self.assertEqual(len(bad['findings']), 1)
        self.assertIn('B reads A before', bad['findings'][0]['detail'])
        for variant in (reverse + '\nreversed = list\n', reverse.replace('reversed(self._results.items())', 'reversed(list(self._results.items()))')):
            self.assertTrue(self.run_case(variant, ['A', 'B'], [['A', 'B']])['unresolved'])

    def test_unreachable_partial_selection(self):
        fixed = (HERE / 'fixed.py.txt').read_text()
        guard = '            if selected is not None and old_id not in selected:'
        changed = fixed.replace(guard, guard + "\n                self._connection.execute('DELETE FROM workbench_results.x')\n                self.other_effect()")
        self.assertEqual(self.run_case(changed, ['A', 'B'], [['A', 'B']]), {'findings': [], 'unresolved': []})
        reversed_guard = changed.replace('if selected is not None and old_id not in selected:', 'if selected is None and old_id not in selected:')
        self.assertTrue(self.run_case(reversed_guard, ['A', 'B'], [['A', 'B']])['unresolved'])
        with_else = changed.replace('            new_id, result = self._materialize', '            else:\n                pass\n            new_id, result = self._materialize')
        self.assertTrue(self.run_case(with_else, ['A', 'B'], [['A', 'B']])['unresolved'])

    def test_before_and_fixed(self):
        before = self.run_case((HERE / 'before.py.txt').read_text(), ['A', 'B'], [['A', 'B']])
        fixed = self.run_case((HERE / 'fixed.py.txt').read_text(), ['A', 'B'], [['A', 'B']])
        self.assertEqual(len(before['findings']), 1)
        self.assertEqual(before['unresolved'], [])
        self.assertEqual(fixed, {'findings': [], 'unresolved': []})

    def test_unsupported_conditional_effect(self):
        fixed = (HERE / 'fixed.py.txt').read_text()
        source = fixed.replace('            new_id, result = self._materialize(old.sql, old.preview, admitted=True)',
                               '            if old_id:\n                new_id, result = self._materialize(old.sql, old.preview, admitted=True)')
        result = self.run_case(source, ['A', 'B'], [['A', 'B']])
        self.assertEqual(result['findings'], [])
        self.assertTrue(result['unresolved'])


if __name__ == '__main__':
    unittest.main()
