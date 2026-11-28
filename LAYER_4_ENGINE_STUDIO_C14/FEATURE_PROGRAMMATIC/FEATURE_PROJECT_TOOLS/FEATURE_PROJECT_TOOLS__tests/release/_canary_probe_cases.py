"""Check that the candidate probe isolates and removes its own container."""

from errno import ENOTEMPTY
import io
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import NonCallableMock
from unittest.mock import AsyncMock, patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    _release_canary as release_canary,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import (
    test_suite__shared as suite,
)
from .canary_test_support import (
    assert_failed_queries,
)


class CanaryProbeCases:
    def test_cleanup_recovers_only_late_regular_finder_metadata(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        sentinel = root / "sentinel"
        sentinel.write_text("preserve")
        remove_directory = release_canary.os.rmdir
        for entry in ("metadata", "symlink", "unexpected"):
            self._cleanup_entry(root, sentinel, remove_directory, entry)
        self.assertEqual("preserve", sentinel.read_text())

    def _cleanup_entry(self, root, sentinel, remove_directory, entry):
        folders = []
        injected = False

        def verify(
            _root,
            _selection,
            _package,
            attempt,
            _image,
            *,
            skip_archives=False,
        ):
            folder = attempt / "canary-project" / "ontology"
            folder.mkdir(parents=True)
            folders.append(folder)
            return "endpoint"

        def rmdir(path, **kwargs):
            nonlocal injected
            if Path(path).name == "ontology" and not injected:
                injected = True
                name = "unexpected" if entry == "unexpected" else ".DS_Store"
                late = folders[0] / name
                if entry == "symlink":
                    late.symlink_to(sentinel)
                else:
                    late.touch()
            return remove_directory(path, **kwargs)

        with (
            self.subTest(entry=entry),
            patch.object(release_canary, "_workspace", return_value=root),
            patch.object(release_canary, "_selection"),
            patch.object(release_canary, "_verify_manifest"),
            patch.object(
                release_canary,
                "_verify_candidate_image",
                side_effect=verify,
            ),
            patch.object(release_canary.subprocess, "run"),
            patch.object(release_canary.os, "rmdir", new=rmdir),
        ):
            self._assert_cleanup_entry(root, entry, folders)

    def _assert_cleanup_entry(self, root, entry, folders):
        args = (root, root / "package", "sha256:" + "c" * 64)
        if entry == "metadata":
            self.assertEqual(
                "endpoint",
                release_canary.verify_candidate_image(
                    *args, run_id="scope", selection={}
                ),
            )
            self.assertFalse(folders[0].parent.parent.exists())
        else:
            with self.assertRaises(OSError) as caught:
                release_canary.verify_candidate_image(
                    *args, run_id="scope", selection={}
                )
            self.assertEqual(ENOTEMPTY, caught.exception.errno)
            self.assertTrue(folders[0].exists())

    def test_cleanup_failure_preserves_primary_canary_failure(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        failure = release_canary.CanaryError("canary probe failed")
        with (
            patch.object(release_canary, "_workspace", return_value=root),
            patch.object(release_canary, "_selection"),
            patch.object(release_canary, "_verify_manifest"),
            patch.object(
                release_canary, "_verify_candidate_image", side_effect=failure
            ),
            patch.object(release_canary.subprocess, "run"),
            patch.object(
                release_canary.shutil,
                "rmtree",
                side_effect=OSError("cleanup failed"),
            ),
            self.assertRaises(release_canary.CanaryError) as caught,
        ):
            release_canary.verify_candidate_image(
                root,
                root / "package",
                "sha256:" + "c" * 64,
                run_id="scope",
                selection={},
            )
        self.assertIs(failure, caught.exception)
        self.assertIn("cleanup failed", failure.__notes__[0])

    def test_mcp_probe_requires_a_working_query_on_the_loopback_port(self):
        with (
            patch("httpx2.AsyncClient") as client,
            patch(
                "mcp.client.streamable_http.streamable_http_client"
            ) as transport,
            patch("mcp.client.session.ClientSession") as session,
        ):
            streams = (object(), object())
            transport.return_value.__aenter__.return_value = streams
            initialize = AsyncMock()
            session.return_value.__aenter__.return_value.initialize = (
                initialize
            )
            query = AsyncMock(
                return_value=NonCallableMock(
                    spec_set=["is_error", "structured_content"],
                    is_error=False,
                    structured_content={"rows": [[1]]},
                )
            )
            session.return_value.__aenter__.return_value.call_tool = query
            self.assertTrue(release_canary._mcp_ready(54321, 2.0))
            client.assert_called_once_with(
                trust_env=False, follow_redirects=False, timeout=2.0
            )
            transport.assert_called_once_with(
                "http://127.0.0.1:54321/anechoic/mcp",
                http_client=client.return_value.__aenter__.return_value,
            )
            session.assert_called_once_with(*streams)
            initialize.assert_awaited_once_with()
            query.assert_awaited_once_with(
                "query_run",
                {
                    "sql": "SELECT 1 AS ready FROM framework.atoms LIMIT 1",
                    "result_delivery": "inline",
                    "result_format": "json_matrix",
                },
            )
            assert_failed_queries(self, query)
            self._assert_ping_and_failed_initialization(
                session, query, initialize
            )

    def _assert_ping_and_failed_initialization(
        self, session, query, initialize
    ):
        ping = AsyncMock()
        session.return_value.__aenter__.return_value.send_ping = ping
        query.reset_mock()
        self.assertTrue(
            release_canary._mcp_ready(54321, 2.0, query_enabled=False)
        )
        ping.assert_awaited_once_with()
        query.assert_not_awaited()
        initialize.side_effect = RuntimeError("could not initialize")
        self.assertFalse(release_canary._mcp_ready(54321, 2.0))

    def test_cli_reports_endpoint_and_rejects_missing_arguments(self):
        image = "sha256:" + "c" * 64
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        argv = [
            "suite",
            "--phase",
            "image",
            "--candidate-image",
            image,
            "--project-root",
            str(root),
            "--canary-package",
            "/tmp/package",
            "--run-id",
            "session-1",
            "--canary-selection",
            "{}",
        ]
        output = io.StringIO()
        order = []
        with (
            patch.object(sys, "argv", argv),
            patch("sys.stdout", output),
            patch("sys.stderr", new_callable=io.StringIO),
            patch.object(
                suite,
                "run_full_suite",
                side_effect=lambda *a, **k: order.append("suite") or 0,
            ) as run,
            patch.object(
                release_canary,
                "verify_candidate_image",
                side_effect=lambda *a, **k: (
                    order.append("canary")
                    or "http://127.0.0.1:54321/anechoic/mcp"
                ),
            ) as canary,
        ):
            self.assertEqual(0, suite.main())
        self._assert_cli_success(root, image, output, order, run, canary)
        self._assert_cli_failures(argv, root)

    def _assert_cli_success(self, root, image, output, order, run, canary):
        self.assertEqual(["suite", "canary"], order)
        self.assertEqual("image", run.call_args.kwargs["phase"])
        self.assertEqual(image, run.call_args.kwargs["candidate_image"])
        canary.assert_called_once()
        self.assertEqual(
            "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:54321/anechoic/mcp\n",
            output.getvalue(),
        )
        (report,) = (root / ".anechoic_tmp/test_reports").glob("*.json")
        payload = json.loads(report.read_text())
        self.assertEqual("passed", payload["status"])
        self.assertEqual(
            "http://127.0.0.1:54321/anechoic/mcp", payload["canary_endpoint"]
        )

    def _assert_cli_failures(self, argv, root):
        with (
            patch.object(sys, "argv", argv),
            patch.object(suite, "run_full_suite", return_value=1),
            patch("sys.stderr", new_callable=io.StringIO),
            patch.object(release_canary, "verify_candidate_image") as canary,
        ):
            self.assertEqual(1, suite.main())
            canary.assert_not_called()
        with (
            patch.object(
                sys,
                "argv",
                ["suite", "--phase", "image", "--project-root", str(root)],
            ),
            patch("sys.stderr", io.StringIO()),
        ):
            self.assertEqual(1, suite.main())
