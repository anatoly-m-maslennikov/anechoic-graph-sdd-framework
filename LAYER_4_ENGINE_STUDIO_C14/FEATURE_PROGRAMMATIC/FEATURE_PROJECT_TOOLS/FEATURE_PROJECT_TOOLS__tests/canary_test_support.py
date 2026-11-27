"""Support assertions and process fixtures for release canary tests."""

from pathlib import Path
from subprocess import TimeoutExpired
from unittest.mock import NonCallableMock

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    _release_canary as release_canary,
)


def assert_failed_queries(self, query):
    for failed in (
        NonCallableMock(
            spec_set=["is_error", "structured_content"],
            is_error=True,
            structured_content={"rows": [[1]]},
        ),
        NonCallableMock(
            spec_set=["is_error", "structured_content"],
            is_error=False,
            structured_content={"rows": []},
        ),
        NonCallableMock(
            spec_set=["is_error", "structured_content"],
            is_error=False,
            structured_content=None,
        ),
    ):
        with self.subTest(failed=failed):
            query.return_value = failed
            self.assertFalse(release_canary._mcp_ready(54321, 2.0))


def startup_run(self, calls, deadline_mode, log_timeout, argv, **kwargs):
    calls.append(argv)
    if argv[1] == "port":
        self.assertEqual(
            30 if deadline_mode == "1" else None, kwargs["timeout"]
        )
        return NonCallableMock(spec_set=["stdout"], stdout="127.0.0.1:54321\n")
    if argv[1] == "container":
        return NonCallableMock(spec_set=["stdout"], stdout="false\n")
    if argv[1] == "logs":
        self.assertEqual(5, kwargs["timeout"])
        if log_timeout:
            raise TimeoutExpired(argv, kwargs["timeout"])
        return NonCallableMock(
            spec_set=["stdout", "stderr"],
            stdout="a" * 9000 + "startup context",
            stderr="startup error\n",
        )


def retry_run(self, calls, selection, settings, argv, **kwargs):
    calls.append(argv)
    if argv[1] == "run":
        cidfile = Path(argv[argv.index("--cidfile") + 1])
        self.assertEqual(0o700, cidfile.parent.stat().st_mode & 0o777)
        copied = cidfile.parent / "canary-project"
        self.assertTrue((copied / "candidate").is_file())
        self.assertTrue((copied / selection["manifest_path"]).is_file())
        self.assertEqual(
            settings, (copied / release_canary._RUNTIME_SETTINGS).read_bytes()
        )
        cidfile.write_text("b" * 64)
        return NonCallableMock(spec_set=["stdout"], stdout="")
    if argv[1] == "logs":
        return NonCallableMock(
            spec_set=["stdout", "stderr"], stdout="", stderr=""
        )
    return NonCallableMock(spec_set=["stdout"], stdout="127.0.0.1:54321\n")
