"""Allowed classification values retain the existing source facts."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(TOOL.parent))
sys.path.insert(0, str(TOOL.parents[1]))

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    CLASSIFICATION_PYTHON_BODY,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_enhanced_current_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import render_model


class AllowedClassificationValuesTests(unittest.TestCase):
    def test_native_claim_projects_allowed_axis_values(self):
        row = {'source': {'atom_id': 'CA-R-2484', 'version': 2, 'path': 'R2484.md', 'sha256': 'a'*64},
               'subjects': {'active': 'ANECHOIC_MODEL <+ Node >| Container', 'passive': []},
               'read_view': {'content_role': 'Requirement', 'type': 'Rule'}, 'body': CLASSIFICATION_PYTHON_BODY}
        new, new_errors = extract_claim_constraints(row)
        self.assertEqual(new_errors, [])
        self.assertEqual([(r['kind'], r.get('subject_selector'), r.get('axis'), r.get('value')) for r in new],
                         [('axis_allowed_value', 'Node', 'Container', 'yes'),
                          ('axis_allowed_value', 'Node', 'Container', 'no')])
        new_graph, provenance = compose_enhanced_current_graph([row])
        self.assertFalse(any(r.get('kind') == 'axis_condition' for r in new_graph['constraints']))
        self.assertEqual({r['value'] for r in new_graph['constraints'] if r['kind'] == 'axis_allowed_value'}, {'yes', 'no'})
        rendered = render_model(new_graph, provenance, updated_at='2026-11-13 00:00:00 +0000',
                                source_selection='Fixture', projection_identity={'projection_id': 'CA-PROJ-901', 'named_selection': 'Current'})
        self.assertIn('Node >| Container: yes', rendered)
        self.assertIn('Node >| Container: no', rendered)


if __name__ == '__main__':
    unittest.main()
