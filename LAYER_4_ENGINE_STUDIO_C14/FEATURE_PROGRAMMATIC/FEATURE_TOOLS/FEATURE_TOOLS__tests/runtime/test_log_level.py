import io
import json
import os
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.RUNTIME_SUPPORT.\
    RUNTIME_SUPPORT__shared import (
    TechnicalDiagnosticLogger,
)


class LogLevelTests(unittest.TestCase):
    def test_severity_thresholds_and_default(self):
        levels = ("DEBUG", "INFO", "WARNING", "ERROR")
        for threshold in levels:
            stream = io.StringIO()
            logger = TechnicalDiagnosticLogger(
                None, None, "test", stream, "host"
            )
            with (
                self.subTest(threshold=threshold),
                patch.dict(os.environ, {"ANECHOIC_LOG_LEVEL": threshold}),
            ):
                for severity in levels:
                    self.assertIsNone(
                        logger.emit(
                            severity=severity,
                            code="x",
                            relative_path="",
                            reason="",
                        )
                    )
                self.assertEqual(
                    list(levels[levels.index(threshold) :]),
                    [
                        json.loads(line)["severity"]
                        for line in stream.getvalue().splitlines()
                    ],
                )
        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, None, "test", stream, "host")
        with patch.dict(os.environ):
            os.environ.pop("ANECHOIC_LOG_LEVEL", None)
            with patch.object(
                TechnicalDiagnosticLogger,
                "_record",
                side_effect=AssertionError("serialized"),
            ):
                self.assertIsNone(
                    logger.emit(
                        severity="DEBUG", code="x", relative_path="", reason=""
                    )
                )
        self.assertEqual("", stream.getvalue())

    def test_invalid_setting_and_sink_failure_are_secondary(self):
        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, None, "test", stream, "host")
        with patch.dict(os.environ, {"ANECHOIC_LOG_LEVEL": "info"}):
            self.assertEqual(
                "invalid ANECHOIC_LOG_LEVEL",
                logger.emit(code="x", relative_path="", reason=""),
            )
        self.assertEqual("", stream.getvalue())
        with patch.dict(os.environ, {"ANECHOIC_LOG_LEVEL": "INFO"}):
            stream.close()
            self.assertIsNotNone(
                logger.emit(code="x", relative_path="", reason="")
            )


if __name__ == "__main__":
    unittest.main()
