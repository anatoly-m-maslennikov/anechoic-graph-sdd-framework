"""Native declarations retain the existing compilers' explicit inputs."""

from pathlib import Path
import unittest


FEATURE = Path(__file__).resolve().parents[1]
PROGRAMMATIC = FEATURE.parent
TOOLS = PROGRAMMATIC / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    RECURSIVE_CONTENT, ROLE_HEADER, INSTANCE_CHECK, HEADER_RELATIONS,
)
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.compiler_claim import compiler_model_statements  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.legacy_claim_compiler__pub import compile_python_model_claim, compile_atom_dependencies_claim_with_check  # noqa: E402


def _compile(source):
    return compiler_model_statements(parse_native_model_claim(source))


def _body(statements):
    return "## Claim\n\n### Formal Claim\n\n```CFEL\n" + ";\n".join(statements) + ";\n```\n"


def _row(statements):
    body = _body(statements)
    return {"id": "CA-R-1", "ref": "CA-R-1", "version": 1, "source_path": "source.md",
            "status_group": "Current", "role": "Requirement", "form": "Declaration",
            "_content_bytes": body.encode(), "content_markdown": body}


def _native_row(source, identifier="CA-R-1"):
    result = _row(())
    body = f"## Claim\n### Formal Claim\n```python\n{source}\n```\n"
    return result | {"id": identifier, "ref": identifier, "_content_bytes": body.encode(),
                     "content_markdown": body}


class CompilerClaimTests(unittest.TestCase):
    def test_explicit_atom_dependencies_consumer_keeps_callback_metadata(self):
        claim = """from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Atom

def dependencies_are_distinct(atom: Atom) -> bool:
    return len(atom.dependencies) == len(set(atom.dependencies))

declare_entity(entity_name="Dependencies", relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context.Topics",
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_format=str, value_cardinality=Cardinality(minimum=0, maximum=None),
    dependent_property_cardinality=0, instance_check=dependencies_are_distinct)
"""
        statements, check = compile_atom_dependencies_claim_with_check(claim)
        self.assertEqual(statements, (
            "Atom.Header.Context.Topics.Dependencies{::0..1} :: [string]{::0+}",
            "Atom.Header.Context.Topics.Dependencies.*[]{::0}",
        ))
        self.assertEqual(check["name"], "dependencies_are_distinct")
        self.assertEqual(check["parameter_type"], "Atom")
        self.assertEqual(statements, compile_python_model_claim(claim))
        with self.assertRaisesRegex(ValueError, "typed Atom Dependencies validator"):
            compile_atom_dependencies_claim_with_check(claim.replace('entity_name="Dependencies"', 'entity_name="Other"'))
        with self.assertRaisesRegex(ValueError, "typed Atom Dependencies validator"):
            compile_atom_dependencies_claim_with_check(claim.replace("dependencies_are_distinct", "other_check"))

    def test_aspect_instance_compiles_exact_structure_facts(self):
        address = "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Query Processing"
        claim = ("from anechoic.formal_claims import declare_entity\n"
                 "from anechoic.model import Aspect\n"
                 f"declare_entity(entity_name='Query Processing', instance=Aspect(address={address!r}))\n")
        self.assertEqual((address, f"({address}) ((IS_INSTANCE_OF)) Aspect"), _compile(claim))
        from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.lint_python_model_claim__pub import lint_python_model_claim
        self.assertEqual((), lint_python_model_claim(claim, declared_addresses=["Aspect"], relation_names=[], python_class_bindings={"Aspect": ["Aspect"]}))
        invalid_claim = claim.replace("<+ Aspects <+", "<+ Invalid <+")
        self.assertTrue(lint_python_model_claim(invalid_claim, declared_addresses=["Aspect"], relation_names=[], python_class_bindings={"Aspect": ["Aspect"]}))
        from copy import deepcopy
        parsed = parse_native_model_claim(claim)
        for invalid in ("Atom <+ Aspects <+ Query Processing", "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Other"):
            modified = deepcopy(parsed)
            modified["arguments"]["instance"]["fields"]["address"] = invalid
            with self.assertRaisesRegex(ValueError, "invalid Aspect instance address"):
                compiler_model_statements(modified)

    def test_allowed_classification_values_are_not_fixed_classifications(self):
        claim = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Node", allowed_classification_values={"Container": ("yes", "no")})
"""
        self.assertEqual(("Node >| Container: yes", "Node >| Container: no"), _compile(claim))
        for bad in ('("yes", "yes")', '()', '["yes"]'):
            with self.assertRaises(ValueError):
                _compile(claim.replace('("yes", "no")', bad))
        with self.assertRaises(ValueError):
            _compile(claim.replace('entity_name="Node",', 'entity_name="Node", classifications={"Container": "yes"},'))

    def test_same_bearer_fallback_requires_a_declared_property(self):
        from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.lint_python_model_claim__pub import lint_python_model_claim

        claim = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Label", relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context", value_format=str, fallback_property_name="Form")
"""
        self.assertIn("$atom.Header.Context.Label ?== $atom.Header.Context.Form", _compile(claim))
        addresses = {"Atom.Header.Context", "Atom.Header.Context.Label", "Atom.Header.Context.Form"}
        relations = {"IS_PROPERTY_OF"}
        self.assertEqual((), lint_python_model_claim(claim, declared_addresses=addresses, relation_names=relations))
        missing = addresses - {"Atom.Header.Context.Form"} | {"Other.Header.Context.Form"}
        diagnostics = lint_python_model_claim(claim, declared_addresses=missing, relation_names=relations)
        self.assertIn("unknown declared fallback Property: Atom.Header.Context.Form", diagnostics[0])

    def test_base_status_claim_preserves_values_and_order_numbers(self):
        claim = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Status", relation_name="IS_PROPERTY_OF", base_path="Atom.Header.State",
               property_occurrence_cardinality=1, value_format=str, value_cardinality=1,
               dependent_property_cardinality=0, allowed_values=("Draft", "Active", "Archived"),
               status_order_numbers={"Draft": 0, "Archived": 99})
"""
        self.assertEqual((
            "Atom.Header.State.Status{::1} :: [string]{::1}",
            "Atom.Header.State.Status.*[]{::0}",
            "Atom.Header.State.Status :: Draft",
            "Atom.Header.State.Status :: Active",
            "Atom.Header.State.Status :: Archived",
            "Atom/(.Header.State.Status := Draft).Header.State.Status >| (Status Order Number == 0)",
            "Atom/(.Header.State.Status := Archived).Header.State.Status >| (Status Order Number == 99)",
        ), _compile(claim))
        with self.assertRaisesRegex(ValueError, "invalid base Status Order Numbers"):
            _compile(claim.replace('"Archived": 99', '"Archived": 0'))

    def test_projection_form_preserves_admitted_value_and_selector(self):
        claim = """from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class Map(Projection):
    pass

declare_entity(entity_class=Map, entity_name="Map", qualification_property_path="Projection.Form")
"""
        self.assertEqual(("Projection.Form :: Map", "Projection/(.Form in (Map))"), _compile(claim))
        with self.assertRaisesRegex(ValueError, "Projection as its sole base"):
            _compile(claim.replace("import Projection", "import Atom").replace("Map(Projection)", "Map(Atom)"))

    def test_property_bearer_uses_a_qualified_model_path(self):
        def compile_property(base):
            return _compile(
                "from anechoic.formal_claims import declare_entity\n"
                f"declare_entity(entity_name='Mermaid Scheme', relation_name='IS_PROPERTY_OF', base_path={base!r})"
            )

        base = "Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Step).Content.Claim"
        self.assertEqual((f"{base}.Mermaid Scheme",), compile_property(base))
        self.assertEqual(("Step.Content.Claim.Mermaid Scheme",), compile_property("Step.Content.Claim"))
        for invalid in ("Atom//Step", f"{base};Injected", f"{base}{{::1}}"):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "unsupported compiler name"):
                compile_property(invalid)


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
        with self.assertRaisesRegex(ValueError, "invalid recursive_dependent_property_cardinality cardinality"):
            _compile(native.replace("recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None)",
                                    "recursive_dependent_property_cardinality=-1"))
        with self.assertRaisesRegex(ValueError, "name format requires cardinality"):
            _compile(native.replace("recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None),", ""))
        with self.assertRaisesRegex(ValueError, "must be acyclic"):
            _compile(native.replace('("Semantics", "Details")', '("Semantics", "Summary")'))
        with self.assertRaisesRegex(ValueError, "must name distinct allowed children"):
            _compile(native.replace('ordered_dependent_property_roles=(Requirement, Method, Evaluation, Delivery),',
                                    'allowed_dependent_property_names=("Summary", "Claim"),'))



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
            _compile(native.replace("    dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None)", ""))[-1],
        )
        bounded = native.replace("dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None)",
                                 "dependent_property_value_cardinality=Cardinality(minimum=1, maximum=2)")
        self.assertEqual("Atom.Header.Relations.* :: [string]{::1..2}", _compile(bounded)[-1])
        with self.assertRaisesRegex(ValueError, "invalid dependent_property_value_cardinality cardinality"):
            _compile(native.replace("dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None)",
                                    "dependent_property_value_cardinality=-1"))
        with self.assertRaisesRegex(ValueError, "requires a Property Declaration and value format"):
            _compile(native.replace("dependent_property_value_format=str,", ""))

    def test_nested_header_property_preserves_single_role(self):
        native = ROLE_HEADER
        with self.assertRaisesRegex(ValueError, "unsupported Property class selection"):
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


    def test_relation_classifications_compile_only_when_explicit(self):
        source = """from anechoic.formal_claims import declare_relation
declare_relation(relation_name="LINKS", inverse_alias="LINKED_BY",
    source_endpoint={"level": "model_entities"}, target_endpoint={"level": "model_entities"},
    classifications={"Direction": "Forward"}, inverse_classifications={"Direction": "Reverse"})
"""
        self.assertEqual(_compile(source), (
            "Relation//LINKS", "Relation//LINKED_BY ((IS_INVERSE_ALIAS_FOR)) Relation//LINKS",
            "Relation//LINKS >| Direction == Forward", "Relation//LINKED_BY >| Direction == Reverse",
        ))
        self.assertEqual(_compile(source.replace(',\n    classifications={"Direction": "Forward"}, inverse_classifications={"Direction": "Reverse"}', '')), (
            "Relation//LINKS", "Relation//LINKED_BY ((IS_INVERSE_ALIAS_FOR)) Relation//LINKS",
        ))

    def test_unsafe_or_unsupported_compiler_values_fail(self):
        native = '''
from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Name", relation_name="IS_PROPERTY_OF", base_path="Atom.Header;Other")
'''
        with self.assertRaisesRegex(ValueError, "unsupported compiler name"):
            _compile(native)

    def test_instance_check_cannot_be_silently_dropped(self):
        native = INSTANCE_CHECK
        parsed = parse_native_model_claim(native)
        self.assertEqual("is_valid_atom", parsed["arguments"]["instance_check"])
        with self.assertRaisesRegex(ValueError, "instance_check requires a typed validator"):
            compiler_model_statements(parsed)

    def test_scope_level_schema_compiles_without_calling_its_check(self):
        claim = '''from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

def check_structural_level(unit: ScopeUnit) -> bool:
    return unit.structural_level == 0

declare_entity(entity_name="structural_level", relation_name="IS_PROPERTY_OF",
               base_path="Scope Unit", property_occurrence_cardinality=1,
               value_format=int, value_cardinality=1, instance_check=check_structural_level)
'''
        self.assertEqual(
            ("Scope Unit.structural_level{::1} :: [int]{::1}",),
            compile_python_model_claim(claim),
        )
        with self.assertRaisesRegex(ValueError, "instance_check requires a typed validator"):
            _compile(claim)


if __name__ == "__main__":
    unittest.main()
