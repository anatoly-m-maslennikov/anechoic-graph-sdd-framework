"""Focused checks for process-boundary diagnostic observation behavior."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


TESTS = Path(__file__).resolve().parent
TOOLS = TESTS.parent
for path in (TESTS, TOOLS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (  # noqa: E402
    runtime_process_boundary_module as boundary,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (  # noqa: E402
    FailureRecord,
    report_failure,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (  # noqa: E402
    TechnicalDiagnosticLogger,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_runtime_process_boundary import (  # noqa: E402
    _record_report,
)


class RuntimeProcessObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.calls: list[
            tuple[Path | None, Exception | FailureRecord, dict[str, object]]
        ] = []

    def test_diagnostic_sink_failure_has_bounded_fallback(self) -> None:
        def failed_report(root, error, **kwargs):
            failure, _secondary = _record_report(
                self.calls, root, error, **kwargs
            )
            return failure, "sink failed: password=secret"

        stderr = io.StringIO()
        with (
            patch.object(
                boundary, "report_failure", side_effect=failed_report
            ),
            redirect_stderr(stderr),
        ):
            self.assertEqual(
                2,
                boundary.run_process(
                    lambda: (_ for _ in ()).throw(RuntimeError("secret")),
                    operation="sink",
                    root=Path("/project"),
                ),
            )
        self.assertEqual(
            1, stderr.getvalue().count("technical diagnostics unavailable")
        )
        self.assertNotIn("secret", stderr.getvalue())
        self.assertEqual(1, len(self.calls))
        self.assertEqual(Path("/project"), self.calls[0][0])
        self.assertEqual("sink", self.calls[0][2]["operation"])

    def test_inner_successful_diagnostic_suppresses_duplicate_nonzero_exit(
        self,
    ) -> None:
        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, None, "test", stream, "host")

        def callback() -> int:
            report_failure(
                None,
                FailureRecord("WARNING", "inner_failure", "safe failure"),
                component="APPEND_CHANGE_RECORDS",
                operation="append",
            )
            print("native output")
            return 2

        with (
            patch.object(boundary, "bound_selection", return_value=None),
            patch(
                f"{report_failure.__module__}.make_unbound_technical_logger",
                return_value=(logger, None),
            ),
            redirect_stdout(io.StringIO()) as stdout,
            redirect_stderr(io.StringIO()) as stderr,
        ):
            result = boundary.run_process(callback, operation="append")
        self.assertEqual(2, result)
        self.assertEqual("native output\n", stdout.getvalue())
        self.assertEqual("", stderr.getvalue())
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(1, len(records))
        self.assertEqual("inner_failure", records[0]["code"])

    def test_new_exception_after_prior_warning_is_not_deduplicated(
        self,
    ) -> None:
        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, None, "test", stream, "host")

        def prior() -> int:
            report_failure(
                None,
                FailureRecord("WARNING", "prior_warning", "safe warning"),
                component="TOOL",
                operation="prior",
            )
            return 0

        def current() -> int:
            raise RuntimeError("new secret")

        with (
            patch.object(boundary, "bound_selection", return_value=None),
            patch(
                f"{report_failure.__module__}.make_unbound_technical_logger",
                return_value=(logger, None),
            ),
            redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(0, boundary.run_process(prior, operation="prior"))
            self.assertEqual(
                2, boundary.run_process(current, operation="current")
            )
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(
            ["prior_warning", "internal_failure"],
            [record["code"] for record in records],
        )
        self.assertEqual(
            ["prior", "current"], [record["operation"] for record in records]
        )


if __name__ == "__main__":
    unittest.main()
