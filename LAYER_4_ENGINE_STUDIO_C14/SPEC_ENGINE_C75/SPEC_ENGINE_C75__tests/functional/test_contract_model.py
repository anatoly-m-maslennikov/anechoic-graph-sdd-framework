import unittest

from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.lean_values__pub import lean_string
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.contract_model__pub import parse_cli_contract, parse_contract, parse_trace_contract


CLAIM = '''declare_contract(operation='POST /tools', outcomes={
    'success': (200, 'result'), 'invalid_input': (400, 'typed_error'),
    'internal_error': (500, 'typed_error')},
    checks={'input_format': {'fields': ('z', 'a')}, 'interface': {'protocol': 'http'}})'''


class ContractModelTests(unittest.TestCase):
    def test_normalized_traceable_facts(self):
        self.assertEqual(parse_contract(CLAIM), {'operation': 'POST /tools', 'outcomes': [
            ('success', 200, 'result'), ('invalid_input', 400, 'typed_error'),
            ('internal_error', 500, 'typed_error')], 'facts': [
            ('input_format.fields', ['a', 'z']), ('interface.protocol', ['http'])]})
        self.assertEqual(lean_string('a\nb'),
                         'String.ofList [Char.ofNat 97, Char.ofNat 10, Char.ofNat 98]')

    def test_unsupported_claims_are_rejected(self):
        for source in (CLAIM.replace('POST /tools', 'GET /tools'),
                       CLAIM.replace("('z', 'a')", "('a', 'a')"),
                       CLAIM + '\nprint("executed")'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_contract(source)

    def test_check_literals_require_values(self):
        prefix = "declare_cli_contract(interface='i', action='a', runner='uv', path='p', checks="
        for value in ("''", "' '", "()", "('',)", "('valid', ' ')"):
            checks = "{'guarantees': {'example': " + value + "}})"
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'empty check value'):
                parse_cli_contract(prefix + checks)

    def test_required_effect_detail_is_literal_and_typed(self):
        prefix = "declare_trace_contract(action='check', output='ready', must_effect=(('api', 'returned', "
        detail = "{'sql': 'current', 'read_only': True, 'count': 1, 'error': None}"
        self.assertEqual(parse_trace_contract(prefix + detail + "),))")['must_effect'],
                         [('api', 'returned', {'sql': 'current', 'read_only': True, 'count': 1, 'error': None})])
        for detail in ("{}", "{'': 'current'}", "{'sql': ('current',)}", "{'sql': 'old', 'sql': 'current'}",
                       "{'rows': {'at_most': True}}", "{'rows': {'at_most': -1}}",
                       "{'rows': {'at_most': 1, 'other': 2}}", "{'rows': {'at_most': 1, 'at_most': 2}}"):
            with self.subTest(detail=detail), self.assertRaises(ValueError):
                parse_trace_contract(prefix + detail + "),))")
        self.assertEqual({'rows': {'at_most': 45}},
                         parse_trace_contract(prefix + "{'rows': {'at_most': 45}}),))")['must_effect'][0][2])
