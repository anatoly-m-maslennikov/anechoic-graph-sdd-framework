import json
import unittest
from contextlib import nullcontext
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from ...LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    _package__shared \
    import load_boundary_model  # fmt: skip
from .test_boundary_model import _inputs

_SPEC_PACKAGE = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75"
_COMPARISON_PACKAGE = (
    f"{_SPEC_PACKAGE}.LAYER_2_FORMAL_SPECIFICATION_C94."
    "LAYER_4_SPEC_COMPARISON_C88"
)


def _validation_contexts(model, claims):
    declarations = [
        [{"source": model[role]["source"], "claim": value}]
        for role, value in claims.items()
    ]
    captured = {
        "program": "lean source\n",
        "stdout": json.dumps([[declarations, [], None]]),
    }
    return nullcontext([captured]), nullcontext([])


def _render_before_comparing(profile, module, comparison, events):
    language = f"python {profile}"
    solution = "python" if profile == "trace" else language
    model = {
        role: {"source": {"atom_id": role}}
        for role in ("manifest", "contract", "solution")
    }
    model["contract"]["claims"] = [(language, "")]
    model["solution"]["claims"] = [(solution, "")]
    claims = {role: {} for role in model}
    validated = dict(status="matched", claims=claims, issues=[], unresolved=[])
    contexts = _validation_contexts(model, claims)
    compiled = {"lean": "lean source", **validated}
    return _observe_comparison(
        profile,
        module,
        comparison,
        events,
        model,
        validated,
        contexts,
        compiled,
    )


def _observe_comparison(
    profile, module, comparison, events, model, validated, contexts, compiled
):
    chain = import_module(f"{_SPEC_PACKAGE}.formal_chain__pub")
    provider = import_module(f"{_COMPARISON_PACKAGE}.{module}")
    entry_name = f"compare_{profile}_spec"
    directions = {
        role: {"status": "matched", "facts": []}
        for role in (
            "manifest_contract",
            "manifest_solution",
            "contract_solution",
        )
    }

    def validate(*args, **kwargs):
        events.append("validation")
        return validated

    def render(*args, **kwargs):
        events.append("render")
        return "diagram"

    def enter(*args, **kwargs):
        events.append("comparison entry")
        return getattr(provider, entry_name)(*args, **kwargs)

    def compare(*args, **kwargs):
        events.append("compare")
        if profile == "trace":
            return directions
        return dict(status="matched", directions=directions, sources=args[0])

    operations = dict(
        load_boundary_model=Mock(return_value=model),
        capture_lean_json=Mock(side_effect=contexts),
        compile_lean=Mock(return_value=compiled),
        validate_translation=validate,
        render_solution=render,
    )
    with (
        patch.multiple(chain, **operations, **{entry_name: enter}),
        patch.object(
            provider,
            "render_solution",
            side_effect=AssertionError("rendered twice"),
        ),
        patch.object(provider, comparison, side_effect=compare),
    ):
        return verify_formal_chain(".", "C7", {}, {}, {})


class FormalChainRegressions(unittest.TestCase):
    def test_failed_translation_does_not_render_or_compare(self):
        base = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75"
        translation = {
            "status": "unresolved",
            "issues": [],
            "unresolved": [],
            "claims": {},
        }
        with (
            patch(
                f"{base}.formal_chain__pub.load_boundary_model",
                return_value={},
            ),
            patch(
                f"{base}.formal_chain__pub.compile_lean",
                return_value={"lean": "lean source"},
            ),
            patch(
                f"{base}.formal_chain__pub.validate_translation",
                return_value=translation,
            ),
            patch(f"{base}.formal_chain__pub.render_solution") as render,
            patch(f"{base}.formal_chain__pub.compare_trace_spec") as trace,
            patch(f"{base}.formal_chain__pub.compare_shape_spec") as shape,
        ):
            result = verify_formal_chain(".", "C7", {}, {}, {})
        self.assertEqual("incomplete", result["outcome"])
        render.assert_not_called()
        trace.assert_not_called()
        shape.assert_not_called()

    def test_render_after_validation_before_comparison(self):
        for profile, module, comparison in (
            ("trace", "trace_spec__pub", "_profile_directions"),
            ("shape", "shape_spec__pub", "compare_obligations"),
        ):
            with self.subTest(profile=profile):
                events = []
                result = _render_before_comparing(
                    profile, module, comparison, events
                )
                self.assertEqual(
                    ["validation", "render", "comparison entry", "compare"],
                    events,
                )
                self.assertEqual("diagram", result["mermaid"])
                self.assertEqual("compared", result["outcome"])

    def test_invalid_source_diagnostics_preserve_role_pin_and_field(self):
        for role, index in (("manifest", 0), ("contract", 1), ("solution", 2)):
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                pins = _inputs(root)
                path = root / pins[index]["path"]
                text = path.read_text()
                path.write_text(
                    text.replace("relations:\n", "relations: invalid\n# ", 1)
                )
                result = verify_formal_chain(root, "C7", *pins)
                diagnostic = result["diagnostics"][0]
                self.assertEqual("incomplete", result["outcome"])
                self.assertEqual(role, diagnostic["role"])
                self.assertEqual(pins[index], diagnostic["source"])
                self.assertEqual("relations", diagnostic["field"])
                self.assertIn("Header relations", diagnostic["message"])
                with self.assertRaises(ValueError):
                    load_boundary_model(root, "C7", *pins)

    def test_invalid_claim_heading_reports_source(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _inputs(root)
            path = root / pins[2]["path"]
            path.write_text(path.read_text() + "\n## 🧪\n")
            result = verify_formal_chain(root, "C7", *pins)
        self.assertEqual("incomplete", result["outcome"])
        (diagnostic,) = result["diagnostics"]
        self.assertEqual(
            ("solution", "claim"), (diagnostic["role"], diagnostic["field"])
        )
        self.assertEqual(pins[2]["path"], diagnostic["source"]["path"])
        self.assertIn("sha256", diagnostic["source"])

    def test_explicit_empty_diagram_is_not_rendered_again(self):
        base = _COMPARISON_PACKAGE
        model = {
            role: {"source": {}}
            for role in ("manifest", "contract", "solution")
        }
        model["contract"]["claims"] = []
        compiled = {"claims": {}, "issues": [], "unresolved": [], "lean": ""}
        directions = {
            role: {"status": "matched", "facts": []}
            for role in (
                "manifest_contract",
                "manifest_solution",
                "contract_solution",
            )
        }
        for module, method, comparison in (
            ("trace_spec__pub", "compare_trace_spec", "_profile_directions"),
            ("shape_spec__pub", "compare_shape_spec", "compare_obligations"),
        ):
            with (
                self.subTest(module=module),
                patch(
                    f"{base}.{module}.render_solution",
                    side_effect=AssertionError("rendered twice"),
                ),
                patch(
                    f"{base}.{module}.{comparison}",
                    return_value=(
                        directions
                        if method == "compare_trace_spec"
                        else {"status": "matched", "directions": directions}
                    ),
                ),
            ):
                result = getattr(import_module(f"{base}.{module}"), method)(
                    model, compiled, mermaid=None
                )
                self.assertIsNone(result["mermaid"])

    def test_missing_links_identify_the_source_and_relation(self):
        for role, index, relation in (
            ("contract", 1, "ANSWERS"),
            ("solution", 2, "IS_SOLUTION_FOR"),
        ):
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                pins = _inputs(root)
                path = root / pins[index]["path"]
                path.write_text(
                    path.read_text().replace(f"{relation}:", "OTHER:")
                )
                result = verify_formal_chain(root, "C7", *pins)
                diagnostic = result["diagnostics"][0]
                self.assertEqual("incomplete", result["outcome"])
                self.assertEqual(role, diagnostic["role"])
                self.assertEqual(
                    pins[index],
                    {key: diagnostic["source"][key] for key in pins[index]},
                )
                self.assertEqual(f"relations.{relation}", diagnostic["field"])
                self.assertIn(
                    f"missing exact {relation}", diagnostic["message"]
                )

    def test_invalid_pin_and_missing_file_have_source_context(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _inputs(root)
            pins[1]["version"] = False
            diagnostic = verify_formal_chain(root, "C7", *pins)["diagnostics"][
                0
            ]
            self.assertEqual(
                ("contract", pins[1], "source_pin"),
                (
                    diagnostic["role"],
                    diagnostic["source"],
                    diagnostic["field"],
                ),
            )
            pins[1]["version"] = 1
            (root / pins[2]["path"]).unlink()
            diagnostic = verify_formal_chain(root, "C7", *pins)["diagnostics"][
                0
            ]
            self.assertEqual(
                ("solution", pins[2], "path"),
                (
                    diagnostic["role"],
                    diagnostic["source"],
                    diagnostic["field"],
                ),
            )
