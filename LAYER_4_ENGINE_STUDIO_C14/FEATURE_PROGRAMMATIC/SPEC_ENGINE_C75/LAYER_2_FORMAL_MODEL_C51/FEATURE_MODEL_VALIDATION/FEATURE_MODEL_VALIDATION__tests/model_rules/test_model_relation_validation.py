"""Check Relation inheritance, bounds, endpoints and a closed whitelist."""

import unittest

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim as parse_native_model_claim,
)


from ...FEATURE_MODEL_VALIDATION__shared import validate_model_instance


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Node:
    pass


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Item(Node):
    pass


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class SpecialItem(Item):
    pass


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Container(Node):
    pass


class _RelationFixture:
    def setUp(self):
        self.declarations = {
            Node: {
                "LINKS": {
                    "targets_per_source": 1,
                    "target_entity_paths": ("Item",),
                }
            },
            Container: {
                "LINKS": {"targets_per_source": 0},
                "CONTAINS": {
                    "targets_per_source": {"minimum": 1, "maximum": 2},
                    "target_entity_paths": ("Item",),
                },
            },
        }
        self.model_types = {"Item": Item}

    def admit(
        self,
        model_class,
        relations,
        declarations,
        model_types,
        *,
        endpoint_registry=None,
    ):
        return validate_model_instance(
            model_class,
            properties={},
            outgoing_relations=relations,
            relation_declarations=declarations,
            model_types=model_types,
            checks={},
            population_declarations={
                owner: () for owner in model_class.__mro__[:-1]
            },
            population_peers={},
            endpoint_registry=endpoint_registry,
        )


class RelationValidationTests(_RelationFixture, unittest.TestCase):
    def test_inherited_constraints_and_subtypes(self):
        self.admit(
            Node,
            {"LINKS": [SpecialItem()]},
            self.declarations,
            self.model_types,
        )
        with self.assertRaisesRegex(ValueError, "target count"):
            self.admit(Node, {}, self.declarations, self.model_types)
        with self.assertRaisesRegex(ValueError, "invalid target kind"):
            self.admit(
                Node,
                {"LINKS": [Container()]},
                self.declarations,
                self.model_types,
            )

    def test_local_override_and_other_local_relation(self):
        self.admit(
            Container,
            {"CONTAINS": [Item()]},
            self.declarations,
            self.model_types,
        )
        with self.assertRaisesRegex(ValueError, "target count"):
            self.admit(
                Container,
                {"LINKS": [Item()], "CONTAINS": [Item()]},
                self.declarations,
                self.model_types,
            )
        with self.assertRaisesRegex(ValueError, "target count"):
            self.admit(Container, {}, self.declarations, self.model_types)

    def test_unknown_relation_and_unresolved_contract_fail(self):
        with self.assertRaisesRegex(ValueError, "Undeclared Relations"):
            self.admit(
                Node, {"OTHER": []}, self.declarations, self.model_types
            )
        with self.assertRaisesRegex(
            ValueError, "Missing Relation Declaration"
        ):
            self.admit(Container, {}, {Container: {}}, self.model_types)
        with self.assertRaisesRegex(ValueError, "unresolved target kind"):
            self.admit(Node, {"LINKS": [Item()]}, self.declarations, {})
        self.declarations[Node]["LINKS"]["sources_per_target"] = 1
        with self.assertRaisesRegex(ValueError, "population validation"):
            self.admit(
                Node, {"LINKS": [Item()]}, self.declarations, self.model_types
            )


if __name__ == "__main__":
    unittest.main()
