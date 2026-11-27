import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83._package__shared \
    import recognized_claim  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88._package__shared \
    import check_shape_spec  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import parse_shape  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import validate_manifest  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)

LEAN = (
    os.environ.get("ANECHOIC_TEST_LEAN")
    or os.environ.get("LEAN_BIN")
    or "lean"
)
CONTRACT = (
    "declare_shape_contract(record='Atom', "
    "fields={'header':'Header','content':'Content'}, subtype='Plan')"
)
SOLUTION = (
    "class Atom:\n    header: Header\n    content: Content\n\nclass "
    "Plan(Atom):\n    pass\n"
)


def model(solution=SOLUTION, contract=CONTRACT):
    return {
        "component_id": "C52",
        "manifest": {
            "source": {"atom_id": "M"},
            "fields": {"component_id": "C52", "name": "Core"},
            "boundaries": None,
        },
        "contract": {
            "source": {"atom_id": "C"},
            "claims": [("python shape", contract)],
        },
        "solution": {
            "source": {"atom_id": "S"},
            "claims": [("python shape", solution)],
        },
    }


class ShapeSpecTests(unittest.TestCase):
    def check(self, solution, contract=CONTRACT):
        with patch(
            (
                "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICA"
                "TION_C94.LAYER_2_SPEC_READING_C83._package__shared.load_bound"
                "ary_model"
            ),
            return_value=model(solution, contract),
        ):
            return check_shape_spec(".", "C52", {}, {}, {}, lean=LEAN)

    def test_mermaid_labels_preserve_admitted_reserved_class_names(self):
        contract = CONTRACT.replace("Atom", "note").replace("Plan", "link")
        solution = SOLUTION.replace("Atom", "note").replace("Plan", "link")
        result = self.check(solution, contract)
        self.assertEqual(
            "matched", result["directions"]["contract_solution"]["status"]
        )
        self.assertEqual(
            result["mermaid"],
            'classDiagram\n    class ShapeRecord["note"] {\n        Header header\n'
            '        Content content\n    }\n    class ShapeSubtype["link"]\n'
            "    ShapeRecord <|-- ShapeSubtype",
        )

    def test_real_lean_and_observed_conflicts(self):
        result = self.check(SOLUTION)
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(
            "matched", result["directions"]["contract_solution"]["status"]
        )
        self.assertEqual(
            result["mermaid"],
            'classDiagram\n    class ShapeRecord["Atom"] {\n        Header header\n'
            '        Content content\n    }\n    class ShapeSubtype["Plan"]\n'
            "    ShapeRecord <|-- ShapeSubtype",
        )
        self.assertIn("«f_header» : «T_Header»", result["lean"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Shape.lean"
            path.write_text(result["lean"])
            checked = subprocess.run(
                [LEAN, str(path)],
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
            self.assertEqual(
                0, checked.returncode, checked.stdout + checked.stderr
            )
        for changed in (
            SOLUTION.replace("    header: Header\n", ""),
            SOLUTION.replace("header: Header", "header: Other"),
            SOLUTION.replace("Plan(Atom)", "Plan"),
        ):
            with self.subTest(changed=changed):
                self.assertEqual(
                    "conflicting",
                    self.check(changed)["directions"]["contract_solution"][
                        "status"
                    ],
                )

    def test_manifest_shape_chain_and_invalid_declarations(self):
        boundary = model()
        classes = {
            "Atom": {"fields": {"header": "Header", "content": "Content"}},
            "Plan": {"base": "Atom"},
        }
        io = {"server": {"bundled_model_classes": {"classes": classes}}}
        boundary["manifest"]["boundaries"] = {"io": io}
        boundary["manifest"]["fields"]["boundaries"] = boundary["manifest"][
            "boundaries"
        ]
        with patch(
            (
                "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.load_b"
                "oundary_model"
            ),
            return_value=boundary,
        ):
            result = verify_formal_chain(".", "C52", {}, {}, {}, lean=LEAN)
            self.assertEqual("compared", result["outcome"])
            self.assertEqual("matched", result["status"])
            for direction in result["directions"].values():
                self.assertEqual("matched", direction["status"])
            classes["Atom"]["fields"]["header"] = "Other"
            result = verify_formal_chain(".", "C52", {}, {}, {}, lean=LEAN)
            self.assertEqual(
                "conflicting",
                result["directions"]["manifest_contract"]["status"],
            )
            self.assertEqual(
                "conflicting",
                result["directions"]["manifest_solution"]["status"],
            )
            self.assertEqual(
                "matched", result["directions"]["contract_solution"]["status"]
            )
        classes["Atom"]["extra"] = 1
        self.assertTrue(validate_manifest(boundary["manifest"])["issues"])
        del classes["Atom"]["extra"]
        io["server"]["unknown"] = {}
        self.assertTrue(validate_manifest(boundary["manifest"])["unresolved"])

    def test_shape_comparison_reports_unresolved_state(self):
        boundary = model()
        classes = {
            "Atom": {"fields": {"header": "Header", "content": "Content"}},
            "Plan": {"base": "Atom"},
        }
        boundaries = {
            "io": {"server": {"bundled_model_classes": {"classes": classes}}},
            "state": {"reads": ["archive"], "writes": []},
        }
        boundary["manifest"]["boundaries"] = boundary["manifest"]["fields"][
            "boundaries"
        ] = boundaries
        with patch(
            (
                "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICA"
                "TION_C94.LAYER_2_SPEC_READING_C83._package__shared.load_bound"
                "ary_model"
            ),
            return_value=boundary,
        ):
            result = check_shape_spec(".", "C52", {}, {}, {}, lean=LEAN)
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(
            "matched", result["directions"]["contract_solution"]["status"]
        )
        self.assertIn(
            "boundaries.state", {gap["field"] for gap in result["unresolved"]}
        )

    def test_generated_names_do_not_collide(self):
        for name in ("mk", "rec", "toR_Atom", "T_Header", "f_mk"):
            contract = (
                "declare_shape_contract(record='Atom', fields={'"
                f"{name}"
                "':'Header'}, subtype='Plan')"
            )
            solution = (
                "class Atom:\n    "
                f"{name}"
                ": Header\n\nclass Plan(Atom):\n    pass\n"
            )
            boundary = model(solution)
            boundary["contract"]["claims"] = [("python shape", contract)]
            with (
                self.subTest(name=name),
                patch(
                    (
                        "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_S"
                        "PECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__s"
                        "hared.load_boundary_model"
                    ),
                    return_value=boundary,
                ),
            ):
                result = check_shape_spec(".", "C52", {}, {}, {}, lean=LEAN)
                self.assertEqual(
                    "matched",
                    result["directions"]["contract_solution"]["status"],
                )
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "Shape.lean"
                    path.write_text(result["lean"])
                    checked = subprocess.run(
                        [LEAN, str(path)],
                        capture_output=True,
                        text=True,
                        timeout=45,
                        check=False,
                    )
                    self.assertEqual(
                        0, checked.returncode, checked.stdout + checked.stderr
                    )

    def test_rejects_executable_and_duplicate_syntax(self):
        self.assertTrue(recognized_claim("solution", "python shape", SOLUTION))
        for role, source in (
            ("solution", SOLUTION.replace("Plan(Atom)", "Plan(Unknown)")),
            ("solution", SOLUTION.replace("    pass", "    print(1)")),
            (
                "solution",
                SOLUTION.replace(
                    "    content: Content", "    header: Content"
                ),
            ),
            ("solution", SOLUTION + "\nprint(1)"),
            (
                "contract",
                CONTRACT.replace("'content':'Content'", "'header':'Content'"),
            ),
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_shape(source, role)
