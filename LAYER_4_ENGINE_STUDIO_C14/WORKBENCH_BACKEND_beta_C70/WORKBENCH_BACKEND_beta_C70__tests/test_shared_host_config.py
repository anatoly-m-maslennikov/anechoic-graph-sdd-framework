"""Exercise logging settings at the native shared Backend startup boundary."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from WORKBENCH_BACKEND_beta_C70.shared_host_config import load


class SharedHostConfigTests(unittest.TestCase):
    def test_accepts_legacy_settings_and_validates_the_optional_logging_table(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            settings = root / "runtime.toml"
            base = f'schema_version=1\n[shared_mcp]\nproject_root="{root}"\nhttp_port=8092\n'
            for suffix, expected in (("", "INFO"), ("[logging]\n", "INFO"), ('[logging]\nlevel="WARNING"\n', "WARNING")):
                with self.subTest(suffix=suffix):
                    settings.write_text(base + suffix)
                    self.assertEqual(expected, load(settings).log_level)
            for suffix in ('level="warning"\n', 'level=false\n', 'extra="INFO"\n'):
                with self.subTest(suffix=suffix), self.assertRaisesRegex(ValueError, "host_configuration_invalid"):
                    settings.write_text(base + "[logging]\n" + suffix)
                    load(settings)
