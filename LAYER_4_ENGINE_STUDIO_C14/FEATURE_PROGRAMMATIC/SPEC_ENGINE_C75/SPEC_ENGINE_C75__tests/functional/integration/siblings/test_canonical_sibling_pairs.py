from ._canonical_sibling_pair_cases import CanonicalSiblingPairCases

import os
from importlib import import_module
import shutil
import tempfile
import unittest
from pathlib import Path

_base = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
_delegation = import_module(
    _base + "LAYER_2_FORMAL_SPECIFICATION_C94."
    "LAYER_4_SPEC_COMPARISON_C88.DELEGATION_VERIFICATION_C89."
    "_package__shared"
)
check_sibling_outcome = _delegation.check_sibling_outcome
check_sibling_binding = _delegation.check_sibling_binding
SourceError = import_module(
    _base + "LAYER_1_SOURCE_ADAPTERS_C95._package__shared"
).SourceError


ROOT = Path(__file__).parents[2] / "assets" / "canonical_siblings"


def pin(number, component):
    return {
        "path": f"AN-S-{number}.md",
        "atom_id": f"AN-S-{number}",
        "version": 1,
        "status": "active",
        "container_component": component,
    }


class CanonicalSiblingPairsTests(CanonicalSiblingPairCases, unittest.TestCase):
    def test_both_sibling_checks_accept_exact_pairs(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        caller = (pin(1, "C1"), pin(2, "C2"))
        provider = (pin(3, "C1"), pin(4, "C3"))
        for check in (check_sibling_binding, check_sibling_outcome):
            with self.subTest(check=check.__name__):
                result = check(
                    ROOT,
                    caller,
                    "C3",
                    provider,
                    event="invoke",
                    interface="worker",
                    lean=lean,
                )
                self.assertEqual("matched", result["status"])
                self.assertEqual(
                    "AN-S-3", result["sources"]["manifest"]["atom_id"]
                )
                self.assertEqual(
                    "AN-S-3", result["sources"]["contract"]["atom_id"]
                )
                self.assertEqual(
                    "AN-S-4", result["sources"]["solution"]["atom_id"]
                )
                self.assertEqual(
                    {"caller_manifest", "caller_contract", "caller_solution"},
                    set(result["directions"]),
                )

    def test_wrong_manifest_reference_conflicts(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                shutil.copy(source, root / source.name)
            source = root / "AN-S-2.md"
            source.write_text(
                source.read_text().replace("AN-S-3@1", "AN-S-9@1")
            )
            for check in (check_sibling_binding, check_sibling_outcome):
                with self.subTest(check=check.__name__):
                    result = check(
                        root,
                        (pin(1, "C1"), pin(2, "C2")),
                        "C3",
                        (pin(3, "C1"), pin(4, "C3")),
                        event="invoke",
                        interface="worker",
                        lean=lean,
                    )
                    self.assertEqual("conflicting", result["status"])

    def test_caller_solution_pin_is_validated(self):
        caller = (pin(1, "C1"), {**pin(2, "C2"), "version": 2})
        for check in (check_sibling_binding, check_sibling_outcome):
            with (
                self.subTest(check=check.__name__),
                self.assertRaises(SourceError),
            ):
                check(
                    ROOT,
                    caller,
                    "C3",
                    (pin(3, "C1"), pin(4, "C3")),
                    event="invoke",
                    interface="worker",
                )

    def test_private_entry_is_checked_against_boundary_and_solution(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                shutil.copy(source, root / source.name)
            for name in ("AN-S-3.md", "AN-S-4.md"):
                with self.subTest(source=name):
                    source = root / name
                    original = source.read_text()
                    source.write_text(
                        original.replace("worker.run", "worker.other")
                    )
                    result = check_sibling_binding(
                        root,
                        (pin(1, "C1"), pin(2, "C2")),
                        "C3",
                        (pin(3, "C1"), pin(4, "C3")),
                        event="invoke",
                        interface="worker",
                        lean=lean,
                    )
                    self.assertEqual("conflicting", result["status"])
                    source.write_text(original)

    def test_outcome_checks_explicit_entry_and_transport(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                shutil.copy(source, root / source.name)
            for name, original, changed in (
                ("AN-S-2.md", "worker.run", "worker.other"),
                (
                    "AN-S-3.md",
                    "'transport': 'in_process'",
                    "'transport': 'http'",
                ),
                ("AN-S-4.md", "worker.run", "worker.other"),
            ):
                with self.subTest(source=name):
                    source = root / name
                    body = source.read_text()
                    source.write_text(body.replace(original, changed))
                    result = check_sibling_outcome(
                        root,
                        (pin(1, "C1"), pin(2, "C2")),
                        "C3",
                        (pin(3, "C1"), pin(4, "C3")),
                        event="invoke",
                        interface="worker",
                        lean=lean,
                    )
                    self.assertEqual("conflicting", result["status"], result)
                    source.write_text(body)

    def test_explicit_outcome_transport_requires_a_matching_client(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                shutil.copy(source, root / source.name)
            for name in ("AN-S-1.md", "AN-S-2.md"):
                with self.subTest(source=name):
                    source = root / name
                    body = source.read_text()
                    source.write_text(
                        body.replace(
                            "'transport': 'in_process'", "'transport': 'http'"
                        )
                    )
                    with self.assertRaisesRegex(
                        ValueError, "does not declare client"
                    ):
                        check_sibling_outcome(
                            root,
                            (pin(1, "C1"), pin(2, "C2")),
                            "C3",
                            (pin(3, "C1"), pin(4, "C3")),
                            event="invoke",
                            interface="worker",
                        )
                    source.write_text(body)

    def test_mixed_framing_order_does_not_change_sibling_checks(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                shutil.copy(source, root / source.name)
            for first in (True, False):
                for name, claim in FRAMING.items():
                    source = root / name
                    body = (ROOT / name).read_text()
                    fence = f"```python framing\n{claim}\n```\n"
                    if first:
                        position = body.rfind("```python")
                        body = body[:position] + fence + body[position:]
                    else:
                        body += "\n" + fence
                    source.write_text(body)
                for check in (check_sibling_binding, check_sibling_outcome):
                    with self.subTest(first=first, check=check.__name__):
                        kwargs = (
                            {"action": "run"}
                            if check is check_sibling_binding
                            else {}
                        )
                        result = check(
                            root,
                            (pin(1, "C1"), pin(2, "C2")),
                            "C3",
                            (pin(3, "C1"), pin(4, "C3")),
                            event="invoke",
                            interface="worker",
                            lean=lean,
                            **kwargs,
                        )
                        self.assertEqual("matched", result["status"], result)

    def test_public_interface_mismatch_conflicts(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                shutil.copy(source, root / source.name)
            source = root / "AN-S-3.md"
            source.write_text(
                source.read_text().replace(
                    "interface='worker', transport='in_process'",
                    "interface='other', transport='in_process'",
                )
            )
            result = check_sibling_binding(
                root,
                (pin(1, "C1"), pin(2, "C2")),
                "C3",
                (pin(3, "C1"), pin(4, "C3")),
                event="invoke",
                interface="worker",
                lean=lean,
            )
            self.assertEqual(
                "conflicting",
                result["directions"]["caller_contract"]["status"],
            )


FRAMING = {
    "AN-S-3.md": (
        "declare_framing_contract(delimiter=[35], "
        "line_endings=[[10], [13, 10]])"
    ),
    "AN-S-4.md": "declare_framing_solution("
    "opening_prefixes=[[35, 10], [35, 13, 10]], "
    "closing_prefixes=[[10, 35, 10], [10, 35, 13, 10], "
    "[13, 10, 35, 10], [13, 10, 35, 13, 10]])",
}
