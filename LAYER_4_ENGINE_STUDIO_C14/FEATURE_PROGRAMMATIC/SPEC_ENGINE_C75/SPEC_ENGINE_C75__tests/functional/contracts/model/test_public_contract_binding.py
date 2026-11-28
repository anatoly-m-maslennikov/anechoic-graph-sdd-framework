import os
import shutil
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    normalize_claim,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import _binding_directions  # fmt: skip


CLI = (
    "declare_cli_contract(interface='command_line', action='run', "
    "command='build', "
    "arguments=('--project',), outcomes={'done': 'zero'})"
)
IN_PROCESS = (
    "declare_trace_contract(interface='worker', action='run', "
    "transport='in_process', "
    "cases={'done': {}})"
)


def normalize(*claims, public=True):
    return normalize_claim(
        "contract", {"claims": claims, "public": public}, "C1"
    )


def _trigger_workflow(detail):
    expect = {"kind": "trigger", "target": "worker", "detail": detail}
    return {
        "initial": "start",
        "states": [{"name": "start", "transitions": [{"expect": expect}]}],
    }


class PublicContractBindingTests(unittest.TestCase):
    def test_embedded_contract_accepts_public_cli_and_in_process_bindings(
        self,
    ):
        model, error = normalize(
            ("python cli", CLI),
            (
                "python trace",
                IN_PROCESS.replace("action='run'", "action='submit'"),
            ),
        )
        self.assertIsNone(error)
        self.assertEqual(
            {
                "interface": "command_line",
                "action": "run",
                "command": "build",
                "transport": "cli",
                "arguments": ["--project"],
                "outcomes": {"done": "zero"},
            },
            model["operations"]["run"],
        )
        self.assertEqual("worker", model["operations"]["submit"]["interface"])
        self.assertNotIn("entry", model["operations"]["submit"])

    def test_embedded_contract_rejects_implementation_bindings(self):
        for language, source, binding in (
            ("python cli", CLI, "runner='uv', path='run.py'"),
            ("python cli", CLI, "runner='uv', module='engine.run'"),
            ("python cli", CLI, "subcommands={'build': 'C2'}"),
            ("python trace", IN_PROCESS, "entry='worker.run'"),
        ):
            with self.subTest(binding=binding):
                _, error = normalize((language, f"{source[:-1]}, {binding})"))
                self.assertIsNotNone(error)
        for language, source in (
            ("python cli", CLI),
            ("python trace", IN_PROCESS),
        ):
            with self.subTest(language=language):
                _, error = normalize((language, source), public=False)
                self.assertIsNotNone(error)

    def test_manifest_entry_is_checked_against_the_solution(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean unavailable")
        contract, error = normalize(("python trace", IN_PROCESS))
        self.assertIsNone(error)
        sources = dict.fromkeys(("manifest", "contract", "solution"), "source")
        server = {"transport": "in_process", "entry": "worker.run"}
        claims = {
            "manifest": {"boundaries": {"io": {"server": {"worker": server}}}}
        }
        detail = server.copy()
        workflow = _trigger_workflow(detail)

        def compare():
            return _binding_directions(
                sources, claims, contract, workflow, lean
            )

        matched = compare()
        self.assertTrue(
            all(
                direction["status"] == "matched"
                for direction in matched.values()
            )
        )
        for direction in ("manifest_contract", "contract_solution"):
            self.assertNotIn(
                "entry", {fact["key"] for fact in matched[direction]["facts"]}
            )
        detail["entry"] = "other.run"
        del server["transport"]
        self.assertEqual(
            "conflicting", compare()["manifest_solution"]["status"]
        )
        del detail["entry"]
        self.assertEqual(
            "unresolved", compare()["manifest_solution"]["status"]
        )
        del server["entry"]
        self.assertEqual("matched", compare()["manifest_solution"]["status"])
        detail["transport"] = "unknown"
        self.assertEqual(
            "conflicting", compare()["contract_solution"]["status"]
        )
