"""Construct declared Pydantic groups while preserving legacy Model inputs."""

from collections import UserDict
from collections.abc import Mapping
from dataclasses import field, is_dataclass
from hashlib import sha256
from pathlib import Path
from runpy import run_path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass, is_pydantic_dataclass

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import validate_model_instance


GROUP = {"property_occurrence_cardinality": 1, "value_cardinality": 0, "dependent_property_cardinality": 1}
STRICT = ConfigDict(strict=True, extra="forbid")


@dataclass(config=STRICT)
class Identity:
    ref_id: str = field(metadata={"property_occurrence_cardinality": 1, "value_cardinality": 1})


@dataclass(config=STRICT)
class Header:
    identity: Identity = field(metadata=GROUP)


@dataclass(config=STRICT)
class Model:
    header: Header = field(metadata=GROUP)
    properties: dict[str, object] = field(default_factory=dict)


@dataclass(config=STRICT)
class OptionalModel:
    header: Header = field(default=None, kw_only=True, metadata={
        "property_occurrence_cardinality": {"minimum": 0, "maximum": 1},
        "value_cardinality": 0, "dependent_property_cardinality": 1,
    })


@dataclass(config=STRICT)
class MappingGroup(Mapping):
    value: str = field(metadata={"value_cardinality": 1})

    def __getitem__(self, key):
        if key != "value":
            raise KeyError(key)
        return self.value

    def __iter__(self):
        return iter(("value",))

    def __len__(self):
        return 1


@dataclass(config=STRICT)
class MappingModel:
    group: MappingGroup = field(metadata=GROUP)


def admit(kind, properties, *, checks=None, rules=(), peers=()):
    declarations = {owner: {} for owner in kind.__mro__[:-1]}
    population = {owner: rules if owner is kind else () for owner in kind.__mro__[:-1]}
    return validate_model_instance(kind, properties=properties, outgoing_relations={}, relation_declarations=declarations,
                                   model_types={}, checks=checks or {}, population_declarations=population,
                                   population_peers={kind: peers})


class ConstructGroupsTest(unittest.TestCase):
    def test_nested_mapping_constructs_typed_groups_and_preserves_plain_mapping(self):
        properties = {"plain": ["one", {"two": 2}]}
        raw = UserDict({"header": UserDict({"identity": UserDict({"ref_id": "AN-T-1"})}), "properties": properties})
        result = admit(Model, raw, checks={"typed": lambda value: isinstance(value.header.identity, Identity)})
        self.assertIsInstance(result.header, Header)
        self.assertIsInstance(result.header.identity, Identity)
        self.assertEqual("AN-T-1", result.header.identity.ref_id)
        self.assertEqual(properties, result.properties)
        self.assertIsInstance(raw["header"], UserDict)
        self.assertIsInstance(raw["header"]["identity"], UserDict)

    def test_typed_groups_keep_identity(self):
        identity = Identity(ref_id="AN-T-2")
        header = Header(identity=identity)
        self.assertIs(header, admit(Model, {"header": header}).header)
        self.assertIs(identity, admit(Model, {"header": {"identity": identity}}).header.identity)
        typed_mapping = MappingGroup(value="typed")
        self.assertIs(typed_mapping, admit(MappingModel, {"group": typed_mapping}).group)

    def test_historical_c52_destination_preserves_legacy_mapping(self):
        """Load C52 atom_fields.py lines 1–8 and 40–47 from b5f7ed5266.

        Keep the original namespace available to resolve deferred annotations.
        """
        fixture = Path(__file__).parent / "assets/fixtures/c52-b5f7ed5266-atom-destination.py.txt"
        self.assertEqual(
            "1e1898be63e79a1c61e76f9c8aecff1ba85bd7e82867fa0bfbd933675252ea45",
            sha256(fixture.read_bytes()).hexdigest(),
        )
        legacy = ModuleType(f"{__name__}._historical_c52")
        legacy.__dict__.update(run_path(str(fixture), run_name=legacy.__name__))
        with patch.dict(sys.modules, {legacy.__name__: legacy}):
            destination, file_type = legacy.AtomDestination, legacy.AtomDestinationFile
            for kind in (destination, file_type):
                self.assertTrue(is_dataclass(kind))
                self.assertFalse(is_pydantic_dataclass(kind))
            raw = {"name": "atom.md", "path": "."}
            self.assertIs(raw, admit(destination, {"file": raw}).file)
            typed = file_type("atom.md", ".")
            self.assertIs(typed, admit(destination, {"file": typed}).file)
            with self.assertRaisesRegex(ValueError, "file.path"):
                admit(destination, {"file": raw | {"path": 1}})

    def test_invalid_nested_values_keep_diagnostic_paths(self):
        for raw, message in (({"header": {"identity": {"ref_id": 1}}}, "header.identity.ref_id"),
                             ({"header": {"identity": {"ref_id": None}}}, "header.identity.ref_id"),
                             ({"header": {"identity": {}}}, "header.identity.ref_id"),
                             ({"header": {"identity": {"ref_id": "a", "extra": True}}}, "header.identity.Undeclared")):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, message):
                admit(Model, raw)

    def test_omitted_group_differs_from_explicit_null(self):
        self.assertIsNone(admit(OptionalModel, {}).header)
        with self.assertRaisesRegex(ValueError, "header"):
            admit(OptionalModel, {"header": None})
        self.assertIsInstance(admit(OptionalModel, {"header": {"identity": {"ref_id": "A"}}}).header, Header)

    def test_mutated_typed_group_is_checked_without_replacing_it(self):
        identity = Identity(ref_id="valid")
        header = Header(identity=identity)
        identity.ref_id = 42
        with self.assertRaisesRegex(ValueError, "header.identity.ref_id"):
            admit(Model, {"header": header})

    def test_mutated_typed_group_cannot_hide_a_raw_nested_mapping(self):
        header = Header(identity=Identity(ref_id="valid"))
        header.identity = {"ref_id": "raw"}
        with self.assertRaisesRegex(ValueError, "header.identity"):
            admit(Model, {"header": header})

    def test_checks_uniqueness_and_cycles_use_constructed_values(self):
        raw = {"header": {"identity": {"ref_id": "AN-T-3"}}}
        peer = admit(Model, raw)
        with self.assertRaisesRegex(ValueError, "Population uniqueness violated: Header.Identity.Ref ID"):
            admit(Model, raw, rules=({"keys": ("Header.Identity.Ref ID",)},), peers=(peer,))
        cycle = {}
        cycle["self"] = cycle
        with self.assertRaisesRegex(ValueError, "contain a cycle"):
            admit(Model, {**raw, "properties": cycle})


if __name__ == "__main__":
    unittest.main()
