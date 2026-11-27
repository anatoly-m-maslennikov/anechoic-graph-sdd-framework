"""Exercise the shared validation path with inherited Model contracts."""

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import validate_model_instance


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Parent:
    identity: int


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Child(Parent):
    pass


def identity_is_positive(instance: Child) -> bool:
    return instance.identity > 0


class InstanceValidationTests(unittest.TestCase):
    def validate(self, identity, outgoing_relations, *, rules=(), peers=None, endpoint_registry=None):
        return validate_model_instance(
            Child,
            properties={"identity": identity},
            outgoing_relations=outgoing_relations,
            relation_declarations={
                Parent: {"LINKS": {"targets_per_source": 1, "target_entity_paths": ("Parent",)}},
                Child: {},
            },
            model_types={"Parent": Parent},
            checks={"identity_is_positive": identity_is_positive},
            population_declarations={Parent: rules, Child: ()},
            population_peers={} if peers is None else {Parent: peers},
            endpoint_registry=endpoint_registry,
        )

    def test_accepts_valid_instance_and_checks_each_contract(self):
        self.assertEqual(self.validate(1, {"LINKS": [Parent(2)]}), Child(1))
        with self.assertRaises(ValueError):
            self.validate("1", {"LINKS": [Parent(2)]})
        with self.assertRaisesRegex(ValueError, "target count"):
            self.validate(1, {})
        with self.assertRaisesRegex(ValueError, "identity_is_positive: instance check failed"):
            self.validate(0, {"LINKS": [Parent(2)]})

    def test_applies_inherited_uniqueness_to_the_complete_supplied_population(self):
        relations = {"LINKS": [Parent(2)]}
        rules = ({"keys": ("Identity",)},)
        self.assertEqual(self.validate(1, relations, rules=rules, peers=[Parent(2)]), Child(1))
        with self.assertRaisesRegex(ValueError, "Population uniqueness violated"):
            self.validate(1, relations, rules=rules, peers=[Parent(1)])
        with self.assertRaisesRegex(ValueError, "Missing population for Parent"):
            self.validate(1, relations, rules=rules)

    def test_applies_endpoint_declarations_to_inherited_relations(self):
        args = {
            "relation_name": "LINKS",
            "source_endpoint": {"level": "instances", "entity_paths": ("Parent",)},
            "target_endpoint": {"level": "instances", "entity_paths": ("Parent",)},
        }
        registry = {"LINKS": (args, False)}
        self.assertEqual(self.validate(1, {"LINKS": [Child(2)]}, endpoint_registry=registry), Child(1))
        args["target_endpoint"]["level"] = "model_entities"
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds are not admitted"):
            self.validate(1, {"LINKS": [Child(2)]}, endpoint_registry=registry)
