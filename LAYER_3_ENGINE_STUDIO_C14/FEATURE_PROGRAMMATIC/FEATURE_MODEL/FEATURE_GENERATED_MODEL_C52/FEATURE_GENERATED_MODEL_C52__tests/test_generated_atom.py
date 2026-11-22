"""Check the checked-in generated Atom classes."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_GENERATED_MODEL_C52 import Atom, AtomContent, AtomContext, AtomHeader, AtomTier, Plan


class GeneratedAtomTests(unittest.TestCase):
    def test_generated_atom_composes_header_context_and_content(self):
        self.assertEqual(set(Atom.__dataclass_fields__), {"header", "content"})
        self.assertEqual(set(AtomHeader.__dataclass_fields__), {"identity", "context", "relations", "state", "destination"})
        self.assertEqual(set(AtomContext.__dataclass_fields__),
                         {"container", "role", "form", "label", "topics", "tier", "plan", "concern"})
        self.assertEqual(set(AtomContent.__dataclass_fields__), {"summary", "properties"})
        self.assertEqual(set(AtomTier.__dataclass_fields__), {"value", "label"})
        relation = AtomHeader.__dataclass_fields__["relations"].metadata
        self.assertEqual(relation["dependent_property_value_cardinality"], {"minimum": 1, "maximum": None})
        self.assertTrue(issubclass(Plan, Atom))
