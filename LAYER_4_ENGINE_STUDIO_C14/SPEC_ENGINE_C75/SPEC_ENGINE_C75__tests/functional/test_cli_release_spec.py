import shutil
import tempfile
import unittest
from itertools import pairwise
from pathlib import Path

from SPEC_ENGINE_C75.cli_spec__pub import check_cli_spec
from test_cli_spec import _CONTRACT, _MANIFEST, _carrier


def _release_workflow(*, bypass=None, refs=('candidate', 'candidate', 'candidate'),
                      early=None, outcome='completed', build_owner='C81'):
    def edge(destination, **params):
        return {'target': destination, 'guard': {'type': 'matchesTrace', 'params': params}}

    stages = ('static', 'functional', 'build', 'verify_image', 'install', 'report')
    states = {}
    for stage, target in pairwise(stages):
        detail = {'release_stage': stage}
        if stage in ('build', 'verify_image', 'install'):
            ref = refs[('build', 'verify_image', 'install').index(stage)]
            if ref is not None:
                detail['image_ref'] = ref
        owner = {'target': build_owner} if stage == 'build' else {}
        states[stage] = {'on': {'passed': edge(target, kind='effect', outcome='passed', detail=detail, **owner)}}
    states['idle'] = {'on': {'request': edge('static', kind='trigger', target='suite',
                                          detail={'transport': 'cli', 'runner': 'uv',
                                                  'path': 'suite.py', 'command': 'local'})}}
    states['report'] = {'on': {'complete': edge('done', kind='output', outcome=outcome)}}
    states['done'] = {'type': 'final'}
    if early:
        states['static']['on']['early'] = edge(
            'done', kind='output', **({} if early == 'wildcard' else {'outcome': early}))
    if bypass:
        source, target = bypass
        states[source]['on']['skip'] = edge(target, kind='effect')
    machine = {'id': 'release', 'initial': 'idle', 'states': states}
    return (f'## Claim\n\n### Formal Claim\n\n```python\n'
            f"component_workflow(component='C2', action='run', machine={machine!r})\n```\n")



class CliReleaseSpecTests(unittest.TestCase):
    def test_release_order_requires_passing_stages_and_exact_candidate(self):
        if shutil.which('lean') is None:
            self.skipTest('Lean executable unavailable')
        manifest = _MANIFEST.replace("'path': 'suite.py'", "'path': 'suite.py', 'command': 'local'")
        contract = _CONTRACT.replace(
            "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
            """command='local', checks={'guarantees': {
                'host_checks_before_build':'static_then_functional',
                'image_checks_before_install':'exact_candidate', 'build_owner':'C81'}}""",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', manifest),
                _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}', contract),
                _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}', _release_workflow()),
            )
            report = check_cli_spec(root, 'C2', *pins, interface='suite')
            self.assertTrue(all(item['status'] == 'matched' for item in report['directions'].values()))
            header = (solution := root / pins[2]['path']).read_text(encoding='utf-8').split('## Claim', 1)[0]
            for mutation, key in (
                ({'bypass': ('static', 'build')}, 'host_checks_before_build'),
                ({'bypass': ('verify_image', 'install')}, 'image_checks_before_install'),
                ({'refs': ('candidate', 'other', 'candidate')}, 'image_checks_before_install'),
                ({'refs': ('candidate', 'candidate', 'other')}, 'image_checks_before_install'),
                ({'early': 'completed_with_cleanup_pending'}, 'image_checks_before_install'),
                ({'early': 'completed'}, 'image_checks_before_install'),
                ({'early': 'wildcard'}, 'image_checks_before_install'),
                ({'build_owner': 'C63'}, 'build_owner'),
            ):
                with self.subTest(mutation=mutation):
                    solution.write_text(header + _release_workflow(**mutation), encoding='utf-8')
                    report = check_cli_spec(root, 'C2', *pins, interface='suite')
                    facts = {row['key']: row['status'] for row in report['directions']['contract_solution']['facts']}
                    self.assertEqual('conflicting', facts[f'guarantees.{key}'])

            for mutation in ({'refs': (None, 'candidate', 'candidate')},
                             {'refs': ('candidate', None, 'candidate')},
                             {'refs': ('candidate', 'candidate', None)},
                             {'refs': ('', 'candidate', 'candidate')}, {'outcome': 'failed'}):
                with self.subTest(mutation=mutation):
                    solution.write_text(header + _release_workflow(**mutation), encoding='utf-8')
                    report = check_cli_spec(root, 'C2', *pins, interface='suite')
                    facts = report['directions']['contract_solution']['facts']
                    fact = next(row for row in facts if row['key'] == 'guarantees.image_checks_before_install')
                    self.assertEqual('unresolved', fact['status'])
