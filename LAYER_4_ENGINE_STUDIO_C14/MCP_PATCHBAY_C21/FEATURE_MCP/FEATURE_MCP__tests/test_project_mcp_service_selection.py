"""Service-scoped Docker roster selection for the Project MCP backend."""

import json
from pathlib import Path
import unittest
from unittest.mock import NonCallableMock
from unittest.mock import patch


APP = Path(__file__).resolve().parents[1]

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (  # noqa: E402
    HEALTH_PATH,
    MCP_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import BackendError  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.docker__shared import (  # noqa: E402
    ProjectMcpBackend,
)


_WORKER_ID = "1" * 64
_MCP_ID = "2" * 64
_SECOND_MCP_ID = "3" * 64


class ProjectMcpServiceSelectionTests(unittest.TestCase):
    def _selection(self, root: Path):
        return NonCallableMock(
            spec_set=["root", "control_relative", "instance_id"],
            root=root,
            control_relative=Path("control"),
            instance_id="a" * 64,
        )

    def _row(self, selection, identifier: str) -> dict[str, object]:
        return {
            "Id": identifier,
            "Image": "sha256:" + "b" * 64,
            "Config": {
                "Labels": {
                    "org.anechoic.project": selection.instance_id,
                    "org.anechoic.service": "mcp-http",
                    "org.anechoic.control_root": "control",
                    "org.anechoic.host_project_root": str(selection.root),
                }
            },
            "State": {"Status": "running", "Health": {"Status": "healthy"}},
            "NetworkSettings": {"Ports": {}},
            "Mounts": [
                {
                    "Type": "volume",
                    "Name": "anechoic-framework-db",
                    "Destination": "/var/lib/anechoic",
                    "RW": True,
                },
                {
                    "Type": "bind",
                    "Source": str(selection.root),
                    "Destination": "/project",
                },
            ],
        }

    def _docker_roster(
        self, selection, mcp_identifiers: list[str], *, foreign_project=False
    ):
        def run(argv, *, timeout, env):
            if argv[:3] == ["docker", "ps", "--all"]:
                service_filter = "label=org.anechoic.service=mcp-http"
                identifiers = (
                    mcp_identifiers
                    if service_filter in argv
                    else [_WORKER_ID, *mcp_identifiers]
                )
                return "\n".join(identifiers)
            if argv[:3] == ["docker", "container", "inspect"]:
                if argv[-1] == _WORKER_ID:
                    self.fail(
                        "worker must not be inspected as the MCP service"
                    )
                row = self._row(selection, argv[-1])
                if foreign_project:
                    row["Config"]["Labels"]["org.anechoic.project"] = "f" * 64
                return json.dumps(row)
            self.fail(f"unexpected Docker command: {argv!r}")

        return run

    def test_inspect_selects_mcp_service_from_shared_project_roster(
        self,
    ) -> None:
        selection = self._selection(APP)
        with patch(
            (
                "MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend._boun"
                "ded_run"
            ),
            side_effect=self._docker_roster(selection, [_MCP_ID]),
        ):
            rows = ProjectMcpBackend().inspect(selection)
        self.assertEqual([_MCP_ID], [row["Id"] for row in rows])

    def test_inspect_ignores_worker_only_project_roster(self) -> None:
        selection = self._selection(APP)
        with patch(
            (
                "MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend._boun"
                "ded_run"
            ),
            side_effect=self._docker_roster(selection, []),
        ):
            rows = ProjectMcpBackend().inspect(selection)
        self.assertEqual([], rows)

    def test_inspect_refuses_duplicate_mcp_services(self) -> None:
        selection = self._selection(APP)
        with patch(
            (
                "MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend._boun"
                "ded_run"
            ),
            side_effect=self._docker_roster(
                selection, [_MCP_ID, _SECOND_MCP_ID]
            ),
        ):
            with self.assertRaises(BackendError) as raised:
                ProjectMcpBackend().inspect(selection)
        self.assertEqual("DOCKER_PUBLICATION_FAILED", raised.exception.code)

    def test_inspect_refuses_foreign_project_row(self) -> None:
        selection = self._selection(APP)
        with patch(
            (
                "MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend._boun"
                "ded_run"
            ),
            side_effect=self._docker_roster(
                selection,
                [_MCP_ID],
                foreign_project=True,
            ),
        ):
            with self.assertRaises(BackendError) as raised:
                ProjectMcpBackend().inspect(selection)
        self.assertEqual("RUNTIME_MISMATCH", raised.exception.code)

    def test_health_admits_only_the_canonical_mcp_path(self) -> None:
        observed = []

        async def initialize(url, timeout):
            observed.append((url, timeout))

        backend = ProjectMcpBackend()
        with patch.object(
            ProjectMcpBackend, "_initialize", new=staticmethod(initialize)
        ):
            self.assertTrue(
                backend.health(f"http://127.0.0.1:8092{MCP_PATH}", 1)
            )
        self.assertEqual([(f"http://127.0.0.1:8092{MCP_PATH}", 1.0)], observed)
        self.assertFalse(backend.health("http://127.0.0.1:8092/mcp", 1))

    def test_launch_probe_refuses_pending_health_before_mcp_handshake(
        self,
    ) -> None:
        import httpx2

        def respond(request):
            self.assertEqual(HEALTH_PATH, request.url.path)
            return httpx2.Response(200, json={"state": "pending"})

        client = httpx2.AsyncClient(transport=httpx2.MockTransport(respond))
        with (
            patch.object(httpx2, "AsyncClient", return_value=client),
            patch(
                "mcp.client.streamable_http.streamable_http_client"
            ) as handshake,
        ):
            self.assertFalse(
                ProjectMcpBackend().health(
                    f"http://127.0.0.1:8092{MCP_PATH}", 1
                )
            )
            handshake.assert_not_called()


if __name__ == "__main__":
    unittest.main()
