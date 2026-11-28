"""Framing action selection alongside workflow, Tool and Trace claims."""

import tempfile
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import (validate_declaration)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    check_cli_spec,
    check_tool_api_spec,
    check_trace_spec,
)  # fmt: skip

from ._direct_framing_observations import CONTRACT, SOLUTION
from ...contracts.cli.test_cli_spec import _SOLUTION
from ..chain.test_direct_manifest_chain import _manifest, _pins
from ...workflows.trace.test_trace_cases import FIRST as TRACE
from ...workflows.trace.test_trace_cases import SECOND as OTHER_TRACE
from ...workflows.trace.test_trace_cases import SOLUTION as TRACE_SOLUTION


def _cli_framing_pins(root, framing_first):
    boundaries = (
        "{'io': {'server': {'suite': {'transport': 'cli', "
        "'runner': 'uv', 'path': 'suite.py'}}}}"
    )
    cli = (
        "declare_cli_contract(interface='suite', action='run', "
        "outcomes={'succeeded': 'zero', 'failed': 'nonzero'})"
    )
    workflow = _SOLUTION.split("```")[1].replace(
        "component='C2'", "component='C15'"
    )
    manifest_framing = _manifest(
        "python framing", CONTRACT, boundaries=boundaries
    )
    manifest_cli = f"\n```python cli\n{cli}\n```\n"
    manifest = (
        manifest_framing + manifest_cli
        if framing_first
        else manifest_framing.replace(
            "\n```python framing",
            manifest_cli + "\n```python framing",
            1,
        )
    )
    pins = _pins(root, manifest, SOLUTION)
    path = root / pins[1]["path"]
    framing = path.read_text().replace("```python\n", "```python framing\n")
    workflow_fence = f"\n```{workflow}```\n"
    path.write_text(
        framing + workflow_fence
        if framing_first
        else framing.replace(
            "```python framing",
            workflow_fence + "```python framing",
            1,
        )
    )
    return pins


class FramingWorkflowCases:
    def test_whole_chain_framing_retains_other_modeled_io(self):
        boundaries = {
            "io": {
                "class_shapes": {
                    "Atom": {"fields": {"header": "Header"}},
                    "Plan": {"base": "Atom"},
                },
                "server": {
                    "invoke": {
                        "outcomes": {
                            "succeeded": {
                                "must_effect": [("parser", "called")]
                            }
                        }
                    }
                },
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(
                root,
                _manifest(
                    "python framing", CONTRACT, boundaries=repr(boundaries)
                ),
                SOLUTION,
            )
            path = root / pins[1]["path"]
            path.write_text(
                path.read_text().replace("```python\n", "```python framing\n")
            )
            report = verify_formal_chain(root, "C15", *pins, lean=self.lean)
        self.assertEqual("bounded_match", report["status"], report)
        self.assertIn(
            "boundaries.io",
            {
                gap["field"]
                for gap in report["translation"]["coverage_unresolved"]
            },
        )

    def test_mixed_manifest_and_solution_select_independent_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _cli_framing_pins(root, framing_first=True)
            report = validate_declaration(root, "C15", "manifest", pins[0])
            self.assertFalse(
                any(
                    item["field"] == "contract"
                    for item in report["unresolved"]
                ),
                report,
            )
            framing = verify_formal_chain(
                root, "C15", *pins, action="framing", lean=self.lean
            )
            self.assertEqual("bounded_match", framing["status"], framing)
            cli = verify_formal_chain(
                root, "C15", *pins, action="run", lean=self.lean
            )
            self.assertEqual(
                "matched",
                cli["directions"]["manifest_solution"]["status"],
                cli,
            )
            unselected = verify_formal_chain(
                root, "C15", *pins, lean=self.lean
            )
            self.assertEqual("incomplete", unselected["outcome"])

    def test_direct_cli_selects_workflow_in_both_fence_orders(self):
        for framing_first in (True, False):
            with (
                self.subTest(framing_first=framing_first),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                pins = _cli_framing_pins(root, framing_first)
                report = check_cli_spec(
                    root,
                    "C15",
                    *pins,
                    interface="suite",
                    action="run",
                    lean=self.lean,
                )
                self.assertEqual(
                    "matched",
                    report["directions"]["manifest_solution"]["status"],
                    report,
                )
                self.assertIn("stateDiagram-v2", report["mermaid"])

    def test_direct_trace_and_tool_select_workflow(self):
        tool = (
            "declare_tool_api_contract(operation='POST /tools', "
            "outcomes={'success': (200, 'result'), "
            "'invalid_input': (400, 'typed_error'), "
            "'internal_error': (500, 'typed_error')})"
        )
        for language, claim, check in (
            ("python trace", TRACE, check_trace_spec),
            ("python contract", tool, check_tool_api_spec),
        ):
            with (
                self.subTest(language=language),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                manifest = (
                    _manifest("python framing", CONTRACT)
                    + f"\n```{language}\n{claim}\n```\n"
                )
                pins = _pins(root, manifest, SOLUTION)
                path = root / pins[1]["path"]
                framing = path.read_text().replace(
                    "```python\n", "```python framing\n"
                )
                path.write_text(
                    framing + f"\n```python\n{TRACE_SOLUTION}\n```\n"
                )
                report = check(
                    root, "C15", *pins, action="compile", lean=self.lean
                )
                self.assertIn("stateDiagram-v2", report["mermaid"])

    # fmt: off
    def \
    test_framing_selection_rejects_reserved_workflow_name_in_either_carrier(
        self,
    ):
        # fmt: on
        cases = (("contract", False), ("contract", True), ("solution", False))
        for role, repeated in cases:
            with (
                self.subTest(role=role, repeated=repeated),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                trace, workflow = TRACE, TRACE_SOLUTION
                if role == "contract":
                    trace = trace.replace(
                        "action='compile'", "action='framing'"
                    )
                else:
                    workflow = workflow.replace(
                        "action='compile'", "action='framing'"
                    )
                manifest = _manifest("python framing", CONTRACT)
                manifest += f"\n```python trace\n{trace}\n```\n"
                if repeated:
                    other = OTHER_TRACE.replace(
                        "action='compile'", "action='framing'"
                    )
                    manifest += f"\n```python trace\n{other}\n```\n"
                pins = _pins(root, manifest, SOLUTION)
                path = root / pins[1]["path"]
                framing = path.read_text().replace(
                    "```python\n", "```python framing\n"
                )
                path.write_text(framing + f"\n```python\n{workflow}\n```\n")
                result = verify_formal_chain(
                    root, "C15", *pins, action="framing", lean=self.lean
                )
                self.assertEqual("incomplete", result["outcome"])
                (diagnostic,) = result["diagnostics"]
                self.assertIn("'framing' is reserved", diagnostic["message"])
                self.assertEqual(role, diagnostic["role"])
                pin = pins[1] if role == "solution" else pins[0]
                self.assertEqual(pin["path"], diagnostic["source"]["path"])
