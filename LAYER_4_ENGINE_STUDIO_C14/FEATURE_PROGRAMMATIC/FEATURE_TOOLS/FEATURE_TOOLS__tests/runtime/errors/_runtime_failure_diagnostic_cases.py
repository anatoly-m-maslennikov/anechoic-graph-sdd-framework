"""Runtime diagnostic warning and file boundary cases."""

from concurrent.futures import CancelledError as FutureCancelledError
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.RUNTIME_SUPPORT.\
    RUNTIME_SUPPORT__shared import (
    ExplicitBlockingRuntimeFailure,
    TechnicalDiagnosticLogger,
    report_failure,
)


class RuntimeFailureCases:
    def test_workbench_query_error_is_a_warning_but_runtime_unavailability_is_an_error(
        self,
    ) -> None:
        stream = io.StringIO()
        logger = self._logger(stream)
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
            query, query_secondary = report_failure(
                self.root,
                ExplicitBlockingRuntimeFailure("query_error", "invalid SQL"),
                component="MCP_HTTP",
                operation="workbench",
            )
            unavailable, unavailable_secondary = report_failure(
                self.root,
                ExplicitBlockingRuntimeFailure(
                    "workbench_unavailable",
                    "Workbench unavailable; restart required",
                ),
                component="MCP_HTTP",
                operation="workbench",
            )
        self.assertEqual(
            ("WARNING", "query_error"), (query.severity, query.code)
        )
        self.assertIsNone(query_secondary)
        self.assertEqual(
            ("ERROR", "workbench_unavailable"),
            (unavailable.severity, unavailable.code),
        )
        self.assertIsNone(unavailable_secondary)
        self._assert_workbench_records(stream)

    def _assert_workbench_records(self, stream):
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(
            ["WARNING", "ERROR"], [record["severity"] for record in records]
        )
        self.assertEqual(
            ["failed", "blocked"], [record["outcome"] for record in records]
        )

    def test_report_does_not_write_journal_or_source_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            journal = root / "journal.ndjson"
            source = root / "source.md"
            journal.write_text("old journal\n", encoding="utf-8")
            source.write_text("old source\n", encoding="utf-8")
            before = {path: path.read_bytes() for path in (journal, source)}
            logger = TechnicalDiagnosticLogger(
                None, None, "test", io.StringIO(), "host"
            )
            with (
                patch(
                    f"{report_failure.__module__}.active_selection",
                    side_effect=ValueError("invalid"),
                ),
                patch(
                    (
                        f"{report_failure.__module__}"
                        ".make_unbound_technical_logger"
                    ),
                    return_value=(logger, None),
                ),
            ):
                report_failure(
                    root,
                    RuntimeError("secret"),
                    component="COMP",
                    operation="op",
                )
            self.assertEqual(
                before, {path: path.read_bytes() for path in before}
            )

    def test_cancellation_and_base_exceptions_are_not_swallowed(self) -> None:
        with patch(
            f"{report_failure.__module__}.active_selection",
            side_effect=FutureCancelledError,
        ):
            with self.assertRaises(FutureCancelledError):
                report_failure(
                    self.root,
                    RuntimeError("x"),
                    component="COMP",
                    operation="op",
                )
        with patch(
            f"{report_failure.__module__}.active_selection",
            side_effect=KeyboardInterrupt,
        ):
            with self.assertRaises(KeyboardInterrupt):
                report_failure(
                    self.root,
                    RuntimeError("x"),
                    component="COMP",
                    operation="op",
                )
