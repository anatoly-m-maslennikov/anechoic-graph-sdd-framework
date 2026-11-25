import importlib.util
from pathlib import Path
import unittest

import duckdb

spec = importlib.util.spec_from_file_location('analysis_projection', Path(__file__).parent.parent / 'analysis_projection.py')
projection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(projection)


class AnalysisProjectionTest(unittest.TestCase):
    def setUp(self):
        self.db = db = duckdb.connect()
        self.addCleanup(db.close)
        db.execute('CREATE TABLE mrt_atom_references (reference VARCHAR, exact_ref VARCHAR)')
        db.execute('CREATE TABLE mrt_atom_graph_relations (source_kind VARCHAR, source_ref VARCHAR, target_kind VARCHAR, target_ref VARCHAR, relation_type VARCHAR, derived BOOLEAN)')
        db.execute("INSERT INTO mrt_atom_references VALUES ('AN-1', 'AN-1@1'), ('AN-2', 'AN-2@1')")
        db.execute("INSERT INTO mrt_atom_graph_relations VALUES ('Atom','AN-1','Atom','AN-2','IS_CONTAINED_BY',false), ('Atom','AN-2','Component','C1','CONTAINED_BY',false)")
        db.execute('CREATE TABLE mrt_real_graph_package_imports (source_key VARCHAR, target_key VARCHAR, occurrence_count BIGINT)')
        db.execute("INSERT INTO mrt_real_graph_package_imports VALUES ('p', 'q', 3)")
        projection.prepare(db)
        projection.replace_code(db, [
            ('Package', 'p', 'src.py', 'implementation', 100, 10),
            ('Package', 'p', 'test.py', 'test_code', 20, 2),
            ('Package', 'p', 'image', 'test_assets', 50, None),
            ('Package', 'q', 'q.py', 'implementation', 10, None),
        ])
        projection.replace_spec(db, [
            ('AN-1@1', 20, 4, 10, 2),
            ('AN-2@1', 20, 4, 10, 2),
        ])
        projection.replace_bindings(db, [('p', 'AN-1@1'), ('p', 'AN-2@1'), ('q', 'AN-2@1')])

    def test_ratios_bindings_profiles_and_replacement_validation(self):
        db = self.db
        row = db.execute("""SELECT numerator_bytes, denominator_bytes, bytes_ratio, numerator_lines,
            denominator_lines, partial_spec, test_assets_bytes, test_assets_unknown_lines
            FROM biz_architecture_ratios WHERE scope_id='p' AND code_population='implementation_and_test_code'
            AND spec_population='body'""").fetchone()
        self.assertEqual(row, (120, 10, 12.0, 12, 2, True, 50, 1))
        self.assertEqual(db.execute("""SELECT spec_population, numerator_bytes, denominator_bytes,
            bytes_ratio, numerator_lines, denominator_lines, lines_ratio FROM biz_architecture_ratios
            WHERE scope_id='p' AND code_population='test_code' ORDER BY spec_population""").fetchall(),
            [('body', 20, 10, 2.0, 2, 2, 1.0), ('full', 20, 20, 1.0, 2, 4, 0.5)])
        self.assertEqual(db.execute("SELECT count(*) FROM biz_architecture_ratios WHERE scope_id='p'").fetchone()[0], 6)
        self.assertEqual(db.execute("SELECT numerator_lines, bytes_ratio FROM biz_architecture_ratios WHERE scope_id='q' AND code_population='implementation' LIMIT 1").fetchone(), (None, None))
        self.assertEqual(db.execute("SELECT outgoing_packages, outgoing_occurrences FROM biz_package_review_profiles WHERE package_key='p'").fetchone(), (1, 3))
        self.assertEqual(db.execute("SELECT relative_path FROM biz_package_largest_files WHERE package_key='p' AND size_rank=1").fetchone(), ('src.py',))
        with self.assertRaises(ValueError):
            projection.replace_code(db, [('Package', 'p', 'src.py', 'implementation', 1, 1)] * 2)
        with self.assertRaises(ValueError):
            projection.replace_bindings(db, [('p', 'AN-1')] * 2)
        self.assertEqual(db.execute('SELECT count(*) FROM biz_architecture_code_metrics').fetchone()[0], 4)
        self.assertEqual(db.execute('SELECT count(*) FROM mrt_real_graph_package_spec_bindings').fetchone()[0], 3)

    def test_delta_batch_preserves_unaffected_rows_and_rejects_conflicts(self):
        db = self.db
        before = db.execute('SELECT * FROM biz_architecture_spec_metrics ORDER BY atom_ref').fetchall()
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            projection.apply_spec_delta(db, ('AN-1@1',), [('AN-2@1', 1, 1, 1, 1)])
        self.assertEqual(db.execute('SELECT * FROM biz_architecture_spec_metrics ORDER BY atom_ref').fetchall(), before)
        for refs, rows in [(['AN-1@1', 'AN-1@1'], []), ([], [('AN-3@1', 1, 1, 1, 1)] * 2)]:
            with self.assertRaises(ValueError):
                projection.apply_spec_delta(db, refs, rows)
        self.assertEqual(db.execute('SELECT * FROM biz_architecture_spec_metrics ORDER BY atom_ref').fetchall(), before)
        projection.apply_spec_delta(db, ('AN-1@1', 'missing'), [('AN-1@1', 5, 2, 3, 1), ('AN-3@1', 4, 2, 2, 1)])
        self.assertEqual(db.execute('SELECT * FROM biz_architecture_spec_metrics ORDER BY atom_ref').fetchall(),
                         [('AN-1@1', 5, 2, 3, 1), before[1], ('AN-3@1', 4, 2, 2, 1)])
        projection.apply_spec_delta(db, ('AN-1@1',), ())
        self.assertEqual(db.execute('SELECT count(*) FROM biz_architecture_spec_metrics').fetchone(), (2,))
        projection.replace_code(db, ())
        projection.replace_spec(db, ())
        projection.replace_bindings(db, ())
        for table in ('biz_architecture_code_metrics', 'biz_architecture_spec_metrics', 'mrt_real_graph_package_spec_bindings'):
            self.assertEqual(db.execute(f'SELECT count(*) FROM {table}').fetchone(), (0,))

    def test_native_sizes_and_delta_follow_current_containment(self):
        db = self.db
        with self.assertRaisesRegex(ValueError, 'no Spec size evidence'):
            projection.snapshot_sizes({})
        projection.replace_spec(db, [('AN-1@1', 40, 8, 20, 4)])
        self.assertEqual(db.execute("SELECT denominator_bytes FROM biz_architecture_ratios WHERE scope_id='p' AND spec_population='full' LIMIT 1").fetchone(), (40,))
        self.assertEqual(db.execute("SELECT denominator_bytes FROM biz_architecture_ratios WHERE scope_id='C1' AND spec_population='full' LIMIT 1").fetchone(), (40,))
        projection.apply_spec_delta(db, [], [])
        projection.apply_spec_delta(db, ['AN-1@1'], [('AN-1@2', 60, 12, 30, 6)])
        db.execute("UPDATE mrt_atom_references SET exact_ref='AN-1@2' WHERE reference='AN-1'")
        self.assertEqual(db.execute("SELECT denominator_bytes FROM biz_architecture_ratios WHERE scope_id='C1' AND spec_population='full' LIMIT 1").fetchone(), (60,))
        with self.assertRaises(ValueError):
            projection.apply_spec_delta(db, [], [('AN-1@2', 1, 1, 1, 1)])
        db.execute("UPDATE mrt_atom_graph_relations SET target_ref='C2' WHERE source_ref='AN-2'")
        self.assertEqual(db.execute("SELECT denominator_bytes FROM biz_architecture_ratios WHERE scope_id='C2' AND spec_population='full' LIMIT 1").fetchone(), (60,))


if __name__ == '__main__':
    unittest.main()
