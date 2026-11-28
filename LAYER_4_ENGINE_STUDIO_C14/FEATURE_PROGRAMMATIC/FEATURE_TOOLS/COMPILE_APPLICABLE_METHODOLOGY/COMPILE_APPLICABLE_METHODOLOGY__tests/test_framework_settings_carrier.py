from __future__ import annotations

import importlib
import os
import unittest
from pathlib import Path


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    COMPILE_APPLICABLE_METHODOLOGY.METHODOLOGY_READING.METHODOLOGY_READING__shared import (
    DEFAULT_SETTINGS_NAME,
    INSTANCE_SETTINGS_RELATIVE,
)

support = importlib.import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS."
    "COMPILE_APPLICABLE_METHODOLOGY."
    "COMPILE_APPLICABLE_METHODOLOGY__tests.methodology_test_support"
)
compiler = support.module


class FrameworkSettingsCarrierTest(support.CompilerFixture):
    def setUp(self) -> None:
        super().setUp()
        self.root = self.temp
        self.control = Path(".anechoic_anechoic")

    def write(self, relative: Path, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def paths(self) -> compiler.MethodologyPaths:
        return compiler.methodology_paths(self.root)

    def \
    test_nondefault_control_root_uses_canonical_instance_and_merges_default(
        self,
    ) -> None:  # fmt: skip
        self.write(
            self.layers["CORE_META_MODEL"] / DEFAULT_SETTINGS_NAME,
            (
                '[defaults]\ncolour = "blue"\n[extensions.default]\nenabled = '
                'true\nrevision = "v1"\n'
            ),
        )
        canonical = self.write(
            self.control / INSTANCE_SETTINGS_RELATIVE,
            (
                '[instance]\nlabel = "custom-control"\n[extensions.default]\ne'
                'nabled = true\nrevision = "v2"\n'
            ),
        )
        legacy = self.write(
            self.layers["PROJECT_CONFIGURATION"]
            / "anechoic_framework_settings.toml",
            '[extensions.default]\nenabled = true\nrevision = "legacy"\n',
        )

        settings, bindings = compiler.framework_settings(
            self.root, self.paths()
        )

        self.assertEqual("blue", settings["defaults"]["colour"])
        self.assertEqual("custom-control", settings["instance"]["label"])
        self.assertEqual(
            {"default": "v2"}, compiler.extension_selections(settings)
        )
        self.assertIn(canonical.relative_to(self.root).as_posix(), bindings)
        self.assertNotIn(legacy.relative_to(self.root).as_posix(), bindings)

    def \
test_canonical_instance_addition_mutation_and_removal_change_source_snapshot \
        (self) -> None:  # fmt: skip
        places = self.paths()
        absent = compiler.source_state_snapshot(self.root, places)
        canonical = self.write(
            self.control / INSTANCE_SETTINGS_RELATIVE,
            "[instance]\nvalue = 1\n",
        )
        added = compiler.source_state_snapshot(self.root, places)
        self.assertNotEqual(absent, added)
        self.assertIn(canonical.relative_to(self.root).as_posix(), added)

        canonical.write_text("[instance]\nvalue = 2\n", encoding="utf-8")
        mutated = compiler.source_state_snapshot(self.root, places)
        self.assertNotEqual(added, mutated)

        canonical.unlink()
        self.assertEqual(
            absent, compiler.source_state_snapshot(self.root, places)
        )

    def test_symlinked_canonical_carrier_or_ancestor_is_refused(self) -> None:
        canonical = self.root / self.control / INSTANCE_SETTINGS_RELATIVE
        canonical.parent.mkdir(parents=True, exist_ok=True)
        target = self.root / "settings-target.toml"
        target.write_text("[instance]\nvalue = 1\n", encoding="utf-8")
        os.symlink(target, canonical)
        with self.assertRaises(compiler.CompileError) as symlinked_file:
            compiler.framework_settings(self.root, self.paths())
        self.assertEqual(
            "framework-settings-invalid", symlinked_file.exception.code
        )

        canonical.unlink()
        default_dir = self.layers["CORE_META_MODEL"]
        default_dir.rmdir()
        external_dir = self.root / "external-defaults"
        external_dir.mkdir()
        (external_dir / "anechoic_framework_default_settings.toml").write_text(
            "[defaults]\nvalue = 1\n", encoding="utf-8"
        )
        os.symlink(external_dir, default_dir)
        with self.assertRaises(compiler.CompileError) as symlinked_ancestor:
            compiler.framework_settings(self.root, self.paths())
        self.assertEqual(
            "scope-declarations-invalid", symlinked_ancestor.exception.code
        )


if __name__ == "__main__":
    unittest.main()
