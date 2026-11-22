"""Native relation declarations retain Workbench registry behavior."""

from pathlib import Path
import unittest

WORKBENCH = Path(__file__).resolve().parents[2]
PROGRAMMATIC = WORKBENCH.parents[1] / "FEATURE_PROGRAMMATIC"

from KERNEL_MIXER_C59.relation_registry import compile_relation_registry, registry_contribution  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import _outgoing_facts  # noqa: E402


def _row(statements):
    body = "## Claim\n\n### Formal Claim\n\n```CFEL\n" + ";\n".join(statements) + ";\n```\n"
    return {"id": "CA-R-1", "ref": "CA-R-1", "version": 1, "source_path": "source.md",
            "status_group": "Current", "role": "Requirement", "form": "Declaration",
            "_content_bytes": body.encode(), "content_markdown": body}


def _native_row(source, identifier="CA-R-1"):
    result = _row(())
    body = f"## Claim\n### Formal Claim\n```python\n{source}\n```\n"
    return result | {"id": identifier, "ref": identifier, "_content_bytes": body.encode(),
                     "content_markdown": body}


class CompilerRegistryTests(unittest.TestCase):
    def test_relation_registry_keeps_instance_reverse_views(self):
        native = '''
from anechoic.formal_claims import declare_relation
declare_relation(relation_name="IS_PROPERTY_OF", inverse_alias="HAS_PROPERTY",
    source_endpoint={"level": "model_entities_or_instances"},
    target_endpoint={"level": "model_entities_or_instances"})
'''
        result = registry_contribution(_native_row(native))
        self.assertEqual(frozenset({"IS_PROPERTY_OF", "HAS_PROPERTY"}), result.names)
        self.assertEqual((), result.aliases)
        self.assertEqual((("IS_PROPERTY_OF", "HAS_PROPERTY"),), result.inverses)


    def test_native_inverses_produce_reverse_row(self):
        for relation, inverse in (("CARRIES", "IS_CARRIED_BY"), ("IS_PROPERTY_OF", "HAS_PROPERTY")):
            with self.subTest(relation=relation):
                source = (
                    "from anechoic.formal_claims import declare_relation\n"
                    f"declare_relation(relation_name='{relation}', inverse_alias='{inverse}', "
                    "source_endpoint={'level': 'instances'}, "
                    "target_endpoint={'level': 'model_entities_or_instances'})"
                )
                native = _native_row(source, "CA-R-2")
                native["source_path"] = "native.md"
                alone = compile_relation_registry([native])
                self.assertEqual(alone.inverse, {relation: inverse})
                self.assertEqual(alone.aliases, {})
                fact = ("atom", "CA-R-1", relation, "atom", "CA-R-2")
                expected = ("atom", "CA-R-2", inverse, "atom", "CA-R-1", True)
                self.assertIn(expected, _outgoing_facts([], alone, {"source.md": (fact,)})[("atom", "CA-R-2")])


    def test_model_only_inverse_remains_an_alias(self):
        native = '''
from anechoic.formal_claims import declare_relation
declare_relation(relation_name="IS_ORDERED_RIGHT_AFTER", inverse_alias="IS_ORDERED_RIGHT_BEFORE",
    source_endpoint={"level": "model_entities"},
    target_endpoint={"level": "model_entities"})
'''
        result = registry_contribution(_native_row(native))
        self.assertEqual(frozenset({"IS_ORDERED_RIGHT_AFTER"}), result.names)
        self.assertEqual((("IS_ORDERED_RIGHT_BEFORE", "IS_ORDERED_RIGHT_AFTER"),), result.aliases)
        self.assertEqual((), result.inverses)


    def test_instance_sibling_order_keeps_reverse_alias(self):
        source = """from anechoic.formal_claims import declare_relation
declare_relation(relation_name="IS_ORDERED_RIGHT_AFTER", inverse_alias="IS_ORDERED_RIGHT_BEFORE",
    source_endpoint={"level": "instances"}, target_endpoint={"level": "instances"},
    same_immediate_bearer=True)
"""
        result = registry_contribution(_native_row(source))
        self.assertEqual((("IS_ORDERED_RIGHT_BEFORE", "IS_ORDERED_RIGHT_AFTER"),), result.aliases)
        self.assertEqual((), result.inverses)

        body = "## Claim\n\n### Formal Claim\n\n```python\n" + source + "```\n"
        row = _row(())
        row.update(_content_bytes=body.encode(), content_markdown=body)
        direct = registry_contribution(row)
        self.assertEqual(result, direct)


    def test_same_level_property_bearing_keeps_instance_inverse(self):
        source = """from anechoic.formal_claims import declare_relation
declare_relation(relation_name="IS_PROPERTY_OF", inverse_alias="HAS_PROPERTY",
    endpoint_pairs=(
        {"source_endpoint": {"level": "model_entities"}, "target_endpoint": {"level": "model_entities"}},
        {"source_endpoint": {"level": "instances"}, "target_endpoint": {"level": "instances"}},
    ))
"""
        result = registry_contribution(_native_row(source))
        self.assertEqual((("IS_PROPERTY_OF", "HAS_PROPERTY"),), result.inverses)
        self.assertEqual((), result.aliases)

        body = "## Claim\n\n### Formal Claim\n\n```python\n" + source + "```\n"
        row = _row(())
        row.update(_content_bytes=body.encode(), content_markdown=body)
        direct = registry_contribution(row)
        self.assertEqual(result, direct)



if __name__ == "__main__":
    unittest.main()
