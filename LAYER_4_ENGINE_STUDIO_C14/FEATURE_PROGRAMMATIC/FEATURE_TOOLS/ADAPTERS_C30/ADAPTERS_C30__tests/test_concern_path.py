import unittest

from ..concern_path__pub import parse_concern_path
from ..continuant_concern__pub import continuant_model_subject
from ..subject_notation__pub import (
    MembershipPredicate,
    SelectionSuffix,
    parse_subject_expression,
    render_subject,
)


class ConcernPathTests(unittest.TestCase):
    def test_approved_paths(self):
        for authored, canonical in (
            (
                "atom.state.status >| status group := current",
                "atom.state.status >| status group:=current",
            ),
            (
                "status group := current |< atom.state.status",
                "status group:=current |< atom.state.status",
            ),
            (
                "atom/(.state.status := current)//child.name",
                "atom/(.state.status:=current)//child.name",
            ),
            (
                "(atom.state.status >| status group := current)",
                "(atom.state.status >| status group:=current)",
            ),
            (
                "Atom//Spec Atom//.Header.Context",
                "Atom//Spec Atom//.Header.Context",
            ),
            (
                "Atom//Spec Atom//.Header.Context.Template := axiom",
                "Atom//Spec Atom//.Header.Context.Template:=axiom",
            ),
        ):
            with self.subTest(authored=authored):
                self.assertEqual(
                    render_subject(parse_concern_path(authored)), canonical
                )

    def test_membership_predicate(self):
        expression = parse_concern_path(
            "Module/Unit//(.Form in (function, method))"
        )
        predicate = expression.steps[-1].operand
        self.assertIsInstance(predicate, MembershipPredicate)
        self.assertEqual(predicate.property.value, "Form")
        self.assertEqual(
            [value.value for value in predicate.values], ["function", "method"]
        )
        canonical = "Module/Unit//(.Form in (function, method))"
        self.assertEqual(render_subject(expression), canonical)
        self.assertEqual(
            render_subject(parse_concern_path(canonical)), canonical
        )
        self.assertEqual(
            render_subject(parse_concern_path("Module/Unit in service")),
            "Module/Unit in service",
        )
        for path in (
            "Module/Unit//(.Form in ())",
            "Module/Unit//(.Form in (function,))",
            "Module/Unit//(.Form in (function,function))",
            "Module/Unit//(.Form in (function)",
            "Module/Unit//(.Form in function)",
            "Module/Unit//(. in (function))",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                parse_concern_path(path)

    def test_specialization_scope_boundary(self):
        expression = parse_concern_path("Atom//Spec Atom//.Header.Context")
        self.assertEqual(
            [step.operator for step in expression.steps],
            ["//", "//", ".", "."],
        )
        self.assertIsInstance(expression.steps[1].operand, SelectionSuffix)
        self.assertEqual(expression.steps[1].operand.value, "")
        with self.assertRaises(ValueError):
            parse_subject_expression("Atom//Spec Atom//.Header.Context")
        self.assertEqual(
            render_subject(parse_subject_expression("Atom//")), "Atom//"
        )

    def test_rejects_other_subject_operators(self):
        for path in (
            "",
            "atom.state:current",
            "atom +> node",
            "atom <+ node",
            "atom[Text]",
            "atom{1}",
            "atom >|{1} node",
            "atom//",
            "atom/(a,b)",
            "Atom//.Header",
            "Atom//Spec Atom//.",
            "Atom//Spec Atom//",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                parse_concern_path(path)

    def test_continuant_tree_remains_strict(self):
        for path in (
            "Model/Graph >| Classification",
            "Model/Graph/(.Name:=x)",
            "Model/Graph.Name:=x",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                continuant_model_subject(
                    {
                        "subject": "Node",
                        "path": path,
                        "relation": "is_contained_by",
                    }
                )
