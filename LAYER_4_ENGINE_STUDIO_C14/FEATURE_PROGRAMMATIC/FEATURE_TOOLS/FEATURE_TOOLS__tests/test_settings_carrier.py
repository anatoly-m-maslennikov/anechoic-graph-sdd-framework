import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_settings_carrier, write_settings_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import mcp_tool_blacklist


class SettingsCarrierTest(unittest.TestCase):
    def test_readback_and_invalid_write_preserves_bytes(self):
        def validate(document):
            if set(document) != {"value"} or type(document["value"]) is not int:
                raise ValueError("invalid carrier")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.toml"
            path.write_bytes(b"value = 1\n")
            write_settings_carrier(path, "value = 2\n", validate=validate)
            self.assertEqual(read_settings_carrier(path), {"value": 2})
            before = path.read_bytes()
            for text in ('value = "wrong"\n', 'value = [\n'):
                with self.assertRaises(ValueError):
                    write_settings_carrier(path, text, validate=validate)
                self.assertEqual(path.read_bytes(), before)

    def test_settings_roundtrip_preserves_values_and_rejects_an_invalid_blacklist(self):
        valid = ('schema_version = "2.0"\n[project]\nname = "demo"\n'
                 '[artifacts.identity]\nproject_prefix = "DEMO"\n'
                 '[paths]\ncontrol_root = ".anechoic_demo"\n'
                 '[project_mcp]\ntool_blacklist = ["query_run"]\n')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.toml"
            write_settings_carrier(path, valid, validate=mcp_tool_blacklist)
            self.assertEqual(read_settings_carrier(path), {
                "schema_version": "2.0",
                "project": {"name": "demo"},
                "artifacts": {"identity": {"project_prefix": "DEMO"}},
                "paths": {"control_root": ".anechoic_demo"},
                "project_mcp": {"tool_blacklist": ["query_run"]},
            })
            invalid = valid.replace('["query_run"]', '["query_run", 1]')
            with self.assertRaisesRegex(ValueError, "An exact nonempty string is required"):
                write_settings_carrier(path, invalid, validate=mcp_tool_blacklist)
            self.assertEqual(path.read_bytes(), valid.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
