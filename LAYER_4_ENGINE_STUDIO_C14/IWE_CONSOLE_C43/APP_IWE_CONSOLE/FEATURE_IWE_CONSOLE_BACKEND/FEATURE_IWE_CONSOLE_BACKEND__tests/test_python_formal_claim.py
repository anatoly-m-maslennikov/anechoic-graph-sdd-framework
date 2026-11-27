"""Parity for Python Formal Claims at the shared compiler entry point."""

from pathlib import Path
import unittest
from unittest.mock import patch


from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.\
    FEATURE_FORMAL_MODEL_ENGINE__shared \
    import formal_claim_blocks  # fmt: skip
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    compile_content_schema,
    compile_relation_registry,
    declaration_statements,
)

PROGRAMMATIC = Path(__file__).resolve().parents[4] / "FEATURE_PROGRAMMATIC"


def declaration(language, claim):
    body = f"## Claim\n\n### Formal Claim\n\n```{language}\n{claim}\n```\n"
    return {
        "id": "CA-R-2500",
        "ref": "CA-R-2500",
        "version": 6,
        "source_path": "claim.md",
        "role": "Requirement",
        "form": "Declaration",
        "status_group": "Current",
        "_content_bytes": body.encode(),
    }


class PythonFormalClaimTest(unittest.TestCase):
    def test_native_property_reaches_content_compiler(self):
        python = (
            "from anechoic.formal_claims import Cardinality, declare_entity\n"
            'declare_entity(entity_name="Semantics", relation_name="IS_PROPERTY_OF", '
            'base_path="Atom.Content", value_format="markdown", '
            "value_cardinality=Cardinality(minimum=0, maximum=1))"
        )
        schema = compile_content_schema([declaration("python", python)])
        self.assertEqual(("content.semantics",), schema.names)

    def test_content_schema_keeps_constraints_and_source(self):
        prefix = "Atom/(.Header.Context.Role in RMED).Content.Claim"
        python = (
            f'property_rule(address={prefix!r}, value_format="", occurrences="1", values="0")\n'
            f'allowed_children(address={prefix!r}, names=("Formal Claim", "Prose Claim"), '
            'occurrences="1..2", name_format="string")'
        )
        schema = compile_content_schema([declaration("python", python)])
        self.assertEqual(
            [(("claim",), False), (("claim", "*"), True)],
            [(rule.path, rule.value_bearing) for rule in schema.rules],
        )
        roles = {"Requirement", "Method", "Evaluation", "Delivery"}
        self.assertEqual([roles, roles], [rule.roles for rule in schema.rules])
        self.assertEqual(
            [
                {
                    "reference": "CA-R-2500",
                    "version": 6,
                    "source_path": "claim.md",
                }
            ],
            [source.asset() for source in schema.sources],
        )

    def test_relation_inverse_is_visible_to_registry(self):
        native = (
            "from anechoic.formal_claims import declare_relation\n"
            'declare_relation(relation_name="PRECEDES", inverse_alias="FOLLOWS", '
            'source_endpoint={"level": "instances"}, target_endpoint={"level": "instances"})'
        )
        python = (
            'relation(source="Relation//PRECEDES", name="HAS_INVERSE", '
            'target="Relation//FOLLOWS")'
        )
        baseline = compile_relation_registry([declaration("python", native)])
        self.assertEqual(baseline.inverse, {"PRECEDES": "FOLLOWS"})
        self.assertEqual(
            baseline,
            compile_relation_registry([declaration("python", python)]),
        )

    def test_native_relation_registry_uses_endpoint_contract_without_translation(
        self,
    ):
        claim = (
            "from anechoic.formal_claims import declare_relation\n"
            'declare_relation(relation_name="PRECEDES", inverse_alias="FOLLOWS", '
            'source_endpoint={"level": %r}, target_endpoint={"level": %r})'
        )
        with patch(
            (
                "FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.legacy_claim"
                "_compiler__pub.compile_python_model_claim"
            ),
            side_effect=AssertionError,
        ):
            instances = compile_relation_registry(
                [declaration("python", claim % ("instances", "instances"))]
            )
            model = compile_relation_registry(
                [
                    declaration(
                        "python", claim % ("model_entities", "model_entities")
                    )
                ]
            )
        self.assertEqual(instances.inverse, {"PRECEDES": "FOLLOWS"})
        self.assertEqual(model.aliases, {"FOLLOWS": "PRECEDES"})
        self.assertEqual(model.names, {"PRECEDES"})

    def test_python_example_in_prose_is_not_a_model_claim(self):
        self.assertEqual(
            (),
            formal_claim_blocks(
                "## Claim\n### Prose Claim\n```python\nprint(1)\n```\n"
            ),
        )

    def test_legacy_fence_does_not_supply_model_statements(self):
        body = (
            "## Claim\n### Formal Claim\n```CFEL\nAtom.Content.Legacy[string];\n```\n"
            '```python\nproperty_rule(address="Atom.Content.Summary", value_format="markdown")\n```\n'
        )
        self.assertEqual(
            ("Atom.Content.Summary:: [markdown]",), formal_claim_blocks(body)
        )

    def test_accepted_empty_block_preserves_following_statements(self):
        claim = (
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="Example")'
        )
        row = declaration("python", claim)
        self.assertEqual(
            ("",), formal_claim_blocks(row["_content_bytes"].decode())
        )
        self.assertEqual([], list(declaration_statements(row)))
        mixed = row["_content_bytes"] + (
            b'```python\nproperty_rule(address="Atom.Content.Summary", value_format="markdown")\n```\n'
        )
        self.assertEqual(
            ("", "Atom.Content.Summary:: [markdown]"),
            formal_claim_blocks(mixed.decode()),
        )

    def test_python_compiler_preserves_quoted_delimiters_and_statement_ordering(
        self,
    ):
        literal = r'"a#b; c\"#d"'
        python = (
            f'set_value(address="Thing.Value", value={literal!r})  # not a value\n'
            'order_before(first="Thing", second="Other")'
        )
        statements = declaration_statements(declaration("python", python))
        self.assertEqual(
            [f"Thing.Value == {literal}", "Thing ;> Other"],
            [statement for statement, _source in statements],
        )
