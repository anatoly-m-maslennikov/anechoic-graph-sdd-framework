"""Validate generated field contracts at the proposed instance boundary."""

from dataclasses import dataclass, field
from pathlib import Path
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[3]
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import validate_model_fields  # noqa: E402


@dataclass
class Entity:
    identity: int = field(metadata={"property_occurrence_cardinality": 1, "value_cardinality": 1})


@dataclass
class Record(Entity):
    tags: list[str] = field(default_factory=list, metadata={
        "property_occurrence_cardinality": {"minimum": 0, "maximum": 1},
        "value_cardinality": {"minimum": 1, "maximum": 2},
    })


class ModelFieldValidationTests(unittest.TestCase):
    def test_authored_relation_names_and_atom_references(self):
        many = {"minimum": 1, "maximum": None}

        @dataclass
        class Header:
            relations: dict[str, list[str]] | None = field(default=None, metadata={
                "value_cardinality": 0, "dependent_property_cardinality": many,
                "dependent_property_value_cardinality": many,
                "allowed_relation_names": ("IS_REFERENCE",),
            })

        validate_model_fields(Header, {})
        validate_model_fields(Header, {"relations": {"IS_REFERENCE": ["AN-S-2", "AN-S-3@1-draft"]}})
        for relation, targets, error in (
            ("HAS_REFERENCE", ["AN-S-2"], "undeclared authored Relation"),
            ("IS_REFERENCE", ["C9"], "expected Atom references"),
            ("IS_REFERENCE", ["AN-S-2", "AN-S-2"], "duplicate Atom reference"),
            ("IS_REFERENCE", [], "value count"),
        ):
            with self.subTest(relation=relation, targets=targets), self.assertRaisesRegex(ValueError, error):
                validate_model_fields(Header, {"relations": {relation: targets}})

    def test_valid_inherited_and_optional_field(self):
        validate_model_fields(Record, {"identity": 1})
        validate_model_fields(Record, {"identity": 1, "tags": ["one", "two"]})

    def test_rejects_unknown_missing_and_wrong_types(self):
        for values in ({"identity": 1, "other": 2}, {}, {"identity": "1"},
                       {"identity": 1, "tags": [1]}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                validate_model_fields(Record, values)

    def test_rejects_present_empty_and_excess_values(self):
        for tags in ([], ["one", "two", "three"]):
            with self.subTest(tags=tags), self.assertRaises(ValueError):
                validate_model_fields(Record, {"identity": 1, "tags": tags})

    def test_allowed_values_apply_to_each_direct_value(self):
        @dataclass
        class Choice:
            values: list[str] = field(metadata={"value_cardinality": {"minimum": 1, "maximum": 2},
                                                "allowed_values": ("a", "b")})
            scalar: str = field(metadata={"value_cardinality": 1, "allowed_values": ("a", "b")})

        validate_model_fields(Choice, {"values": ["a", "b"], "scalar": "a"})
        with self.assertRaisesRegex(ValueError, "values: value must be one of"):
            validate_model_fields(Choice, {"values": ["a", "c"], "scalar": "a"})
        with self.assertRaisesRegex(ValueError, "values: value count"):
            validate_model_fields(Choice, {"values": [], "scalar": "a"})
        with self.assertRaisesRegex(ValueError, "scalar:"):
            validate_model_fields(Choice, {"values": ["a"], "scalar": 1})

        @dataclass
        class TupleChoice:
            values: tuple[str, ...] = field(metadata={"value_cardinality": 2, "allowed_values": ("a", "b")})

        validate_model_fields(TupleChoice, {"values": ("a", "b")})
        with self.assertRaisesRegex(ValueError, "values: value must be one of"):
            validate_model_fields(TupleChoice, {"values": ("a", "c")})

    def test_rejects_numeric_coercion(self):
        @dataclass
        class Reading:
            value: float

        with self.assertRaisesRegex(ValueError, "type conversion"):
            validate_model_fields(Reading, {"value": 1})

        @dataclass
        class Readings:
            values: set[float]

        with self.assertRaisesRegex(ValueError, "type conversion"):
            validate_model_fields(Readings, {"values": {1}})

    def test_value_count_determines_presence_when_occurrence_is_omitted(self):
        @dataclass
        class OptionalText:
            text: str = field(metadata={"value_cardinality": {"minimum": 0, "maximum": 1}})

        validate_model_fields(OptionalText, {})
        validate_model_fields(OptionalText, {"text": "present"})

    def test_invalid_metadata_fails_even_if_optional_property_is_absent(self):
        @dataclass
        class Invalid:
            name: str = field(default="", metadata={"value_cardinality": {"minimum": 2, "maximum": 1}})

        with self.assertRaisesRegex(ValueError, "Invalid cardinality"):
            validate_model_fields(Invalid, {})

    def test_nested_model_fields_are_validated(self):
        @dataclass
        class Document:
            header: Entity

        validate_model_fields(Document, {"header": Entity(1)})
        with self.assertRaises(ValueError):
            validate_model_fields(Document, {"header": Entity("1")})
        header = Entity(1)
        header.undeclared = True
        with self.assertRaisesRegex(ValueError, "Undeclared properties"):
            validate_model_fields(Document, {"header": header})

    def test_generated_destination_checks_children_separately_from_direct_values(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_GENERATED_MODEL_C52.FEATURE_GENERATED_MODEL_C52__shared import (
            AtomDestination, AtomDestinationFile,
        )

        validate_model_fields(AtomDestination, {"file": AtomDestinationFile("atom.md", ".")})
        with self.assertRaisesRegex(ValueError, "file.path"):
            validate_model_fields(AtomDestination, {"file": AtomDestinationFile("atom.md", 1)})
        with self.assertRaisesRegex(ValueError, "file: occurrence count"):
            validate_model_fields(AtomDestination, {})
        with self.assertRaisesRegex(ValueError, "Undeclared properties"):
            validate_model_fields(AtomDestination, {"directory": "."})

    def test_cyclic_dependent_properties_are_rejected(self):
        @dataclass
        class Document:
            content: dict

        content = {}
        content["child"] = content
        with self.assertRaisesRegex(ValueError, "contain a cycle"):
            validate_model_fields(Document, {"content": content})


if __name__ == "__main__":
    unittest.main()
