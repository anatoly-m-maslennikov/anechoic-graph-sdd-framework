"""Check the checked-in generated Atom classes."""

from dataclasses import asdict, replace
from typing import get_type_hints
import unittest

from pydantic import TypeAdapter, ValidationError

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_GENERATED_MODEL_C52.FEATURE_GENERATED_MODEL_C52__shared \
    import (
        Atom,
        AtomContent,
        AtomContext,
        AtomHeader,
        AtomTier,
        Plan,
    )  # fmt: skip


class GeneratedAtomTests(unittest.TestCase):
    def test_generated_atom_composes_header_context_and_content(self):
        self.assertEqual(set(Atom.__dataclass_fields__), {"header", "content"})
        self.assertEqual(
            set(AtomHeader.__dataclass_fields__),
            {"identity", "context", "relations", "state", "destination"},
        )
        self.assertEqual(
            set(AtomContext.__dataclass_fields__),
            {
                "container",
                "role",
                "form",
                "label",
                "topics",
                "tier",
                "plan",
                "concern",
            },
        )
        self.assertEqual(
            set(AtomContent.__dataclass_fields__), {"summary", "properties"}
        )
        self.assertEqual(
            set(AtomTier.__dataclass_fields__), {"value", "label"}
        )
        relation = AtomHeader.__dataclass_fields__["relations"].metadata
        self.assertEqual(
            relation["dependent_property_value_cardinality"],
            {"minimum": 1, "maximum": None},
        )
        self.assertTrue(issubclass(Plan, Atom))

    def test_standalone_records_validate_and_preserve_operations(self):
        content = AtomContent("Dependency")
        self.assertEqual(
            asdict(content), {"summary": "Dependency", "properties": {}}
        )
        self.assertEqual(
            replace(content, summary="Condition"), AtomContent("Condition")
        )
        with self.assertRaises(TypeError):
            hash(content)
        with self.assertRaises(ValidationError):
            AtomContent(12)
        with self.assertRaises(ValidationError):
            AtomContent("Dependency", debug=True)

    def test_nullable_defaults_keep_constructor_and_admission_types(self):
        self.assertEqual(
            asdict(replace(AtomTier(2), value=3)), {"value": 3, "label": None}
        )
        self.assertEqual(replace(AtomTier(2), label=None), AtomTier(2))
        self.assertIs(get_type_hints(AtomTier)["label"], str)
        with self.assertRaises(ValidationError):
            AtomTier(2, label=12)

    def test_plan_reuses_typed_children_and_can_replace_omitted_defaults(self):
        header = TypeAdapter(AtomHeader).validate_json(
            """{
                "identity": {"id": "AN-T-1", "ref_id": "AN-T-1@1"},
                "context": {
                    "container": {"scope_unit": "C52"},
                    "role": "Plan", "form": "Plan",
                    "topics": {"main_subject": "Atom"}, "tier": {"value": 0}
                },
                "state": {
                    "status": "active", "version": 1,
                    "updated_at": "2026-11-24T00:00:00Z"
                },
                "destination": {"file": {"name": "atom.md", "path": "."}}
            }""",
            strict=True,
        )
        content = AtomContent("Sample")
        plan = Plan(header, content)
        self.assertIs(plan.header, header)
        self.assertIs(plan.content, content)
        self.assertEqual(replace(plan), plan)
        self.assertEqual(replace(header, relations=None), header)
        context = header.context
        self.assertEqual(
            replace(context, label=None, plan=None, concern=None), context
        )
        self.assertEqual(
            get_type_hints(AtomHeader)["relations"], dict[str, list[str]]
        )
        with self.assertRaises(ValidationError):
            Plan(asdict(header), content)
