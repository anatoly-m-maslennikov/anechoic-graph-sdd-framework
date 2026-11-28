"""Native declarations retain the existing compilers' explicit inputs."""

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.claim_compiler.compiler_claim import (  # noqa: E402
    compiler_model_statements,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    HEADER_RELATIONS,
    RECURSIVE_CONTENT,
    ROLE_HEADER,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (  # noqa: E402
    parse_native_model_claim,
)


def _compile(source):
    return compiler_model_statements(parse_native_model_claim(source))


class CompilerPropertyCases:
    def test_recursive_content_and_role_scoped_ordering(self):
        native = RECURSIVE_CONTENT
        prefix = "Atom/(.Header.Context.Role in (Requirement, Method, Evaluation, Delivery)).Content"
        expected = (
            "Atom.Content{::1} :: []{::0}",
            "Atom.Content.*[string]{::0+}",
            "Atom.Content.**[string]{::0+}",
            "Atom.Content.** :: [markdown]",
            f"{prefix}.Summary ;> {prefix}.Claim",
            f"{prefix}.Claim ;> {prefix}.Semantics",
            f"{prefix}.Semantics ;> {prefix}.Details",
        )
        self.assertEqual(expected, _compile(native))
        self._reject_invalid_recursive_content(native)

    def _reject_invalid_recursive_content(self, native):
        with self.assertRaisesRegex(
            ValueError,
            "invalid recursive_dependent_property_cardinality cardinality",
        ):
            _compile(
                native.replace(
                    "recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None)",
                    "recursive_dependent_property_cardinality=-1",
                )
            )
        with self.assertRaisesRegex(
            ValueError, "name format requires cardinality"
        ):
            _compile(
                native.replace(
                    "recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None),",
                    "",
                )
            )
        with self.assertRaisesRegex(ValueError, "must be acyclic"):
            _compile(
                native.replace(
                    '("Semantics", "Details")', '("Semantics", "Summary")'
                )
            )
        with self.assertRaisesRegex(
            ValueError, "must name distinct allowed children"
        ):
            _compile(
                native.replace(
                    "ordered_dependent_property_roles=(Requirement, Method, Evaluation, Delivery),",
                    'allowed_dependent_property_names=("Summary", "Claim"),',
                )
            )

    def test_header_relations_child_value_cardinality(self):
        native = HEADER_RELATIONS
        expected = (
            "Atom.Header.Relations{::0..1} :: []{::0}",
            "Atom.Header.Relations.*[string]{::1+}",
            "Atom.Header.Relations.* :: [string]{::1+}",
        )
        self.assertEqual(expected, _compile(native))
        self.assertEqual(
            "Atom.Header.Relations.* :: [string]",
            _compile(
                native.replace(
                    "    dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None)",
                    "",
                )
            )[-1],
        )
        bounded = native.replace(
            "dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None)",
            "dependent_property_value_cardinality=Cardinality(minimum=1, maximum=2)",
        )
        self.assertEqual(
            "Atom.Header.Relations.* :: [string]{::1..2}",
            _compile(bounded)[-1],
        )
        with self.assertRaisesRegex(
            ValueError,
            "invalid dependent_property_value_cardinality cardinality",
        ):
            _compile(
                native.replace(
                    "dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None)",
                    "dependent_property_value_cardinality=-1",
                )
            )
        with self.assertRaisesRegex(
            ValueError, "requires a Property Declaration and value format"
        ):
            _compile(
                native.replace("dependent_property_value_format=str,", "")
            )

    def test_nested_header_property_preserves_single_role(self):
        native = ROLE_HEADER
        with self.assertRaisesRegex(
            ValueError, "unsupported Property class selection"
        ):
            _compile(native.replace("(Plan,)", "(Plan, Plan)"))

    def test_role_status_values_inherit_property_shape(self):
        native = """
from anechoic.formal_claims import declare_entity
from anechoic.model import Concern

declare_entity(
    entity_name="Status",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.State",
    applies_to_entity_classes=(Concern,),
    allowed_values=("Resolved", "Canceled"),
    status_order_numbers={"Resolved": 21},
)
"""
        self.assertEqual(
            (
                "Atom/(.Header.Context.Role in (Concern)).Header.State.Status :: Resolved",
                "Atom/(.Header.Context.Role in (Concern)).Header.State.Status :: Canceled",
                "Atom/(.Header.State.Status := Resolved).Header.State.Status >| (Status Order Number == 21)",
            ),
            _compile(native),
        )

    def test_relation_axes_compile_only_when_explicit(self):
        source = """from anechoic.formal_claims import declare_relation
declare_relation(relation_name="LINKS", inverse_alias="LINKED_BY",
    source_endpoint={"level": "model_entities"}, target_endpoint={"level": "model_entities"},
    axes={"Direction": "Forward"}, inverse_axes={"Direction": "Reverse"})
"""
        self.assertEqual(
            _compile(source),
            (
                "Relation//LINKS",
                "Relation//LINKED_BY ((IS_INVERSE_ALIAS_FOR)) Relation//LINKS",
                "Relation//LINKS >| Direction == Forward",
                "Relation//LINKED_BY >| Direction == Reverse",
            ),
        )
        self.assertEqual(
            _compile(
                source.replace(
                    ',\n    axes={"Direction": "Forward"}, inverse_axes={"Direction": "Reverse"}',
                    "",
                )
            ),
            (
                "Relation//LINKS",
                "Relation//LINKED_BY ((IS_INVERSE_ALIAS_FOR)) Relation//LINKS",
            ),
        )
