"""Compare the live C52 shape with its pinned Python implementation."""

import hashlib
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.\
    shape_implementation \
    import compare  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)

ROOT = Path(__file__).resolve().parents[5]
BASE = "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/"
MANIFEST = {
    "path": BASE
    + "01_TIER_1_ARCHITECTURE/AN-S-3066-SPEC-COMPONENT_MANIFEST--declare-generated-model.md",
    "atom_id": "AN-S-3066",
    "version": 10,
    "status": "active",
    "container_component": "C51",
}
SOLUTION = {
    "path": BASE
    + "FEATURE_GENERATED_MODEL_C52/AN-S-5033-DES-SOLUTION--represent-bundled-model-classes.md",
    "atom_id": "AN-S-5033",
    "version": 2,
    "status": "active",
    "container_component": "C52",
}
SOURCE = (
    "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/"
    "LAYER_2_FORMAL_MODEL_C51/FEATURE_GENERATED_MODEL_C52/FEATURE_GENERATED_MODEL_C52__shared.py"
)
LEAN = (
    os.environ.get("ANECHOIC_TEST_LEAN")
    or os.environ.get("LEAN_BIN")
    or shutil.which("lean")
)
COMPONENT_PATH = Path(SOURCE).parent
EXPORTED = {
    f"{Path(SOURCE).stem}.{name}": "public" for name in ("Atom", "Plan")
}


def pin(root):
    return {
        "path": SOURCE,
        "sha256": hashlib.sha256((root / SOURCE).read_bytes()).hexdigest(),
    }


def run(root, implementation):
    owner = {
        "id": "C52",
        "kind": "component",
        "path": COMPONENT_PATH.as_posix(),
        "fields": {"boundaries": {"code": {"exports": EXPORTED}}},
    }
    ownership = SimpleNamespace(
        owner=lambda path: (
            owner if Path(path).is_relative_to(COMPONENT_PATH) else None
        )
    )
    return compare(
        root,
        "C52",
        MANIFEST,
        SOLUTION,
        implementation,
        formal_verifier=verify_formal_chain,
        ownership=ownership,
        lean=LEAN,
    )


def copy_sources(root):
    for relative in (MANIFEST["path"], SOLUTION["path"], SOURCE):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)


@unittest.skipUnless(LEAN, "Lean is unavailable")
class ShapeImplementationTests(unittest.TestCase):
    def test_live_source_has_matched_shape_and_unresolved_boundary(self):
        implementation = pin(ROOT)
        report = run(ROOT, implementation)
        self.assertEqual("compared", report["outcome"], report)
        self.assertEqual("unresolved", report["status"], report)
        self.assertEqual(implementation, report["sources"]["implementation"])
        self.assertEqual("AN-S-3066", report["sources"]["manifest"]["atom_id"])
        self.assertEqual("AN-S-5033", report["sources"]["solution"]["atom_id"])
        for role in ("contract", "solution"):
            direction = report["directions"][f"{role}_implementation"]
            self.assertEqual("matched", direction["status"], report)
            expected = {
                "record",
                "subtype",
                "base",
                "field.content",
                "field.header",
            }
            if role == "solution":
                expected.add("subtype_fields")
            self.assertEqual(
                expected, {fact["key"] for fact in direction["facts"]}
            )
            self.assertTrue(
                all(fact["status"] == "matched" for fact in direction["facts"])
            )

    def test_changed_field_or_base_conflicts_with_both_specs(self):
        changes = (
            (b"header: AtomHeader", b"header: AtomContent", "field.header"),
            (b"class Plan(Atom):", b"class Plan(Continuant):", "base"),
        )
        for original, changed, key in changes:
            with (
                self.subTest(key=key),
                tempfile.TemporaryDirectory() as folder,
            ):
                root = Path(folder)
                copy_sources(root)
                source = root / SOURCE
                raw = source.read_bytes()
                self.assertEqual(1, raw.count(original))
                source.write_bytes(raw.replace(original, changed))
                report = run(root, pin(root))
                self.assertEqual("compared", report["outcome"], report)
                self.assertEqual("conflicting", report["status"], report)
                for role in ("contract", "solution"):
                    direction = report["directions"][f"{role}_implementation"]
                    facts = {
                        fact["key"]: fact["status"]
                        for fact in direction["facts"]
                    }
                    self.assertEqual(
                        "conflicting", direction["status"], report
                    )
                    self.assertEqual("conflicting", facts[key], report)

    def test_extra_subtype_field_does_not_extend_the_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            copy_sources(root)
            source = root / SOURCE
            raw = source.read_bytes()
            self.assertEqual(1, raw.count(b"class Plan(Atom):\n    pass"))
            source.write_bytes(
                raw.replace(
                    b"class Plan(Atom):\n    pass",
                    b"class Plan(Atom):\n    extra: str",
                )
            )
            report = run(root, pin(root))
        self.assertEqual(
            "matched",
            report["directions"]["contract_implementation"]["status"],
            report,
        )
        self.assertEqual(
            "conflicting",
            report["directions"]["solution_implementation"]["status"],
            report,
        )

    def test_unrelated_source_with_matching_classes_is_unresolved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            copy_sources(root)
            code = (root / SOURCE).read_bytes()
            for path in (
                Path("unrelated") / Path(SOURCE).name,
                COMPONENT_PATH / "unrelated.py",
            ):
                with self.subTest(path=path):
                    target = root / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(code)
                    report = run(
                        root,
                        {
                            "path": path.as_posix(),
                            "sha256": hashlib.sha256(code).hexdigest(),
                        },
                    )
                    self.assertEqual("incomplete", report["outcome"], report)
                    self.assertEqual({}, report["directions"], report)

    def test_stale_digest_and_unsupported_annotation_are_unresolved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            copy_sources(root)
            source = root / SOURCE
            old_pin = pin(root)
            raw = source.read_bytes()
            original = b"header: AtomHeader"
            self.assertEqual(1, raw.count(original))
            source.write_bytes(
                raw.replace(original, b"header: AtomHeader | None")
            )
            for implementation, reason in (
                (old_pin, "digest"),
                (pin(root), "Unsupported"),
            ):
                with self.subTest(reason=reason):
                    report = run(root, implementation)
                    self.assertEqual("incomplete", report["outcome"], report)
                    self.assertEqual("unresolved", report["status"], report)
                    self.assertEqual({}, report["directions"])
                    self.assertTrue(
                        any(
                            isinstance(item, str) and reason in item
                            for item in report["unresolved"]
                        ),
                        report,
                    )


if __name__ == "__main__":
    unittest.main()
