import os
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    _package__shared import (
    load_boundary_model,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    normalize_claim,
    parse_workflow,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_MERMAID_RENDERER_C87.\
    _package__shared import (
    render_solution,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    DELEGATION_VERIFICATION_C89._package__shared import (
    check_child_outcome,
    check_cli_child_dispatch,
)
# fmt: on

from ._manifest_child_fixtures import (
    _cli_child,
    _manifest,
)

from ._manifest_child_validation_cases import ManifestValidationCases

from ...contracts.dispatch.test_cli_child_dispatch import _parent_workflow
from ...contracts.cli.test_cli_spec import _carrier
from ..delegation.test_trace_child_delegation import CONTRACT, PARENT

_PARENT = PARENT.replace(
    "'output': 'succeeded'",
    "'output': 'succeeded', 'manifest': 'AN-S-2@1', "
    "'interface': 'renderer', 'transport': 'in_process', "
    "'limit': {'at_most': 5}, 'path': 'rendered.svg'",
)
_CHILD = CONTRACT.replace(
    "action='render'",
    "action='render', interface='renderer', transport='in_process'",
).replace("'shown'),", "'shown', {'limit': 4, 'path': 'rendered.svg'}),")


class ManifestChildTests(ManifestValidationCases, unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which(
            "lean"
        )
        if self.lean is None:
            self.skipTest("Lean executable unavailable")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.parent = _manifest(
            self.root,
            "AN-S-1",
            "C00",
            "C1",
            CONTRACT.replace("action='render'", "action='run'"),
        )
        self.child = _manifest(
            self.root,
            "AN-S-2",
            "C1",
            "C2",
            _CHILD,
            {
                "io": {
                    "server": {
                        "renderer": {
                            "transport": "in_process",
                            "entry": "renderer.render",
                        }
                    }
                }
            },
        )
        self.solution = _carrier(
            self.root,
            "AN-S-3",
            "solution",
            "C1",
            "{ANSWERS: [AN-S-1@1]}",
            _PARENT,
        )

    def check(self):
        return check_child_outcome(
            self.root,
            self.solution,
            "C2",
            self.child,
            parent_manifest=self.parent,
            event="render",
            lean=self.lean,
        )

    def mutate(self, pin, before, after):
        path = self.root / pin["path"]
        original = path.read_text()
        self.assertIn(before, original)
        path.write_text(original.replace(before, after))
        return lambda: path.write_text(original)

    def test_parent_only_reads_the_child_manifest_and_renders_the_call(self):
        report = self.check()
        self.assertEqual("matched", report["status"])
        self.assertEqual({"caller", "manifest"}, report["sources"].keys())
        self.assertEqual({"caller_manifest"}, report["directions"].keys())
        self.assertEqual("AN-S-2", report["sources"]["manifest"]["atom_id"])
        self.assertTrue(report["sources"]["manifest"]["sha256"])
        model = load_boundary_model(
            self.root, "C1", self.parent, solution=self.solution
        )
        normalized, error = normalize_claim(
            "solution", model["solution"], "C1"
        )
        self.assertIsNone(error)
        diagram = render_solution(model, normalized)
        for label in ("C2", "render", "succeeded", "AN-S-2@1"):
            self.assertIn(label, diagram)
        self.assertEqual(3, len(list(self.root.glob("*.md"))))

    def test_repeated_event_preserves_json_value_types(self):
        source = _PARENT.split("```python\n", 1)[1].split("```", 1)[0]
        states = parse_workflow(source)["machine"]["states"]
        solution_path = self.root / self.solution["path"]
        original = solution_path.read_text()
        child_path = self.root / self.child["path"]
        child = child_path.read_text()
        for first, second, expected in (
            (True, True, "matched"),
            (True, 1, "unresolved"),
            (1, 1.0, "matched"),
        ):
            with self.subTest(first=first, second=second):
                opening = deepcopy(states["start"]["on"]["render"])
                closing = deepcopy(opening)
                opening["target"] = "again"
                opening["guard"]["params"]["detail"]["visible"] = first
                closing["guard"]["params"]["detail"]["visible"] = second
                machine = {
                    "id": "run",
                    "initial": "start",
                    "states": {
                        "start": {"on": {"render": opening}},
                        "again": {"on": {"render": closing}},
                        "done": states["done"],
                    },
                }
                replacement = (
                    "component_workflow(component='C1', action='run', "
                    f"machine={machine!r})\n"
                )
                solution_path.write_text(original.replace(source, replacement))
                child_path.write_text(
                    child.replace(
                        "'path': 'rendered.svg'",
                        f"'path': 'rendered.svg', 'visible': {first!r}",
                    )
                )
                self.assertEqual(expected, self.check()["status"])

    def test_legacy_child_contract_is_reported_as_unresolved(self):
        pin = _carrier(
            self.root,
            "AN-S-2",
            "component_manifest",
            "C1",
            "{}",
            """## Formal Manifest

```python
from anechoic.model import ComponentManifest
ComponentManifest(component_id='C2', name='Example')
```
""",
        )
        self.child = pin
        result = self.check()
        self.assertEqual("unresolved", result["status"], result)
        self.assertTrue(
            any(
                item["source"]["atom_id"] == "AN-S-2"
                and "embedded Contract" in item["message"]
                for item in result["unresolved"]
            )
        )

    def test_http_request_fields_follow_the_public_action(self):
        contract = (
            _CHILD.replace("python trace", "python contract")
            .replace("declare_trace_contract", "declare_http_contract")
            .replace(
                "transport='in_process'",
                "route='render', operation='POST /render', "
                "outcomes={'succeeded': (200, 'result')}, "
                "checks={'input_format': {'fields': ('format', 'input')}}",
            )
        )
        self.child = _manifest(
            self.root,
            "AN-S-2",
            "C1",
            "C2",
            contract,
            {
                "io": {
                    "server": {
                        "renderer": {
                            "transport": "http",
                            "routes": {"POST /render": "render"},
                        }
                    }
                }
            },
        )
        self.mutate(
            self.solution,
            "'transport': 'in_process'",
            "'transport': 'http', "
            "'route': 'render', 'operation': 'POST /render', "
            "'request_fields': ['input', 'format']",
        )
        self.assertEqual("matched", self.check()["status"])
        self.mutate(self.solution, "['input', 'format']", "['format']")
        self.assertEqual("conflicting", self.check()["status"])

    def test_cli_first_dispatch_binds_manifest_action_and_inputs(self):
        child = _cli_child(self)
        call = (
            "'target': 'C2', 'detail': {'manifest': '"
            "AN-S-2@1', 'action': 'run', "
            "'arguments': ['--name', '<value>']}"
        )
        workflow = _parent_workflow().replace("'target': 'C2'", call)
        unpinned = (
            "'invoking': {'on': {'unbound': {'target'"
            ": 'reporting', 'guard': {'type': 'matche"
            "sTrace', "
            "'params': {'kind': 'effect', 'target': 'C2'}}}, 'dispatch':"
        )
        solution = _carrier(
            self.root,
            "AN-S-3",
            "solution",
            "C1",
            "{ANSWERS: [AN-S-1@1]}",
            workflow,
        )
        self._assert_cli_dispatch_cases(solution, child, unpinned)

    def _assert_cli_dispatch_cases(self, solution, child, unpinned):
        for before, after, expected in (
            ("", "", "matched"),
            ("AN-S-2@1", "AN-S-2@2", "conflicting"),
            ("'action': 'run'", "'action': 'inspect'", "unresolved"),
            ("['--name', '<value>']", "['--other']", "conflicting"),
            ("'invoking': {'on': {'dispatch':", unpinned, "unresolved"),
        ):
            with self.subTest(before=before, after=after):
                restore = self.mutate(solution, before, after)
                try:
                    report = check_cli_child_dispatch(
                        self.root,
                        solution,
                        "C2",
                        child,
                        parent_manifest=self.parent,
                        interface="suite",
                        command="local",
                        lean=self.lean,
                    )
                    self.assertEqual(expected, report["status"])
                    self.assertEqual(
                        {"caller_manifest"}, report["directions"].keys()
                    )
                finally:
                    restore()
