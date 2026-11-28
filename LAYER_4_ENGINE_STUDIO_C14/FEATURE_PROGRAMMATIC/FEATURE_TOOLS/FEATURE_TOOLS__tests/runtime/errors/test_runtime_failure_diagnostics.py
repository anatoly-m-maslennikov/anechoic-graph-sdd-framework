"""Focused checks for the shared runtime failure diagnostic facade."""

from __future__ import annotations

from contextlib import redirect_stderr
import io
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parents[3]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.PROJECT_SUPPORT.RUNTIME_SUPPORT.RUNTIME_SUPPORT__shared import (  # noqa: E402
    ExplicitBlockingRuntimeFailure,
    FailureRecord,
    TechnicalDiagnosticLogger,
    report_failure,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.runtime.errors import (  # noqa: E402
    _runtime_failure_diagnostic_cases as cases,
)


class _FailingStream:
    def write(self, _value: str) -> int:
        raise OSError("password=secret")

    def flush(self) -> None:
        raise OSError("password=secret")


class RuntimeFailureDiagnosticsTests(
    cases.RuntimeFailureCases, unittest.TestCase
):
    def setUp(self) -> None:
        self.root = Path("/bound/project")
        self.selection = SimpleNamespace(settings={"actual": "settings"})

    def _logger(self, stream: io.TextIOBase) -> TechnicalDiagnosticLogger:
        return TechnicalDiagnosticLogger(
            "ACTUAL", self.root, "test", stream, "host"
        )

    def test_bound_root_uses_selected_settings_and_actual_component(
        self,
    ) -> None:
        stream = io.StringIO()
        logger = self._logger(stream)
        with (
            patch(
                f"{report_failure.__module__}.active_selection",
                return_value=self.selection,
            ) as selected,
            patch(
                f"{report_failure.__module__}.make_technical_logger",
                return_value=(logger, None),
            ) as made,
        ):
            failure, secondary = report_failure(
                self.root,
                RuntimeError("password=secret"),
                component="ACTUAL_COMPONENT",
                operation="lookup",
                correlation_id="corr-1",
            )
        selected.assert_called_once_with(self.root)
        made.assert_called_once_with(self.selection.settings, self.root)
        self.assertIsNone(secondary)
        self.assertEqual("RuntimeError", failure.exception_class)
        record = json.loads(stream.getvalue())
        self.assertEqual("ACTUAL_COMPONENT", record["component"])
        self.assertEqual("ACTUAL", record["project_prefix"])
        self.assertEqual("corr-1", record["correlation_id"])
        self.assertNotIn("password=secret", stream.getvalue())

    def test_unbound_or_invalid_selection_is_visible_without_guessed_prefix(
        self,
    ) -> None:
        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, None, "test", stream, "host")
        with patch(
            f"{report_failure.__module__}.make_unbound_technical_logger",
            return_value=(logger, None),
        ):
            with redirect_stderr(io.StringIO()):
                failure, secondary = report_failure(
                    None,
                    RuntimeError("password=secret"),
                    component="COMP",
                    operation="op",
                )
        self.assertEqual("internal_failure", failure.code)
        self.assertIsNone(secondary)
        record = json.loads(stream.getvalue())
        self.assertEqual("unbound", record["project_binding"])
        self.assertNotIn("project_prefix", record)

        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, None, "test", stream, "host")
        with (
            patch(
                f"{report_failure.__module__}.active_selection",
                side_effect=ValueError("secret"),
            ),
            patch(
                f"{report_failure.__module__}.make_unbound_technical_logger",
                return_value=(logger, None),
            ),
        ):
            _failure, secondary = report_failure(
                self.root,
                RuntimeError("password=secret"),
                component="COMP",
                operation="op",
            )
        self.assertEqual("project binding unavailable", secondary)
        self.assertEqual(
            "unbound", json.loads(stream.getvalue())["project_binding"]
        )

    def test_record_preserves_optional_fields_and_elapsed_number(self) -> None:
        for elapsed, expected in (
            (1, '"elapsed_ms":1'),
            (1.5, '"elapsed_ms":1.5'),
        ):
            stream = io.StringIO()
            logger = self._logger(stream)
            self.assertIsNone(
                logger.emit(
                    code="test",
                    relative_path="",
                    reason="token=secret",
                    elapsed_ms=elapsed,
                )
            )
            line = stream.getvalue()
            self.assertIn(expected, line)
            self.assertNotIn("correlation_id", line)
            self.assertNotIn("exception_class", line)
            self.assertNotIn("project_binding", line)
            self.assertNotIn("token=secret", line)

    def test_sink_failure_is_secondary_and_sanitized(self) -> None:
        logger = self._logger(_FailingStream())
        with (
            patch(
                f"{report_failure.__module__}.active_selection",
                return_value=self.selection,
            ),
            patch(
                f"{report_failure.__module__}.make_technical_logger",
                return_value=(logger, None),
            ),
        ):
            _failure, secondary = report_failure(
                self.root,
                RuntimeError("password=secret"),
                component="COMP",
                operation="op",
            )
        self.assertEqual("technical diagnostic emission failed", secondary)

    def test_structured_warning_is_not_given_a_fake_exception_class(
        self,
    ) -> None:
        stream = io.StringIO()
        logger = self._logger(stream)
        warning = FailureRecord("WARNING", "project_invalid", "safe warning")
        with (
            patch(
                f"{report_failure.__module__}.active_selection",
                return_value=self.selection,
            ),
            patch(
                f"{report_failure.__module__}.make_technical_logger",
                return_value=(logger, None),
            ),
        ):
            failure, secondary = report_failure(
                self.root, warning, component="COMP", operation="op"
            )
        self.assertIs(warning, failure)
        self.assertIsNone(secondary)
        self.assertNotIn("exception_class", json.loads(stream.getvalue()))

    def test_structured_errors_preserve_severity_except_workbench_query_error(
        self,
    ) -> None:
        stream = io.StringIO()
        logger = self._logger(stream)
        cases = (
            ("query_error", "WARNING", "failed"),
            ("workbench_unavailable", "ERROR", "blocked"),
            ("synthetic_error", "ERROR", "blocked"),
        )
        with (
            patch(
                f"{report_failure.__module__}.active_selection",
                return_value=self.selection,
            ),
            patch(
                f"{report_failure.__module__}.make_technical_logger",
                return_value=(logger, None),
            ),
        ):
            for code, severity, outcome in cases:
                with self.subTest(code=code):
                    stream.seek(0)
                    stream.truncate(0)
                    synthetic = FailureRecord(
                        "ERROR",
                        code,
                        "safe synthetic",
                    )
                    failure, secondary = report_failure(
                        self.root, synthetic, component="COMP", operation="op"
                    )
                    self.assertEqual(severity, failure.severity)
                    self.assertIsNone(secondary)
                    record = json.loads(stream.getvalue())
                    self.assertEqual(severity, record["severity"])
                    self.assertEqual(outcome, record["outcome"])

    def test_explicit_blocking_failure_remains_error(self) -> None:
        stream = io.StringIO()
        logger = self._logger(stream)
        error = ExplicitBlockingRuntimeFailure(
            "runtime_blocked", "worker unavailable"
        )
        with (
            patch(
                f"{report_failure.__module__}.active_selection",
                return_value=self.selection,
            ),
            patch(
                f"{report_failure.__module__}.make_technical_logger",
                return_value=(logger, None),
            ),
        ):
            failure, secondary = report_failure(
                self.root, error, component="COMP", operation="op"
            )
        self.assertEqual(
            ("ERROR", "runtime_blocked"), (failure.severity, failure.code)
        )
        self.assertIsNone(secondary)
        self.assertEqual("ERROR", json.loads(stream.getvalue())["severity"])


if __name__ == "__main__":
    unittest.main()
