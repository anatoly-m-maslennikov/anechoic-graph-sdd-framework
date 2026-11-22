"""Native Relation derivation remains source-bound projection metadata."""
from pathlib import Path
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[2]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_model_claim__pub import NativeModelClaimError, parse_native_model_claim


def claim(name, base=None):
    derivation = f', derived_from={base!r}' if base is not None else ''
    return ('from anechoic.formal_claims import declare_relation\n'
            f'declare_relation(relation_name={name!r}, source_endpoint={{"level": "instances"}}, '
            f'target_endpoint={{"level": "instances"}}{derivation})\n')


class NativeRelationDerivationTests(unittest.TestCase):
    def test_invalid_derived_from_rejected(self):
        for value in ('', 'bad name', 'Relation//OTHER', 'SELF', 1, None):
            code = claim('SELF').replace('target_endpoint={"level": "instances"}',
                                         f'target_endpoint={{"level": "instances"}}, derived_from={value!r}')
            with self.subTest(value=value), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(code)


if __name__ == '__main__':
    unittest.main()
