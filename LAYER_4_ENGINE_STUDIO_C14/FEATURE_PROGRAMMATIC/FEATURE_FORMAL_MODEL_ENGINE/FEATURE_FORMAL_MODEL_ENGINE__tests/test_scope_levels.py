"""The reviewed check uses stored levels from Scope declarations."""

import base64
import importlib.util
import json
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

from pydantic import ValidationError


from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.\
    FEATURE_FORMAL_MODEL_ENGINE__shared \
    import (
        Atom,
        ScopeUnit,
        check_scope_levels_with_packaged_check,
        dependencies_are_distinct,
        generated_assets,
        load_packaged_module,
        verify_packaged_assets,
        verify_packaged_dependencies_check,
        write_package,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope__shared import (
    ScopeUnitDeclaration,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
    formal_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier,
)

PROGRAMMATIC = Path(__file__).resolve().parents[2]


def check_structural_level(unit):
    return unit.structural_level == (
        0 if unit.container is None else unit.container.structural_level + 1
    )


class ScopeLevelsTests(unittest.TestCase):
    def test_checks_authored_levels_and_reports_missing_parent_data(self):
        def record(name, level, parent=None):
            return ScopeUnitDeclaration(
                name,
                "CA-R-1",
                1,
                Path("scope.md"),
                parent=parent,
                structural_level=level,
            )

        declarations = SimpleNamespace(
            by_name={
                "root": record("root", 0),
                "valid": record("valid", 1, "root"),
                "wrong": record("wrong", 2, "root"),
                "legacy": record("legacy", None, "root"),
                "missing_container_level": record(
                    "missing_container_level", 2, "legacy"
                ),
            }
        )
        self.assertEqual(
            {
                "wrong": "Structural level violates the reviewed Claim",
                "legacy": "Missing structural_level",
                "missing_container_level": (
                    "Container is missing structural_level"
                ),
            },
            check_scope_levels_with_packaged_check(
                declarations, instance_check=check_structural_level
            ),
        )

    def test_model_inputs_are_strict_frozen_and_hashable(self):
        root = ScopeUnit(0, None)
        child = ScopeUnit(1, root)
        atom = Atom(("A", "B"))
        self.assertEqual(child, ScopeUnit(1, ScopeUnit(0, None)))
        self.assertEqual(hash(child), hash(ScopeUnit(1, root)))
        self.assertEqual({atom}, {Atom(("A", "B"))})
        with self.assertRaises(FrozenInstanceError):
            child.structural_level = 2
        with self.assertRaises(FrozenInstanceError):
            atom.dependencies = ()
        for build in (
            lambda: ScopeUnit("1", root),
            lambda: ScopeUnit(1, {}),
            lambda: Atom(["A"]),
            lambda: Atom((1,)),
        ):
            with self.subTest(build=build), self.assertRaises(ValidationError):
                build()

    def test_dependency_claim(self):
        verify_packaged_dependencies_check()
        self.assertTrue(dependencies_are_distinct(Atom(("A", "B"))))
        self.assertFalse(dependencies_are_distinct(Atom(("A", "A"))))

    def test_packaged_check_reproduces_and_loads(self):
        root = Path(__file__).resolve().parent.parent
        assets = root / "assets"
        pin = json.loads((root / "scope_callback_selection.json").read_text())[
            "selected"
        ]["pin"]
        metadata = json.loads(
            (assets / "scope_level_metadata.json").read_text()
        )
        if (
            metadata["python_version"] != list(sys.version_info[:3])
            or metadata["python_magic"] != importlib.util.MAGIC_NUMBER.hex()
        ):
            self.skipTest(
                "packaged check requires its pinned Python interpreter"
            )
        raw = base64.b64decode(
            json.loads((assets / "scope_level_sources.json").read_text())[
                metadata["reference"]
            ]
        )
        generated = generated_assets(raw, pin=pin, release_sources=[pin])
        with tempfile.TemporaryDirectory() as tmp:
            rebuilt = Path(tmp)
            write_package(rebuilt, generated)
            verify_packaged_assets(
                rebuilt, raw, pin=pin, release_sources=[pin]
            )
            for name in (
                "scope_level_check.py",
                "scope_level_check.bin",
                "scope_level_metadata.json",
                "scope_level_sources.json",
            ):
                self.assertEqual(
                    (rebuilt / name).read_bytes(), (assets / name).read_bytes()
                )
        check = load_packaged_module(assets, release_pin=metadata)
        self.assertTrue(check(ScopeUnit(0, None)))
        self.assertTrue(check(ScopeUnit(1, ScopeUnit(0, None))))
        self.assertFalse(check(ScopeUnit(2, ScopeUnit(0, None))))

    def test_callback_rejects_runtime_scope_unit_reference(self):
        root = Path(__file__).resolve().parent.parent
        pin = json.loads((root / "scope_callback_selection.json").read_text())[
            "selected"
        ]["pin"]
        snapshot = json.loads(
            (root / "assets/scope_level_sources.json").read_text()
        )
        raw = base64.b64decode(snapshot["CA-R-2554@3"]).replace(
            b"if unit.structural_level is None:",
            b"if ScopeUnit is None:",
            1,
        )
        pin["carrier_sha256"] = sha256(raw).hexdigest()
        pin["claim_sha256"] = sha256(
            formal_claim(parse_carrier(raw, Path("source.md")).body).encode()
        ).hexdigest()
        with self.assertRaisesRegex(
            ValueError, "ScopeUnit may appear only in annotations"
        ):
            generated_assets(raw, pin=pin, release_sources=[pin])
