"""Native declarations retain the existing compilers' explicit inputs."""

import unittest

from ._compiler_property_cases import CompilerPropertyCases, _compile


from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.claim_compiler.compiler_claim import (  # noqa: E402
    compile_atom_dependencies_with_check,
    compiler_model_statements,
)
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import (  # noqa: E402
    compile_python_model_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    INSTANCE_CHECK,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (  # noqa: E402
    parse_native_model_claim,
)


class CompilerClaimTests(CompilerPropertyCases, unittest.TestCase):
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
        statements, check = compile_atom_dependencies_with_check(
            parse_native_model_claim(claim)
        )
        self.assertEqual(
            statements,
            (
                "Atom.Header.Context.Topics.Dependencies{::0..1} :: [string]{::0+}",
                "Atom.Header.Context.Topics.Dependencies.*[]{::0}",
            ),
        )
        self.assertEqual(check["name"], "dependencies_are_distinct")
        self.assertEqual(check["parameter_type"], "Atom")
        self.assertEqual(statements, compile_python_model_claim(claim))
        with self.assertRaisesRegex(
            ValueError, "typed Atom Dependencies validator"
        ):
            compile_atom_dependencies_with_check(
                parse_native_model_claim(
                    claim.replace(
                        'entity_name="Dependencies"', 'entity_name="Other"'
                    )
                )
            )
        with self.assertRaisesRegex(
            ValueError, "typed Atom Dependencies validator"
        ):
            compile_atom_dependencies_with_check(
                parse_native_model_claim(
                    claim.replace("dependencies_are_distinct", "other_check")
                )
            )

    def test_aspect_instance_compiles_exact_structure_facts(self):
        address = "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Query Processing"
        claim = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import Aspect\n"
            f"declare_entity(entity_name='Query Processing', instance=Aspect(address={address!r}))\n"
        )
        self.assertEqual(
            (address, f"({address}) ((INSTANCE_OF)) Aspect"), _compile(claim)
        )
        from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import (
            lint_python_model_claim,
        )

        self.assertEqual(
            (),
            lint_python_model_claim(
                claim,
                declared_addresses=["Aspect"],
                relation_names=[],
                python_class_bindings={"Aspect": ["Aspect"]},
            ),
        )
        invalid_claim = claim.replace("<+ Aspects <+", "<+ Invalid <+")
        self.assertTrue(
            lint_python_model_claim(
                invalid_claim,
                declared_addresses=["Aspect"],
                relation_names=[],
                python_class_bindings={"Aspect": ["Aspect"]},
            )
        )
        from copy import deepcopy

        parsed = parse_native_model_claim(claim)
        for invalid in (
            "Atom <+ Aspects <+ Query Processing",
            "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Other",
        ):
            modified = deepcopy(parsed)
            modified["arguments"]["instance"]["fields"]["address"] = invalid
            with self.assertRaisesRegex(
                ValueError, "invalid Aspect instance address"
            ):
                compiler_model_statements(modified)

    def test_allowed_axis_values_are_not_fixed_axes(self):
        claim = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Node", allowed_axis_values={"Container": ("yes", "no")})
"""
        self.assertEqual(
            ("Node >| Container: yes", "Node >| Container: no"),
            _compile(claim),
        )
        for bad in ('("yes", "yes")', "()", '["yes"]'):
            with self.assertRaises(ValueError):
                _compile(claim.replace('("yes", "no")', bad))
        with self.assertRaises(ValueError):
            _compile(
                claim.replace(
                    'entity_name="Node",',
                    'entity_name="Node", axes={"Container": "yes"},',
                )
            )

    def test_same_bearer_fallback_requires_a_declared_property(self):
        from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import (
            lint_python_model_claim,
        )

        claim = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Label", relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context", value_format=str, fallback_property_name="Form")
"""
        self.assertIn(
            "$atom.Header.Context.Label ?== $atom.Header.Context.Form",
            _compile(claim),
        )
        addresses = {
            "Atom.Header.Context",
            "Atom.Header.Context.Label",
            "Atom.Header.Context.Form",
        }
        relations = {"IS_PROPERTY_OF"}
        self.assertEqual(
            (),
            lint_python_model_claim(
                claim, declared_addresses=addresses, relation_names=relations
            ),
        )
        missing = addresses - {"Atom.Header.Context.Form"} | {
            "Other.Header.Context.Form"
        }
        diagnostics = lint_python_model_claim(
            claim, declared_addresses=missing, relation_names=relations
        )
        self.assertIn(
            "unknown declared fallback Property: Atom.Header.Context.Form",
            diagnostics[0],
        )

    def test_base_status_claim_preserves_values_and_order_numbers(self):
        claim = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Status", relation_name="IS_PROPERTY_OF", base_path="Atom.Header.State",
               property_occurrence_cardinality=1, value_format=str, value_cardinality=1,
               dependent_property_cardinality=0, allowed_values=("Draft", "Active", "Archived"),
               status_order_numbers={"Draft": 0, "Archived": 99})
"""
        self.assertEqual(
            (
                "Atom.Header.State.Status{::1} :: [string]{::1}",
                "Atom.Header.State.Status.*[]{::0}",
                "Atom.Header.State.Status :: Draft",
                "Atom.Header.State.Status :: Active",
                "Atom.Header.State.Status :: Archived",
                "Atom/(.Header.State.Status := Draft).Header.State.Status >| (Status Order Number == 0)",
                "Atom/(.Header.State.Status := Archived).Header.State.Status >| (Status Order Number == 99)",
            ),
            _compile(claim),
        )
        with self.assertRaisesRegex(
            ValueError, "invalid base Status Order Numbers"
        ):
            _compile(claim.replace('"Archived": 99', '"Archived": 0'))

    def test_projection_form_preserves_admitted_value_and_selector(self):
        claim = """from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class Map(Projection):
    pass

declare_entity(entity_class=Map, entity_name="Map", qualification_property_path="Projection.Form")
"""
        self.assertEqual(
            ("Projection.Form :: Map", "Projection/(.Form in (Map))"),
            _compile(claim),
        )
        with self.assertRaisesRegex(ValueError, "Projection as its sole base"):
            _compile(
                claim.replace("import Projection", "import Atom").replace(
                    "Map(Projection)", "Map(Atom)"
                )
            )

    def test_property_bearer_uses_a_qualified_model_path(self):
        def compile_property(base):
            return _compile(
                "from anechoic.formal_claims import declare_entity\n"
                f"declare_entity(entity_name='Mermaid Scheme', relation_name='IS_PROPERTY_OF', base_path={base!r})"
            )

        base = "Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Step).Content.Claim"
        self.assertEqual((f"{base}.Mermaid Scheme",), compile_property(base))
        self.assertEqual(
            ("Step.Content.Claim.Mermaid Scheme",),
            compile_property("Step.Content.Claim"),
        )
        for invalid in ("Atom//Step", f"{base};Injected", f"{base}{{::1}}"):
            with (
                self.subTest(invalid=invalid),
                self.assertRaisesRegex(
                    ValueError, "unsupported compiler name"
                ),
            ):
                compile_property(invalid)

    def test_unsafe_or_unsupported_compiler_values_fail(self):
        native = """
from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Name", relation_name="IS_PROPERTY_OF", base_path="Atom.Header;Other")
"""
        with self.assertRaisesRegex(ValueError, "unsupported compiler name"):
            _compile(native)

    def test_instance_check_cannot_be_silently_dropped(self):
        native = INSTANCE_CHECK
        parsed = parse_native_model_claim(native)
        self.assertEqual(
            "is_valid_atom", parsed["arguments"]["instance_check"]
        )
        with self.assertRaisesRegex(
            ValueError, "instance_check requires a typed validator"
        ):
            compiler_model_statements(parsed)

    def test_scope_level_schema_compiles_without_calling_its_check(self):
        claim = """from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

def check_structural_level(unit: ScopeUnit) -> bool:
    return unit.structural_level == 0

declare_entity(entity_name="structural_level", relation_name="IS_PROPERTY_OF",
               base_path="Scope Unit", property_occurrence_cardinality=1,
               value_format=int, value_cardinality=1, instance_check=check_structural_level)
"""
        self.assertEqual(
            ("Scope Unit.structural_level{::1} :: [int]{::1}",),
            compile_python_model_claim(claim),
        )
        with self.assertRaisesRegex(
            ValueError, "instance_check requires a typed validator"
        ):
            _compile(claim)


if __name__ == "__main__":
    unittest.main()
