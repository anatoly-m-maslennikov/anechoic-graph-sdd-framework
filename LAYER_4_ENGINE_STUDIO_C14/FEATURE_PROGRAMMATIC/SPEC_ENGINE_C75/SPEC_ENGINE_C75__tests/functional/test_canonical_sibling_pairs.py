import os
import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_1_SOURCE_ADAPTERS_C95._package__shared import SourceError
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.DELEGATION_VERIFICATION_C89._package__shared import (
    check_sibling_binding,
    check_sibling_outcome,
)


ROOT = Path(__file__).parent / 'assets' / 'canonical_siblings'


def pin(number, component):
    return {'path': f'AN-S-{number}.md', 'atom_id': f'AN-S-{number}',
            'version': 1, 'status': 'active', 'container_component': component}


class CanonicalSiblingPairsTests(unittest.TestCase):
    def test_both_sibling_checks_accept_exact_pairs(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        caller = (pin(1, 'C1'), pin(2, 'C2'))
        provider = (pin(3, 'C1'), pin(4, 'C3'))
        for check in (check_sibling_binding, check_sibling_outcome):
            with self.subTest(check=check.__name__):
                result = check(
                    ROOT,
                    caller,
                    "C3",
                    provider,
                    event="invoke",
                    interface="worker",
                    lean=lean,
                )
                self.assertEqual("matched", result["status"])
                self.assertEqual(
                    "AN-S-3", result["sources"]["manifest"]["atom_id"]
                )
                self.assertEqual(
                    "AN-S-3", result["sources"]["contract"]["atom_id"]
                )
                self.assertEqual(
                    "AN-S-4", result["sources"]["solution"]["atom_id"]
                )
                self.assertEqual(
                    {"caller_manifest", "caller_contract", "caller_solution"},
                    set(result["directions"]),
                )

    def test_wrong_manifest_reference_conflicts(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob('*.md'):
                shutil.copy(source, root / source.name)
            source = root / 'AN-S-2.md'
            source.write_text(source.read_text().replace('AN-S-3@1', 'AN-S-9@1'))
            for check in (check_sibling_binding, check_sibling_outcome):
                with self.subTest(check=check.__name__):
                    result = check(root, (pin(1, 'C1'), pin(2, 'C2')), 'C3',
                                   (pin(3, 'C1'), pin(4, 'C3')), event='invoke',
                                   interface='worker', lean=lean)
                    self.assertEqual('conflicting', result['status'])

    def test_caller_solution_pin_is_validated(self):
        caller = (pin(1, 'C1'), {**pin(2, 'C2'), 'version': 2})
        for check in (check_sibling_binding, check_sibling_outcome):
            with self.subTest(check=check.__name__), self.assertRaises(SourceError):
                check(ROOT, caller, 'C3', (pin(3, 'C1'), pin(4, 'C3')),
                      event='invoke', interface='worker')

    def test_private_entry_is_checked_against_boundary_and_solution(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob('*.md'):
                shutil.copy(source, root / source.name)
            for name in ('AN-S-3.md', 'AN-S-4.md'):
                with self.subTest(source=name):
                    source = root / name
                    original = source.read_text()
                    source.write_text(original.replace('worker.run', 'worker.other'))
                    result = check_sibling_binding(
                        root, (pin(1, 'C1'), pin(2, 'C2')), 'C3',
                        (pin(3, 'C1'), pin(4, 'C3')), event='invoke',
                        interface='worker', lean=lean)
                    self.assertEqual('conflicting', result['status'])
                    source.write_text(original)

    def test_outcome_checks_explicit_entry_and_transport(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob('*.md'):
                shutil.copy(source, root / source.name)
            for name, original, changed in (
                    ('AN-S-2.md', 'worker.run', 'worker.other'),
                    ('AN-S-3.md', "'transport': 'in_process'", "'transport': 'http'"),
                    ('AN-S-4.md', 'worker.run', 'worker.other')):
                with self.subTest(source=name):
                    source = root / name
                    body = source.read_text()
                    source.write_text(body.replace(original, changed))
                    result = check_sibling_outcome(
                        root, (pin(1, 'C1'), pin(2, 'C2')), 'C3',
                        (pin(3, 'C1'), pin(4, 'C3')), event='invoke',
                        interface='worker', lean=lean)
                    self.assertEqual('conflicting', result['status'], result)
                    source.write_text(body)

    def test_entry_without_transport_is_checked(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob('*.md'):
                shutil.copy(source, root / source.name)
            source = root / "AN-S-2.md"
            source.write_text(
                source.read_text().replace(
                    "'transport': 'in_process', 'entry': 'worker.run'",
                    "'entry': 'worker.other'",
                )
            )
            result = check_sibling_outcome(
                root,
                (pin(1, "C1"), pin(2, "C2")),
                "C3",
                (pin(3, "C1"), pin(4, "C3")),
                event="invoke",
                interface="worker",
                lean=lean,
            )
            self.assertEqual("conflicting", result["status"], result)

    def test_embedded_outcome_needs_association_with_interface(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob('*.md'):
                shutil.copy(source, root / source.name)
            source = root / 'AN-S-3.md'
            source.write_text(source.read_text().replace(
                "'worker': {'transport': 'in_process', 'entry': 'worker.run'}", "'unrelated': {}").replace(
                ", interface='worker', transport='in_process'", ''))
            source = root / 'AN-S-4.md'
            source.write_text(source.read_text().replace(
                ", 'target': 'worker', 'detail': {'transport': 'in_process', 'entry': 'worker.run'}", ''))
            for name in ('AN-S-1.md', 'AN-S-2.md'):
                source = root / name
                source.write_text(
                    source.read_text()
                    .replace("worker", "unrelated")
                    .replace(
                        "'transport': 'in_process', 'entry': 'unrelated.run', ",
                        "",
                    )
                )
            result = check_sibling_outcome(
                root,
                (pin(1, "C1"), pin(2, "C2")),
                "C3",
                (pin(3, "C1"), pin(4, "C3")),
                event="invoke",
                interface="unrelated",
                lean=lean,
            )
            self.assertEqual("unresolved", result["status"], result)
            self.assertTrue(
                all(
                    row["status"] == "unresolved"
                    for row in result["directions"].values()
                ),
                result,
            )

    def test_http_outcome_checks_provider_route_and_client_declaration(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                body = source.read_text().replace(
                    "'transport': 'in_process', 'entry': 'worker.run'",
                    "'transport': 'http', 'route': 'POST /work'",
                )
                if source.name == "AN-S-1.md":
                    body = body.replace(
                        "'transport': 'in_process'",
                        "'transport': 'http', 'routes': ['POST /work']",
                    )
                if source.name == "AN-S-3.md":
                    body = body.replace(
                        "'transport': 'http', 'route': 'POST /work'",
                        "'transport': 'http', 'routes': ['POST /work']",
                    )
                    body = body.replace(
                        ", interface='worker', transport='in_process'", ""
                    )
                (root / source.name).write_text(body)
            def check():
                return check_sibling_outcome(root, (pin(1, 'C1'), pin(2, 'C2')), 'C3',
                                             (pin(3, 'C1'), pin(4, 'C3')), event='invoke',
                                             interface='worker', lean=lean)
            result = check()
            self.assertEqual('matched', result['status'], result)
            source = root / 'AN-S-4.md'
            body = source.read_text()
            source.write_text(body.replace('POST /work', 'POST /other'))
            self.assertEqual('conflicting', check()['status'])
            source.write_text(body)
            source = root / 'AN-S-1.md'
            source.write_text(source.read_text().replace('POST /work', 'POST /other'))
            with self.assertRaisesRegex(ValueError, 'does not declare client'):
                check()

    def test_explicit_outcome_transport_requires_a_matching_client(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob('*.md'):
                shutil.copy(source, root / source.name)
            for name in ('AN-S-1.md', 'AN-S-2.md'):
                with self.subTest(source=name):
                    source = root / name
                    body = source.read_text()
                    source.write_text(
                        body.replace(
                            "'transport': 'in_process'", "'transport': 'http'"
                        )
                    )
                    with self.assertRaisesRegex(
                        ValueError, "does not declare client"
                    ):
                        check_sibling_outcome(
                            root,
                            (pin(1, "C1"), pin(2, "C2")),
                            "C3",
                            (pin(3, "C1"), pin(4, "C3")),
                            event="invoke",
                            interface="worker",
                        )
                    source.write_text(body)

    def test_mixed_framing_order_does_not_change_sibling_checks(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        framing = {
            'AN-S-3.md': "declare_framing_contract(delimiter=[35], line_endings=[[10], [13, 10]])",
            'AN-S-4.md': "declare_framing_solution(opening_prefixes=[[35, 10], [35, 13, 10]], "
                         "closing_prefixes=[[10, 35, 10], [10, 35, 13, 10], "
                         "[13, 10, 35, 10], [13, 10, 35, 13, 10]])",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob('*.md'):
                shutil.copy(source, root / source.name)
            for first in (True, False):
                for name, claim in framing.items():
                    source = root / name
                    body = (ROOT / name).read_text()
                    fence = f'```python framing\n{claim}\n```\n'
                    if first:
                        position = body.rfind('```python')
                        body = body[:position] + fence + body[position:]
                    else:
                        body += '\n' + fence
                    source.write_text(body)
                for check in (check_sibling_binding, check_sibling_outcome):
                    with self.subTest(first=first, check=check.__name__):
                        kwargs = {'action': 'run'} if check is check_sibling_binding else {}
                        result = check(root, (pin(1, 'C1'), pin(2, 'C2')), 'C3',
                                       (pin(3, 'C1'), pin(4, 'C3')), event='invoke',
                                       interface='worker', lean=lean, **kwargs)
                        self.assertEqual('matched', result['status'], result)

    def test_public_interface_mismatch_conflicts(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob('*.md'):
                shutil.copy(source, root / source.name)
            source = root / 'AN-S-3.md'
            source.write_text(source.read_text().replace(
                "interface='worker', transport='in_process'",
                "interface='other', transport='in_process'"))
            result = check_sibling_binding(
                root,
                (pin(1, "C1"), pin(2, "C2")),
                "C3",
                (pin(3, "C1"), pin(4, "C3")),
                event="invoke",
                interface="worker",
                lean=lean,
            )
            self.assertEqual(
                "conflicting",
                result["directions"]["caller_contract"]["status"],
            )
