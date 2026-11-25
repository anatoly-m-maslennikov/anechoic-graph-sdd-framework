from __future__ import annotations

from pathlib import Path
import tempfile
import unittest


from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import schema_mode


class RuntimeSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.path = self.root / ".anechoic_runtime" / "anechoic_runtime_settings.toml"

    def test_missing_file_uses_the_declared_default(self) -> None:
        self.assertEqual(2, schema_mode(self.root))

    def test_schema_mode_is_fixed_to_the_two_admitted_cold_start_modes(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[workbench]\nschema_mode = 1\n", encoding="utf-8")
        self.assertEqual(1, schema_mode(self.root))
        self.path.write_text("[workbench]\nschema_mode = 3\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "schema_mode"):
            schema_mode(self.root)

if __name__ == "__main__":
    unittest.main()
