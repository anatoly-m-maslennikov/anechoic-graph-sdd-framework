from pathlib import Path
from contextlib import redirect_stderr
from io import StringIO
from tempfile import TemporaryDirectory
import unittest

import duckdb

from FEATURE_WORKBENCH_BACKEND.spec_trace import PILOT, SpecTraceStore


class SpecTraceTests(unittest.TestCase):
    def test_mixed_legacy_and_native_pins_preserve_exact_versions(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        package = root / PILOT / 'example'
        package.mkdir(parents=True)
        (package / 'unit.py').write_text('pass')
        sidecar = package / 'unit.py.spec_trace.md'
        sidecar.write_text('## Implements\n- CA-R-123@4\n- AN-S-125@12\n- AN-P-9@2\n')
        connection = self.enterContext(duckdb.connect(':memory:'))
        store = SpecTraceStore(connection, root)
        store.initialize()
        store.refresh()
        pins = 'SELECT atom_id, version FROM implementation_rmedo ORDER BY atom_id'
        self.assertEqual(connection.execute(pins).fetchall(),
                         [('AN-P-9', 2), ('AN-S-125', 12), ('CA-R-123', 4)])

        for invalid in ('AN-T-1@1', 'AN-S-1', 'AN-S-1@1-draft', 'AN-S-1@0'):
            sidecar.write_text(f'## Implements\n- CA-R-123@4\n- {invalid}\n')
            with redirect_stderr(StringIO()):
                store.refresh([sidecar])
            self.assertEqual(connection.execute(pins).fetchall(), [])

    def test_sidecar_edits_replace_only_the_owner_pins(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        package = root / PILOT / 'example'
        package.mkdir(parents=True)
        (package / 'unit.py').write_text('pass')
        module_trace = package / 'unit.py.spec_trace.md'
        module_trace.write_text('## Implements\n- CA-R-123@1\n')
        package_trace = package / 'example.p.spec_trace.md'
        package_trace.write_text('## Applies\n- CA-M-9@1\n')
        connection = self.enterContext(duckdb.connect(':memory:'))
        store = SpecTraceStore(connection, root)
        store.initialize()
        store.refresh()
        pins = 'SELECT atom_id, version FROM implementation_rmedo ORDER BY atom_id'

        module_trace.write_text('## Implements\n- CA-R-123@2\n')
        package_trace.write_text('## Applies\n- CA-M-9@2\n')
        store.refresh([package_trace])
        self.assertEqual(connection.execute(pins).fetchall(), [('CA-M-9', 2), ('CA-R-123', 1)])

        package_trace.write_text('## Applies\n- CA-M-9@3\n- invalid\n')
        stderr = StringIO()
        with redirect_stderr(stderr):
            store.refresh([package_trace])
        self.assertIn(f'{package_trace}:3:', stderr.getvalue())
        self.assertEqual(connection.execute(pins).fetchall(), [('CA-R-123', 1)])

    def test_package_yaml_precedence_validation_and_refresh(self):
        root = Path(self.enterContext(TemporaryDirectory()))
        package = root / PILOT / 'full_package_C43'
        package.mkdir(parents=True)
        canonical = package / 'full_package_C43__spec_bind.yaml'
        legacy = package / 'full_package_C43.p.spec_trace.md'
        legacy.write_text('## Applies\n- CA-M-9@1\n')
        connection = self.enterContext(duckdb.connect(':memory:'))
        store = SpecTraceStore(connection, root)
        store.initialize()
        store.refresh()
        query = 'SELECT entry_kind, atom_id, version FROM implementation_rmedo ORDER BY entry_kind'
        self.assertEqual(connection.execute(query).fetchall(), [('applies', 'CA-M-9', 1)])

        canonical.write_text('implements:\n  - CA-R-123@5\napplies:\n  - AN-S-9@2\n')
        store.refresh([canonical])
        self.assertEqual(connection.execute(query).fetchall(),
                         [('applies', 'AN-S-9', 2), ('implements', 'CA-R-123', 5)])
        for invalid in ('implements: [CA-R-123@0]', 'implements: [CA-R-123@2147483648]',
                        'implements: [CA-R-123@1, invalid]', 'implements: CA-R-123@1',
                        'implements: []\nimplements: []', 'unknown: []', '[]',
                        'implements: &pins [CA-R-123@1]\napplies: *pins'):
            canonical.write_text(invalid)
            stderr = StringIO()
            with redirect_stderr(stderr):
                store.refresh([canonical])
            self.assertIn('Invalid spec trace', stderr.getvalue())
            self.assertEqual(connection.execute(query).fetchall(), [])
        canonical.unlink()
        store.refresh([canonical])
        self.assertEqual(connection.execute(query).fetchall(), [('applies', 'CA-M-9', 1)])
        legacy.unlink()
        store.refresh([legacy])
        self.assertEqual(connection.execute(query).fetchall(), [])

    def test_incremental_trace_and_directory_changes(self):
        tmp_path = Path(self.enterContext(TemporaryDirectory()))
        pilot = tmp_path / PILOT
        package = pilot / 'FEATURE_WORKBENCH_BACKEND' / 'sub'
        package.mkdir(parents=True)
        module = package / 'unit.py'
        module.write_text('pass')
        (package / 'unit.py.spec_trace.md').write_text('## Implements\n- CA-R-123@4\n- CA-M-9@2\n')
        (package / 'sub.p.spec_trace.md').write_text('## Applies\n- CA-E-8@3\n')
        excluded = pilot / 'FEATURE_WORKBENCH_CODEX'
        excluded.mkdir()
        (excluded / 'ignored.py').write_text('pass')
        (tmp_path / (tmp_path.name + '.p.spec_trace.md')).write_text('## Applies\n- CA-R-999@1\n')
        conn = self.enterContext(duckdb.connect(':memory:'))
        store = SpecTraceStore(conn, tmp_path)
        store.initialize()
        store.refresh()
        rel = lambda p: p.relative_to(tmp_path).as_posix()
        assert conn.execute('SELECT atom_id, version FROM implementation_rmedo ORDER BY atom_id').fetchall() == [
            ('CA-E-8', 3), ('CA-M-9', 2), ('CA-R-123', 4)]
        assert conn.execute('SELECT path FROM implementation_objects WHERE path = ?', [rel(excluded)]).fetchall() == []
        assert conn.execute('SELECT container_path FROM implementation_objects WHERE path = ?', [rel(module)]).fetchone() == (rel(package),)
        assert conn.execute("SELECT kind, container_path FROM implementation_objects WHERE path = '.'").fetchone() == ('package', None)

        (package / 'unit.py.spec_trace.md').write_text('## Implements\n- CA-R-123@5\n')
        store.refresh([package / 'unit.py.spec_trace.md'])
        assert conn.execute('SELECT version FROM implementation_rmedo WHERE owner_path = ?', [rel(module)]).fetchall() == [(5,)]
        (package / 'unit.py.spec_trace.md').unlink()
        store.refresh([package / 'unit.py.spec_trace.md'])
        assert conn.execute('SELECT * FROM implementation_rmedo WHERE owner_path = ?', [rel(module)]).fetchall() == []
        assert conn.execute('SELECT kind FROM implementation_objects WHERE path = ?', [rel(module)]).fetchone() == ('module',)

        renamed = package.with_name('moved')
        package.rename(renamed)
        store.refresh([package, renamed])
        assert conn.execute('SELECT path FROM implementation_objects WHERE starts_with(path, ?)', [rel(package)]).fetchall() == []
        assert conn.execute('SELECT kind FROM implementation_objects WHERE path = ?', [rel(renamed / 'unit.py')]).fetchone() == ('module',)
        # A directory-named sidecar no longer owns the renamed directory.
        assert conn.execute('SELECT * FROM implementation_rmedo').fetchall() == []
