"""Allowed classification values retain the existing source facts."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parents[1]), str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    CLASSIFICATION_CFEL_BODY, CLASSIFICATION_PYTHON_BODY,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_enhanced_current_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import render_model


class AllowedClassificationValuesTests(unittest.TestCase):
    def test_allowed_values_match_across_claim_languages(self):
        old_body, new_body = CLASSIFICATION_CFEL_BODY, CLASSIFICATION_PYTHON_BODY
        self.assertNotEqual(new_body, old_body)
        row = {'source': {'atom_id': 'CA-R-2484', 'version': 2, 'path': 'R2484.md', 'sha256': 'a'*64},
               'subjects': {'active': 'ANECHOIC_MODEL <+ Node >| Container', 'passive': []},
               'read_view': {'content_role': 'Requirement', 'type': 'Rule'}, 'body': old_body}
        changed = deepcopy(row)
        changed['body'] = new_body
        old, old_errors = extract_claim_constraints(row)
        new, new_errors = extract_claim_constraints(changed)
        self.assertEqual(old_errors, [])
        self.assertEqual(new_errors, [])
        self.assertEqual([(r['kind'], r.get('subject_selector'), r.get('axis'), r.get('value')) for r in new],
                         [('classification_allowed_value', 'Node', 'Container', 'yes'),
                          ('classification_allowed_value', 'Node', 'Container', 'no')])
        self.assertEqual(old, new)
        old_graph, _ = compose_enhanced_current_graph([row])
        new_graph, _ = compose_enhanced_current_graph([changed])
        self.assertEqual(old_graph["nodes"], new_graph["nodes"])
        self.assertEqual(old_graph["edges"], new_graph["edges"])
        self.assertFalse(any(r.get('kind') == 'classification_condition' for r in new_graph['constraints']))
        self.assertEqual({r['value'] for r in new_graph['constraints'] if r['kind'] == 'classification_allowed_value'}, {'yes', 'no'})
        graph, provenance = compose_enhanced_current_graph([changed])
        rendered = render_model(graph, provenance, updated_at='2026-11-13 00:00:00 +0000',
                                source_selection='Fixture', projection_identity={'projection_id': 'CA-PROJ-901', 'named_selection': 'Current'})
        self.assertIn('Node >| Container: yes', rendered)
        self.assertIn('Node >| Container: no', rendered)


if __name__ == '__main__':
    unittest.main()
