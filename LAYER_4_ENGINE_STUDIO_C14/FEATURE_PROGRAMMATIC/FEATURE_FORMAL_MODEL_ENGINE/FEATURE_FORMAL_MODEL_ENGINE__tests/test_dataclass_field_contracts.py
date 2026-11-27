"""Project typed dataclass field contracts without executing Model code."""

import unittest


from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.\
    FEATURE_FORMAL_MODEL_ENGINE__shared \
    import compiler_model_statements  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import parse_native_model_claim  # fmt: skip


CLAIM = """from dataclasses import dataclass, field
from anechoic.formal_claims import Cardinality, declare_entity

@dataclass
class Example:
    id: int = field(metadata={
        "property_occurrence_cardinality": 1,
        "value_cardinality": 1,
    })
    name: str = field(metadata={
        "property_occurrence_cardinality": Cardinality(minimum=0, maximum=1),
        "value_cardinality": Cardinality(minimum=0, maximum=1),
    })

declare_entity(entity_name="Example", entity_class=Example)
"""


class DataclassFieldContractsTests(unittest.TestCase):
    def test_projects_formats_and_both_cardinalities(self):
        declaration = parse_native_model_claim(CLAIM)
        self.assertEqual(
            (
                "Example.id{::1} :: [int]{::1}",
                "Example.name{::0..1} :: [string]{::0..1}",
            ),
            compiler_model_statements(declaration),
        )

    def test_unconstrained_class_keeps_existing_behavior(self):
        claim = """from dataclasses import dataclass
from anechoic.formal_claims import declare_entity

@dataclass
class Example:
    id: int

declare_entity(entity_name="Example", entity_class=Example)
"""
        self.assertEqual(
            (), compiler_model_statements(parse_native_model_claim(claim))
        )

    def test_rejects_partial_contract_and_unsupported_format(self):
        for claim, error in (
            (
                CLAIM.replace("    id: int", "    extra: str\n    id: int"),
                "unsupported dataclass field contract",
            ),
            (
                CLAIM.replace('"value_cardinality": 1', '"other": 1'),
                "require occurrence and value cardinalities",
            ),
            (
                CLAIM.replace("id: int", "id: list[int]"),
                "unsupported compiler format",
            ),
        ):
            with (
                self.subTest(error=error),
                self.assertRaisesRegex(ValueError, error),
            ):
                compiler_model_statements(parse_native_model_claim(claim))

    def test_root_class_and_nested_dataclass_records(self):
        claim = """
from dataclasses import dataclass
from anechoic.formal_claims import declare_entity

@dataclass(kw_only=True)
class AtomHeader:
    label: str | None = None

@dataclass(kw_only=True)
class Atom:
    header: AtomHeader

declare_entity(entity_class=Atom, entity_name="Atom")
"""
        result = parse_native_model_claim(claim)
        self.assertEqual((), result["classes"][0]["bases"])
        self.assertEqual((), result["classes"][1]["bases"])
        self.assertEqual(
            "AtomHeader", result["classes"][1]["fields"][0]["annotation"]
        )
