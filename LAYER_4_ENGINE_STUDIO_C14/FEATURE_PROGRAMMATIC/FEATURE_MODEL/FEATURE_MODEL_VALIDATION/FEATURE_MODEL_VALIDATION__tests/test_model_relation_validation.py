"""Check Relation inheritance, bounds, endpoints and a closed whitelist."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_relation_validation import validate_model_relations
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim


class Node:
    pass


class Item(Node):
    pass


class SpecialItem(Item):
    pass


class Container(Node):
    pass


class RelationValidationTests(unittest.TestCase):
    def setUp(self):
        self.declarations = {
            Node: {"LINKS": {"targets_per_source": 1, "target_entity_paths": ("Item",)}},
            Container: {"LINKS": {"targets_per_source": 0},
                        "CONTAINS": {"targets_per_source": {"minimum": 1, "maximum": 2},
                                     "target_entity_paths": ("Item",)}},
        }
        self.model_types = {"Item": Item}

    def test_inherited_constraints_and_subtypes(self):
        validate_model_relations(Node, {"LINKS": [SpecialItem()]}, self.declarations, self.model_types)
        with self.assertRaisesRegex(ValueError, "target count"):
            validate_model_relations(Node, {}, self.declarations, self.model_types)
        with self.assertRaisesRegex(ValueError, "invalid target kind"):
            validate_model_relations(Node, {"LINKS": [Container()]}, self.declarations, self.model_types)

    def test_local_override_and_other_local_relation(self):
        validate_model_relations(Container, {"CONTAINS": [Item()]}, self.declarations, self.model_types)
        with self.assertRaisesRegex(ValueError, "target count"):
            validate_model_relations(Container, {"LINKS": [Item()], "CONTAINS": [Item()]},
                                     self.declarations, self.model_types)
        with self.assertRaisesRegex(ValueError, "target count"):
            validate_model_relations(Container, {}, self.declarations, self.model_types)

    def test_unknown_relation_and_unresolved_contract_fail(self):
        with self.assertRaisesRegex(ValueError, "Undeclared Relations"):
            validate_model_relations(Node, {"OTHER": []}, self.declarations, self.model_types)
        with self.assertRaisesRegex(ValueError, "Missing Relation Declaration"):
            validate_model_relations(Container, {}, {Container: {}}, self.model_types)
        with self.assertRaisesRegex(ValueError, "unresolved target kind"):
            validate_model_relations(Node, {"LINKS": [Item()]}, self.declarations, {})
        self.declarations[Node]["LINKS"]["sources_per_target"] = 1
        with self.assertRaisesRegex(ValueError, "population validation"):
            validate_model_relations(Node, {"LINKS": [Item()]}, self.declarations, self.model_types)

    def test_endpoint_registry_enforces_paired_levels_and_inverse_direction(self):
        claim = parse_native_model_claim(
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='KIND', inverse_alias='KIND_OF', "
            "source_endpoint={'level': 'instances'}, target_endpoint={'level': 'model_entities'})"
        )["arguments"]
        declarations = {Node: {"KIND": {"targets_per_source": 1}}}
        registry = {"KIND": (claim, False), "KIND_OF": (claim, True)}
        types = {"Node": Node, "Item": Item}
        validate_model_relations(Node, {"KIND": [Item]}, declarations, types, endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds are not admitted"):
            validate_model_relations(Node, {"KIND": [Item()]}, declarations, types, endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds are not admitted"):
            validate_model_relations(Node, {"KIND_OF": [Item]}, {Node: {"KIND_OF": {}}}, types,
                                     endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "Model target is not declared"):
            validate_model_relations(Node, {"KIND": [Container]}, declarations, types,
                                     endpoint_registry=registry)

    def test_explicit_endpoint_pairs_do_not_create_cross_level_links(self):
        claim = parse_native_model_claim(
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='LINKS', endpoint_pairs=("
            "{'source_endpoint': {'level': 'model_entities'}, 'target_endpoint': {'level': 'model_entities'}},"
            "{'source_endpoint': {'level': 'instances'}, 'target_endpoint': {'level': 'instances'}},))"
        )["arguments"]
        registry = {"LINKS": (claim, False)}
        types = {"Item": Item}
        validate_model_relations(Node, {"LINKS": [Item()]}, self.declarations, types, endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds are not admitted"):
            validate_model_relations(Node, {"LINKS": [Item]}, self.declarations, types, endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "missing or invalid Relation Declaration"):
            validate_model_relations(Node, {"LINKS": [Item()]}, self.declarations, types, endpoint_registry={})
        with self.assertRaisesRegex(ValueError, "inconsistent Relation Declaration binding"):
            validate_model_relations(Node, {"LINKS": [Item()]}, self.declarations, types,
                                     endpoint_registry={"LINKS": (claim, True)})

    def test_endpoint_kinds_must_match_the_same_declared_pair(self):
        claim = parse_native_model_claim(
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='LINKS', inverse_alias='LINKED_BY', endpoint_pairs=("
            "{'source_endpoint': {'entity_paths': ('Node',)}, "
            "'target_endpoint': {'entity_paths': ('Item',)}},"
            "{'source_endpoint': {'entity_paths': ('Container',)}, "
            "'target_endpoint': {'entity_paths': ('Node',)}},))"
        )["arguments"]
        registry = {"LINKS": (claim, False), "LINKED_BY": (claim, True)}
        types = {"Node": Node, "Item": Item, "Container": Container}
        rules = {Node: {"LINKS": {}, "LINKED_BY": {}}}
        validate_model_relations(Node, {"LINKS": [SpecialItem()]}, rules, types, endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds are not admitted"):
            validate_model_relations(Node, {"LINKS": [Container()]}, rules, types, endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds are not admitted"):
            validate_model_relations(Node, {"LINKED_BY": [Item()]}, rules, types, endpoint_registry=registry)
        types.pop("Container")
        with self.assertRaisesRegex(ValueError, "unresolved endpoint kind"):
            validate_model_relations(Node, {"LINKS": [Item()]}, rules, types, endpoint_registry=registry)

    def test_relation_declaration_admits_direct_links_without_an_entity_rule(self):
        claim = {
            "relation_name": "SPECIALIZES",
            "source_endpoint": {"level": "instances", "entity_paths": ("Item",)},
            "target_endpoint": {"level": "instances", "entity_paths": ("Item",)},
            "inverse_alias": "IS_SPECIALIZED_BY",
        }
        registry = {"SPECIALIZES": (claim, False), "IS_SPECIALIZED_BY": (claim, True)}
        types = {"Item": Item}
        rules = {Node: {}, Item: {}, SpecialItem: {}}
        validate_model_relations(SpecialItem, {"SPECIALIZES": [Item()]}, rules, types, endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds are not admitted"):
            validate_model_relations(Node, {"SPECIALIZES": [Item()]}, rules, types, endpoint_registry=registry)
        with self.assertRaisesRegex(ValueError, "inverse Relation requires explicit permission"):
            validate_model_relations(Item, {"IS_SPECIALIZED_BY": [Item()]}, rules, types, endpoint_registry=registry)
        rules[Item]["SPECIALIZES"] = {"targets_per_source": 1}
        with self.assertRaisesRegex(ValueError, "target count"):
            validate_model_relations(SpecialItem, {}, rules, types, endpoint_registry=registry)


if __name__ == "__main__":
    unittest.main()
