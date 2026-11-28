import os
from hashlib import sha256
from importlib import import_module
import shutil
import tempfile
from pathlib import Path

_base = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
_delegation = import_module(
    _base + "LAYER_2_FORMAL_SPECIFICATION_C94."
    "LAYER_4_SPEC_COMPARISON_C88.DELEGATION_VERIFICATION_C89."
    "_package__shared"
)
check_sibling_outcome = _delegation.check_sibling_outcome
check_sibling_binding = _delegation.check_sibling_binding


ROOT = Path(__file__).parents[2] / "assets" / "canonical_siblings"


def pin(number, component):
    return {
        "path": f"AN-S-{number}.md",
        "atom_id": f"AN-S-{number}",
        "version": 1,
        "status": "active",
        "container_component": component,
    }


class CanonicalSiblingPairCases:
    def test_unknown_event_preserves_caller_diagnostic(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        caller = pin(2, "C2")
        result = check_sibling_outcome(
            ROOT,
            (pin(1, "C1"), caller),
            "C3",
            (pin(3, "C1"), pin(4, "C3")),
            event="missing_event",
            interface="worker",
            lean=lean,
        )
        self.assertEqual("unresolved", result["status"])
        digest = sha256((ROOT / caller["path"]).read_bytes()).hexdigest()
        self.assertIn(
            {
                "source": {**caller, "sha256": digest},
                "field": "solution",
                "message": (
                    "The selected effect has no complete provider action "
                    "and output binding"
                ),
            },
            result["unresolved"],
        )

    def test_both_sibling_checks_reject_a_blank_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = []
            for source, component in enumerate(("C1", "C2", "C1", "C3"), 1):
                request = pin(source, component)
                path = request["path"]
                raw = (ROOT / path).read_bytes()
                if component == "C1":
                    raw = raw.replace(
                        b"{component: C1}", b'{component: " \\t"}'
                    )
                    request["container_component"] = " \t"
                (root / path).write_bytes(raw)
                pins.append({**request, "sha256": sha256(raw).hexdigest()})
            for check in (check_sibling_binding, check_sibling_outcome):
                with (
                    self.subTest(check=check.__name__),
                    self.assertRaisesRegex(
                        ValueError, "invalid manifest source pin"
                    ),
                ):
                    check(
                        root,
                        pins[:2],
                        "C3",
                        pins[2:],
                        event="invoke",
                        interface="worker",
                        lean=os.environ.get("ANECHOIC_TEST_LEAN", "lean"),
                    )

    def test_entry_without_transport_is_checked(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                shutil.copy(source, root / source.name)
            source = root / "AN-S-2.md"
            source.write_text(
                source.read_text().replace(
                    "'transport': 'in_process', 'entry': 'worker.run'",
                    "'entry': 'worker.other'",
                )
            )
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

    def test_embedded_outcome_needs_association_with_interface(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in ROOT.glob("*.md"):
                shutil.copy(source, root / source.name)
            self.remove_interface_association(root)
            result = check_sibling_outcome(
                root,
                (pin(1, "C1"), pin(2, "C2")),
                "C3",
                (pin(3, "C1"), pin(4, "C3")),
                event="invoke",
                interface="unrelated",
                lean=lean,
            )
            self.assertEqual("unresolved", result["status"], result)
            self.assertTrue(
                all(
                    row["status"] == "unresolved"
                    for row in result["directions"].values()
                ),
                result,
            )

    def test_http_outcome_checks_provider_route_and_client_declaration(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_http_fixtures(root)

            def check():
                return check_sibling_outcome(
                    root,
                    (pin(1, "C1"), pin(2, "C2")),
                    "C3",
                    (pin(3, "C1"), pin(4, "C3")),
                    event="invoke",
                    interface="worker",
                    lean=lean,
                )

            result = check()
            self.assertEqual("matched", result["status"], result)
            source = root / "AN-S-4.md"
            body = source.read_text()
            source.write_text(body.replace("POST /work", "POST /other"))
            self.assertEqual("conflicting", check()["status"])
            source.write_text(body)
            source = root / "AN-S-1.md"
            source.write_text(
                source.read_text().replace("POST /work", "POST /other")
            )
            with self.assertRaisesRegex(ValueError, "does not declare client"):
                check()

    def remove_interface_association(self, root):
        source = root / "AN-S-3.md"
        source.write_text(
            source.read_text()
            .replace(
                "'worker': {'transport': 'in_process', 'entry': 'worker.run'}",
                "'unrelated': {}",
            )
            .replace(", interface='worker', transport='in_process'", "")
        )
        source = root / "AN-S-4.md"
        source.write_text(
            source.read_text().replace(
                ", 'target': 'worker', 'detail': {"
                "'transport': 'in_process', "
                "'entry': 'worker.run'}",
                "",
            )
        )
        for name in ("AN-S-1.md", "AN-S-2.md"):
            source = root / name
            source.write_text(
                source.read_text()
                .replace("worker", "unrelated")
                .replace(
                    "'transport': 'in_process', 'entry': 'unrelated.run', ",
                    "",
                )
            )

    def write_http_fixtures(self, root):
        for source in ROOT.glob("*.md"):
            body = source.read_text().replace(
                "'transport': 'in_process', 'entry': 'worker.run'",
                "'transport': 'http', 'route': 'POST /work'",
            )
            if source.name == "AN-S-1.md":
                body = body.replace(
                    "'transport': 'in_process'",
                    "'transport': 'http', 'routes': ['POST /work']",
                )
            if source.name == "AN-S-3.md":
                body = body.replace(
                    "'transport': 'http', 'route': 'POST /work'",
                    "'transport': 'http', 'routes': ['POST /work']",
                )
                body = body.replace(
                    ", interface='worker', transport='in_process'", ""
                )
            (root / source.name).write_text(body)
