"""Replay the pinned selection functions with bounded collaborators."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest

HERE = Path(__file__).parent


class ProjectSelectionError(Exception):
    pass


class Reader:
    fingerprints = {'/project/.anechoic_demo/manifest': 'digest'}

    def __init__(self, **kwargs):
        pass

    def currentness(self):
        return {'state': 'unchanged'}


def select(version, state):
    carrier = SimpleNamespace(metadata={'state': state})
    path = Path('/project/.anechoic_demo/manifest')
    seen = []
    def validate(fields, component):
        seen.append(fields.copy())
        return SimpleNamespace(name='Demo', prefix='AN', parameters={})
    env = {'Path': Path, 'datetime': datetime, 'deepcopy': deepcopy,
           'ProjectSelectionError': ProjectSelectionError, 'ReadContext': Reader,
           'CEILINGS': {}, '_project_root': lambda root: Path(root),
           '_manifest_carriers': lambda reader, control: iter([(path, carrier)]),
           '_manifest_inputs': lambda path, carrier: ({'atom_id': 'AN-S-1', 'ref_id': 'AN-S-1@1'}, 'C00'),
           '_instance_id': lambda root, relative: 'id',
           'NativeProjectSelection': lambda *args: args}
    source = (HERE / f'{version}.py.txt').read_text()
    exec(compile('from __future__ import annotations\n' + source, str(path), 'exec'), env)
    options = {'require_atom_state': True} if version == 'fixed' else {}
    try:
        env['resolve_native_project']('/project', '.anechoic_demo', validate_manifest=validate, **options)
    except ProjectSelectionError:
        return False, seen
    return True, seen


class Replay(unittest.TestCase):
    def test_missing_and_valid_state(self):
        before, fields = select('before', {'status': 'active'})
        self.assertTrue(before)
        self.assertNotIn('updated_at', fields[0])
        fixed, fields = select('fixed', {'status': 'active'})
        self.assertFalse(fixed)
        self.assertEqual(fields, [])
        fixed, fields = select('fixed', {'status': 'active', 'updated_at': 'invalid'})
        self.assertFalse(fixed)
        self.assertEqual(fields, [])
        fixed, fields = select('fixed', {'status': 'active', 'updated_at': '2026-11-19T00:00:00Z'})
        self.assertTrue(fixed)
        self.assertEqual(fields[0]['updated_at'], datetime.fromisoformat('2026-11-19T00:00:00Z'))
        self.assertEqual(fields[0]['status'], 'active')


if __name__ == '__main__':
    unittest.main()
