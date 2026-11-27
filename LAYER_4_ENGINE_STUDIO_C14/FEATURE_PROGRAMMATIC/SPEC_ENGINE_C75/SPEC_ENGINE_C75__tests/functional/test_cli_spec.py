import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import check_cli_spec
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import parse_cli_contract

_MANIFEST = """## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id='C2', name='Example', boundaries={'io': {'server': {'suite': {
        'transport': 'cli', 'runner': 'uv', 'path': 'suite.py'}}}}))
```
"""
_CONTRACT = """## Claim

### Formal Claim

```python cli
declare_cli_contract(interface='suite', action='run', runner='uv', path='suite.py',
                     outcomes={'succeeded': 'zero', 'failed': 'nonzero'})
```
"""
_SOLUTION = """## Claim

### Formal Claim

```python
component_workflow(component='C2', action='run', machine={
    'id': 'suite', 'initial': 'idle', 'states': {
        'idle': {'on': {'start': {'target': 'running', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'trigger', 'target': 'suite',
                       'detail': {'transport': 'cli', 'runner': 'uv', 'path': 'suite.py'}}}}}},
        'running': {'on': {
            'pass': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params':
                {'kind': 'output', 'outcome': 'succeeded', 'detail': {'exit_status_class': 'zero'}}}},
            'fail': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params':
                {'kind': 'output', 'outcome': 'failed', 'detail': {'exit_status_class': 'nonzero'}}}},
        }},
        'done': {'type': 'final'},
    }})
```
"""
_QUERY_CONTRACT = _CONTRACT.replace(
    "path='suite.py'", "module='engine.suite'"
).replace(
    "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
    """arguments=('--query', '<text>'), output_fields=('records', 'trace'),
    checks={'guarantees': {'priority': 'exact_name_first'},
            'effects': {'query_scope': 'supplied_frozen_context'},
            'output_format': {'record_properties': ('admission_status', 'source_bindings')}}""",
)
_QUERY_SOLUTION = """## Claim

### Formal Claim

```python
component_workflow(component='C2', action='run', machine={
    'id': 'suite', 'initial': 'idle', 'states': {
        'idle': {'on': {'start': {'target': 'running', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'trigger', 'target': 'suite', 'detail': {
                'transport': 'cli', 'runner': 'uv', 'module': 'engine.suite',
                'arguments': ['--query', '<text>']}}}}}},
        'running': {'on': {
            'search': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params': {
                'kind': 'effect', 'target': 'C2', 'outcome': 'succeeded',
                'detail': {'read_source': 'context_argument', 'rank_first': 'exact_name_match'}}}},
        }},
        'reporting': {'on': {
            'return': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {
                'kind': 'output', 'outcome': 'succeeded',
                'detail': {'record_properties': ['source_bindings', 'admission_status'],
                           'output_fields': ['trace', 'records']}}}},
        }},
        'done': {'type': 'final'},
    }})
```
"""


def _carrier(root, atom_id, template, owner, relations, body):
    path = root / f"{atom_id}.md"
    tier = {
        "component_manifest": 4,
        "component_contract": 0,
        "decision": 1,
        "solution": 0,
    }[template.casefold()]
    path.write_text(
        f"---\natom_family: SPEC\natom_id: {atom_id}\ncontainer: {{component: {owner}}}"
        f"\ntier: {tier}\ncontext: {{template: {template}}}\nrelations: {relations}"
        "\nstate: {status: active, version: 1}\n---\n\n" + body,
        encoding="utf-8",
    )
    return {
        "path": path.name,
        "atom_id": atom_id,
        "version": 1,
        "status": "active",
        "container_component": owner,
    }


class CliSpecTests(unittest.TestCase):
    def test_cli_chain_and_mutations(self):
        if shutil.which('lean') is None:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', _MANIFEST),
                _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}', _CONTRACT),
                _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}', _SOLUTION),
            )
            report = check_cli_spec(root, 'C2', *pins, interface='suite')
            self.assertEqual(
                {'manifest_contract': 'matched', 'manifest_solution': 'matched',
                 'contract_solution': 'matched'},
                {name: row['status'] for name, row in report['directions'].items()})
            self.assertIn('state "running" as S1', report['mermaid'])
            self.assertIn('S1 --> S2 : pass', report['mermaid'])
            solution = root / pins[2]['path']
            original = solution.read_text(encoding='utf-8')
            for old, new, outcome in (
                ("'exit_status_class': 'zero'", "'exit_status_class': 'nonzero'", 'conflicting'),
                (", 'detail': {'exit_status_class': 'nonzero'}", '', 'unresolved'),
            ):
                with self.subTest(outcome=outcome):
                    solution.write_text(original.replace(old, new, 1), encoding='utf-8')
                    direction = check_cli_spec(root, 'C2', *pins, interface='suite')[
                        'directions']['contract_solution']
                    self.assertEqual(outcome, direction['status'])

    def test_cli_contract_rejects_nonliteral_or_ambiguous_outcomes(self):
        declaration = ("declare_cli_contract(interface='test_suite', action='run', "
                       "runner='uv', path='suite.py', outcomes=%s)")
        for outcomes in ("{'ok': True}", "{'ok': 1}", "{'ok': 'zero', 'ok': 'nonzero'}",
                         "{'ok': get_status()}"):
            with self.subTest(outcomes=outcomes), self.assertRaises(ValueError):
                parse_cli_contract(declaration % outcomes)

    def test_cli_exit_codes_distinguish_nonzero_values(self):
        if shutil.which("lean") is None:
            self.skipTest("Lean executable unavailable")
        contract = _CONTRACT.replace(
            "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
            "exit_codes={'succeeded': 0, 'failed': 1}",
        )
        solution = _SOLUTION.replace(
            "'exit_status_class': 'zero'", "'exit_code': 0"
        ).replace("'exit_status_class': 'nonzero'", "'exit_code': 1")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', _MANIFEST),
                _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}', contract),
                _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}', solution),
            )
            self.assertEqual(
                "matched",
                check_cli_spec(root, "C2", *pins, interface="suite")[
                    "directions"
                ]["contract_solution"]["status"],
            )
            path = root / pins[2]["path"]
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "'exit_code': 1", "'exit_code': 130"
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                "conflicting",
                check_cli_spec(root, "C2", *pins, interface="suite")[
                    "directions"
                ]["contract_solution"]["status"],
            )

    def test_cli_contract_rejects_invalid_exit_codes(self):
        declaration = ("declare_cli_contract(interface='suite', action='run', runner='uv', "
                       "path='suite.py', exit_codes={'failed': %s})")
        for code in ('True', '-1', '256', "'1'"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                parse_cli_contract(declaration % code)

    def test_cli_required_effect_blocks_a_terminal_bypass(self):
        if shutil.which('lean') is None:
            self.skipTest('Lean executable unavailable')
        manifest = _MANIFEST.replace("'path': 'suite.py'", "'module': 'engine.suite'")
        contract = _CONTRACT.replace("path='suite.py'", "module='engine.suite'").replace(
            "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
            "output='succeeded', must_effect=(('C2', 'succeeded'),)",
        )
        bypass = """'running': {'on': {
            'bypass': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(
                    root, "AN-S-1", "component_manifest", "C1", "{}", manifest
                ),
                _carrier(
                    root,
                    "AN-S-2",
                    "component_contract",
                    "C2",
                    "{ANSWERS: [AN-S-1]}",
                    contract,
                ),
                _carrier(
                    root,
                    "AN-S-3",
                    "decision",
                    "C2",
                    "{IS_SOLUTION_FOR: [AN-S-2@1]}",
                    _QUERY_SOLUTION,
                ),
            )
            path = root / pins[2]['path']
            initial = path.read_text(encoding='utf-8')
            for body, expected in ((initial, 'matched'),
                                   (initial.replace("'running': {'on': {", bypass, 1), 'conflicting')):
                with self.subTest(expected=expected):
                    path.write_text(body, encoding='utf-8')
                    report = check_cli_spec(root, 'C2', *pins, interface='suite')
                    direction = report['directions']['contract_solution']
                    self.assertEqual(expected, direction['status'])
                    effect = next(row for row in direction['facts'] if row['key'] == 'must_effect')
                    self.assertEqual(expected, effect['status'])

    def test_cli_contract_requires_one_entry_point(self):
        declaration = (
            "declare_cli_contract(interface='suite', action='run', runner='uv'"
        )
        self.assertEqual(
            "engine.suite",
            parse_cli_contract(declaration + ", module='engine.suite')")[
                "module"
            ],
        )
        for entry in ("", ", path='suite.py', module='engine.suite'"):
            with (
                self.subTest(entry=entry),
                self.assertRaisesRegex(ValueError, "exactly one"),
            ):
                parse_cli_contract(declaration + entry + ")")

    def test_cli_subcommands_require_the_declared_first_dispatch(self):
        if shutil.which('lean') is None:
            self.skipTest('Lean executable unavailable')
        manifest = _MANIFEST.replace("'path': 'suite.py'", "'path': 'suite.py', 'subcommands': {'local': 'C2'}")
        contract = _CONTRACT.replace("outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
                                     "subcommands={'local': 'C2'}")
        route = """'running': {'on': {'select': {'target': 'invoking', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'trigger', 'detail': {'command': 'local'}}}}}},
        'invoking': {'on': {'dispatch': {'target': 'reporting', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'effect', 'target': 'C2'}}}}},
        'reporting': {'on': {"""
        solution = _SOLUTION.replace("'running': {'on': {", route)
        bypass = """'invoking': {'on': {'skip': {'target': 'done',
            'guard': {'type': 'matchesTrace', 'params': {'kind': 'output'}}},"""
        generic = """'running': {'on': {'generic': {'target': 'done',
            'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}, 'select':"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', manifest),
                _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}', contract),
                _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}', solution),
            )
            path = root / pins[2]['path']
            original = path.read_text(encoding='utf-8')
            for body, verdict in (
                (original, 'matched'),
                (original.replace("'kind': 'effect', 'target': 'C2'", "'kind': 'effect', 'target': 'C3'"), 'conflicting'),
                (original.replace("'invoking': {'on': {", bypass), 'conflicting'),
                (original.replace("'running': {'on': {'select':", generic), 'conflicting'),
            ):
                path.write_text(body, encoding='utf-8')
                report = check_cli_spec(root, 'C2', *pins, interface='suite')
                direction = report['directions']['contract_solution']
                self.assertEqual(verdict, direction['status'])

    def test_query_checks_require_the_ranked_read_on_every_success_path(self):
        if shutil.which('lean') is None:
            self.skipTest('Lean executable unavailable')
        manifest = _MANIFEST.replace("'path': 'suite.py'", "'module': 'engine.suite', "
                                     "'arguments': ['--query', '<text>'], 'output_fields': ['records', 'trace']")
        bypass = """'running': {'on': {
            'skip': {'target': 'reporting', 'guard': {'type': 'matchesTrace',
                'params': {'kind': 'trigger'}}},"""
        initial_bypass = """'idle': {'on': {'skip_request': {'target': 'running',
            'guard': {'type': 'matchesTrace', 'params': {'kind': 'output'}}},"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', manifest),
                _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}', _QUERY_CONTRACT),
                _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}', _QUERY_SOLUTION),
            )
            report = check_cli_spec(root, 'C2', *pins, interface='suite')
            self.assertTrue(all(item['status'] == 'matched' for item in report['directions'].values()))
            solution = root / pins[2]['path']
            original = solution.read_text(encoding='utf-8')
            for old, new, key, verdict in (
                ('exact_name_match', 'body_match', 'guarantees.priority', 'conflicting'),
                ("['trace', 'records']", "['records']", 'output_fields', 'conflicting'),
                ("'running': {'on': {", bypass, 'guarantees.priority', 'unresolved'),
                ("'idle': {'on': {", initial_bypass, 'interface', 'unresolved'),
            ):
                with self.subTest(verdict=verdict):
                    solution.write_text(original.replace(old, new, 1), encoding='utf-8')
                    report = check_cli_spec(root, 'C2', *pins, interface='suite')
                    facts = report['directions']['contract_solution']['facts']
                    fact = next(row for row in facts if row['key'] == key)
                    self.assertEqual(verdict, fact['status'])
