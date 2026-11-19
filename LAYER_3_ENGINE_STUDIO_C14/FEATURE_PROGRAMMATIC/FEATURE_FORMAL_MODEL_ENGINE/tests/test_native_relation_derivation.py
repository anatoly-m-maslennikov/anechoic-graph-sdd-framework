"""Native Relation derivation remains source-bound projection metadata."""
from pathlib import Path
import sys
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PROGRAMMATIC), str(PROGRAMMATIC / 'FEATURE_TOOLS'),
                str(PROGRAMMATIC / 'FEATURE_TOOLS/GENERATE_ENTITY_GRAPH'),
                str(PROGRAMMATIC / 'FEATURE_APPS/APP_WORKBENCH')]

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import NativeModelClaimError, parse_native_model_claim
from FEATURE_WORKBENCH_BACKEND.relation_declarations import relation_declaration
from cfel_claim_constraints import extract_claim_constraints
from contract_graph import compose_contract_graph
from subject_projection_data import _relation_declarations


def claim(name, base=None):
    derivation = f', derived_from={base!r}' if base is not None else ''
    return ('from anechoic.formal_claims import declare_relation\n'
            f'declare_relation(relation_name={name!r}, source_endpoint={{"level": "instances"}}, '
            f'target_endpoint={{"level": "instances"}}{derivation})\n')


def body(code):
    return f'## Claim\n\n### Formal Claim\n\n```python\n{code}```\n'


class NativeRelationDerivationTests(unittest.TestCase):
    def test_source_bound_projection_and_registry(self):
        for name, base in (('IS_DECLARED_BY', 'GOVERNS'), ('RECURSIVELY_CONTAINS', 'CONTAINS')):
            with self.subTest(name=name):
                code = claim(name, base)
                carrier = {'source': {'atom_id': 'CA-R-1', 'version': 1, 'path': 'source.md'},
                           'subjects': {'active': f'ANECHOIC_MODEL <+ Relation//{name}', 'passive': []},
                           'read_view': {'content_role': 'Requirement', 'type': 'Declaration'}, 'body': body(code)}
                clauses, errors = extract_claim_constraints(carrier)
                self.assertEqual([], errors)
                link, = [row for row in clauses if row.get('relation') == 'IS_DERIVED_RELATION_OF']
                self.assertEqual((f'Relation//{name}', f'Relation//{base}', carrier['source']),
                                 (link['source_selector'], link['target_selector'], link['source']))
                relation, = compose_contract_graph([carrier])['relations']
                self.assertEqual([base], [row['name'] for row in relation['derivation_links']])
                projected, = _relation_declarations([relation])
                self.assertEqual((name, 'Derived'), (projected['name'], projected['derivation']))
                self.assertEqual(relation_declaration(body(code), 'source'),
                                 relation_declaration(body(claim(name)), 'source'))

    def test_invalid_derived_from_rejected(self):
        for value in ('', 'bad name', 'Relation//OTHER', 'SELF', 1, None):
            code = claim('SELF').replace('target_endpoint={"level": "instances"}',
                                         f'target_endpoint={{"level": "instances"}}, derived_from={value!r}')
            with self.subTest(value=value), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(code)


if __name__ == '__main__':
    unittest.main()
