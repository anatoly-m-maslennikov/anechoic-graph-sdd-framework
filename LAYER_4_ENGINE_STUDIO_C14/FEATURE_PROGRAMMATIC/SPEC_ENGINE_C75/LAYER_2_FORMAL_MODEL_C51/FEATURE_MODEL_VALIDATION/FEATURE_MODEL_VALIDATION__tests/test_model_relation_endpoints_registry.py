"""Check Model Relation endpoint registries."""

import unittest

from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_native_model_claim,
)
from .test_model_relation_validation import (
    Container,
    Item,
    Node,
    SpecialItem,
    _RelationFixture,
)


class RelationEndpointRegistryTests(_RelationFixture, unittest.TestCase):
    def test_endpoint_registry_enforces_paired_levels_and_inverse_direction(
        self,
    ):
        claim = _kind_claim()
        declarations = {Node: {"KIND": {"targets_per_source": 1}}}
        registry = {"KIND": (claim, False), "KIND_OF": (claim, True)}
        types = {"Node": Node, "Item": Item}
        self.admit(
            Node,
            {"KIND": [Item]},
            declarations,
            types,
            endpoint_registry=registry,
        )
        with self.assertRaisesRegex(
            ValueError, "endpoint levels or kinds are not admitted"
        ):
            self.admit(
                Node,
                {"KIND": [Item()]},
                declarations,
                types,
                endpoint_registry=registry,
            )
        with self.assertRaisesRegex(
            ValueError, "endpoint levels or kinds are not admitted"
        ):
            self.admit(
                Node,
                {"KIND_OF": [Item]},
                {Node: {"KIND_OF": {}}},
                types,
                endpoint_registry=registry,
            )
        with self.assertRaisesRegex(
            ValueError, "Model target is not declared"
        ):
            self.admit(
                Node,
                {"KIND": [Container]},
                declarations,
                types,
                endpoint_registry=registry,
            )

    def test_explicit_endpoint_pairs_do_not_create_cross_level_links(self):
        claim = _cross_claim()
        registry = {"LINKS": (claim, False)}
        types = {"Item": Item}
        self.admit(
            Node,
            {"LINKS": [Item()]},
            self.declarations,
            types,
            endpoint_registry=registry,
        )
        with self.assertRaisesRegex(
            ValueError, "endpoint levels or kinds are not admitted"
        ):
            self.admit(
                Node,
                {"LINKS": [Item]},
                self.declarations,
                types,
                endpoint_registry=registry,
            )
        with self.assertRaisesRegex(
            ValueError, "missing or invalid Relation Declaration"
        ):
            self.admit(
                Node,
                {"LINKS": [Item()]},
                self.declarations,
                types,
                endpoint_registry={},
            )
        with self.assertRaisesRegex(
            ValueError, "inconsistent Relation Declaration binding"
        ):
            self.admit(
                Node,
                {"LINKS": [Item()]},
                self.declarations,
                types,
                endpoint_registry={"LINKS": (claim, True)},
            )

    def test_endpoint_kinds_must_match_the_same_declared_pair(self):
        claim = _pair_claim()
        registry = {"LINKS": (claim, False), "LINKED_BY": (claim, True)}
        types = {"Node": Node, "Item": Item, "Container": Container}
        rules = {Node: {"LINKS": {}, "LINKED_BY": {}}}
        self.admit(
            Node,
            {"LINKS": [SpecialItem()]},
            rules,
            types,
            endpoint_registry=registry,
        )
        with self.assertRaisesRegex(
            ValueError, "endpoint levels or kinds are not admitted"
        ):
            self.admit(
                Node,
                {"LINKS": [Container()]},
                rules,
                types,
                endpoint_registry=registry,
            )
        with self.assertRaisesRegex(
            ValueError, "endpoint levels or kinds are not admitted"
        ):
            self.admit(
                Node,
                {"LINKED_BY": [Item()]},
                rules,
                types,
                endpoint_registry=registry,
            )
        types.pop("Container")
        with self.assertRaisesRegex(ValueError, "unresolved endpoint kind"):
            self.admit(
                Node,
                {"LINKS": [Item()]},
                rules,
                types,
                endpoint_registry=registry,
            )

    def test_relation_declaration_admits_direct_links_without_an_entity_rule(
        self,
    ):
        claim = _direct_claim()
        registry = {
            "SPECIALIZES": (claim, False),
            "IS_SPECIALIZED_BY": (claim, True),
        }
        types = {"Item": Item}
        rules = {Node: {}, Item: {}, SpecialItem: {}}
        self.admit(
            SpecialItem,
            {"SPECIALIZES": [Item()]},
            rules,
            types,
            endpoint_registry=registry,
        )
        with self.assertRaisesRegex(
            ValueError, "endpoint levels or kinds are not admitted"
        ):
            self.admit(
                Node,
                {"SPECIALIZES": [Item()]},
                rules,
                types,
                endpoint_registry=registry,
            )
        with self.assertRaisesRegex(
            ValueError, "inverse Relation requires explicit permission"
        ):
            self.admit(
                Item,
                {"IS_SPECIALIZED_BY": [Item()]},
                rules,
                types,
                endpoint_registry=registry,
            )
        rules[Item]["SPECIALIZES"] = {"targets_per_source": 1}
        with self.assertRaisesRegex(ValueError, "target count"):
            self.admit(
                SpecialItem, {}, rules, types, endpoint_registry=registry
            )


def _kind_claim():
    claim = parse_native_model_claim(
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='KIND', inverse_alias='KIND_OF', "
        "source_endpoint={'level': 'instances'}, "
        "target_endpoint={'level': 'model_entities'})"
    )["arguments"]
    return claim


def _cross_claim():
    claim = parse_native_model_claim(
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='LINKS', endpoint_pairs=("
        "{'source_endpoint': {'level': 'model_entities'}, "
        "'target_endpoint': {'level': 'model_entities'}},"
        "{'source_endpoint': {'level': 'instances'}, "
        "'target_endpoint': {'level': 'instances'}},))"
    )["arguments"]
    return claim


def _pair_claim():
    claim = parse_native_model_claim(
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='LINKS', "
        "inverse_alias='LINKED_BY', endpoint_pairs=("
        "{'source_endpoint': {'entity_paths': ('Node',)}, "
        "'target_endpoint': {'entity_paths': ('Item',)}},"
        "{'source_endpoint': {'entity_paths': ('Container',)}, "
        "'target_endpoint': {'entity_paths': ('Node',)}},))"
    )["arguments"]
    return claim


def _direct_claim():
    claim = {
        "relation_name": "SPECIALIZES",
        "source_endpoint": {
            "level": "instances",
            "entity_paths": ("Item",),
        },
        "target_endpoint": {
            "level": "instances",
            "entity_paths": ("Item",),
        },
        "inverse_alias": "IS_SPECIALIZED_BY",
    }
    return claim
