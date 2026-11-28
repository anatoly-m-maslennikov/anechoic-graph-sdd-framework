"""Check image selection through the Runtime's environment."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


APP = Path(__file__).resolve().parents[4]

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (  # noqa: E402
    IMAGE,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (  # noqa: E402
    Runtime,
)


IMMUTABLE_IMAGE = "sha256:" + "a" * 64


class ImageOverrideTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_runtime_uses_explicit_immutable_image(self):
        with patch.dict(os.environ, {"ANECHOIC_IMAGE": IMMUTABLE_IMAGE}):
            self.assertEqual(
                IMMUTABLE_IMAGE,
                Runtime(self.root).environment()["ANECHOIC_IMAGE"],
            )
        instance = Runtime(self.root, image=IMMUTABLE_IMAGE)
        with patch.dict(os.environ, {"ANECHOIC_IMAGE": "sha256:" + "b" * 64}):
            self.assertEqual(
                IMMUTABLE_IMAGE, instance.environment()["ANECHOIC_IMAGE"]
            )

    def test_runtime_empty_override_uses_safe_development_fallback(self):
        with patch.dict(os.environ, {"ANECHOIC_IMAGE": ""}):
            self.assertEqual(
                IMAGE, Runtime(self.root).environment()["ANECHOIC_IMAGE"]
            )

    def test_mutable_or_malformed_overrides_are_rejected(self):
        for value in (
            "alpine:latest",
            "sha256:" + "A" * 64,
            "sha256:" + "a" * 63,
            "1",
        ):
            with (
                self.subTest(value=value),
                patch.dict(os.environ, {"ANECHOIC_IMAGE": value}),
            ):
                with self.assertRaisesRegex(ValueError, "immutable sha256"):
                    Runtime(self.root).environment()
        with self.assertRaisesRegex(ValueError, "immutable sha256"):
            Runtime(self.root, image=1)


if __name__ == "__main__":
    unittest.main()
