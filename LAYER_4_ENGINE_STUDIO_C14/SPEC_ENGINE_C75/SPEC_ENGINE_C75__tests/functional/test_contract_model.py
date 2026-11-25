import unittest

from SPEC_ENGINE_C75.contract_model__pub import lean_string, parse_contract


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
