import unittest

from ..continuant_concern__pub import continuant_model_subject


class ContinuantConcernTests(unittest.TestCase):
    def test_canonical_relations_and_model_root(self):
        for concern, expected in (
            ({'subject': 'Model', 'path': 'ANECHOIC', 'relation': 'is_contained_by'}, 'Model'),
            ({'subject': 'Graph', 'path': 'Model', 'relation': 'is_contained_by'}, 'Graph'),
            ({'subject': 'Node', 'path': 'Model/Graph', 'relation': 'is_contained_by'}, 'Graph/Node'),
            ({'subject': 'Atom', 'path': 'Model/Graph/Node', 'relation': 'is_narrower_than'}, 'Graph/Node//Atom'),
            ({'subject': 'Name', 'path': 'Model/Graph/Node', 'relation': 'is_property_of'}, 'Graph/Node.Name'),
            ({'subject': 'Artifact Kind', 'path': 'Model/Graph/Axis', 'relation': 'has_axis'}, 'Graph/Axis >| Artifact Kind'),
            ({'subject': 'Artifact Kind', 'path': 'Model/Graph/Classification', 'relation': 'classifies'}, 'Graph/Classification >| Artifact Kind'),
        ):
            with self.subTest(concern=concern):
                self.assertEqual(continuant_model_subject(concern), 'MODEL//ANECHOIC <+ ' + expected)

    def test_rejects_incomplete_and_noncanonical_locators(self):
        for concern in (None, {}, {'subject': 'A', 'path': 'Model', 'relation': 'is_narrower_than'},
                        {'subject': 'A/B', 'path': 'Model/Graph', 'relation': 'is_contained_by'},
                        {'subject': 'A', 'path': 'Model/Graph >| B', 'relation': 'is_contained_by'},
                        {'subject': 'A', 'path': 'Model/Graph', 'relation': 'unknown'},
                        {'subject': 'A', 'path': 'Model/Graph', 'relation': 'classifies', 'extra': 'x'}):
            with self.subTest(concern=concern), self.assertRaises(ValueError):
                continuant_model_subject(concern)

    def test_split_variant_concern(self):
        concern = {'path': 'Model/Graph/Node//Atom//Ticket//.Header.Context',
                   'relation': '.', 'subject': 'Template := work_report'}
        self.assertEqual(continuant_model_subject(concern),
                         'MODEL//ANECHOIC <+ Graph/Node//Atom//Ticket//Work Report')
        for field, value in (
            ('path', 'Model/Graph/Node//Atom//Ticket.Header.Context'),
            ('subject', 'Tier := 0'),
            ('subject', 'Template := work report'),
        ):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                continuant_model_subject({**concern, field: value})

    def test_concern_can_continue_from_a_resolved_variant(self):
        concern = {'path': 'Model/Graph/Node//Atom//Spec Atom//(Header.Context.Template := axiom)',
                   'subject': 'Next'}
        for relation, operator in (('is_property_of', '.'), ('is_contained_by', '/'), ('is_narrower_than', '//')):
            with self.subTest(relation=relation):
                self.assertEqual(continuant_model_subject({**concern, 'relation': relation}),
                                 'MODEL//ANECHOIC <+ Graph/Node//Atom//Spec Atom//Axiom' + operator + 'Next')
