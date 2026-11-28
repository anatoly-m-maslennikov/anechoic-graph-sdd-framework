"""Exercise the existing MCP stdio entry point with native Workbench."""

import asyncio as asyncio
import hashlib
from pathlib import Path
import subprocess as subprocess
import sys
import tempfile
from unittest.mock import NonCallableMock
import unittest
from unittest.mock import patch

import httpx2 as httpx2
from mcp.client.session import ClientSession as ClientSession
from mcp.client.stdio import (
    StdioServerParameters as StdioServerParameters,
    stdio_client as stdio_client,
)
from mcp.client.streamable_http import (
    streamable_http_client as streamable_http_client,
)
import yaml


from .native_query_behavior_cases import NativeQueryBehaviorCases
from ..group_2.native_query_startup_cases import NativeQueryStartupCases
from ..group_2.native_query_projection_cases import NativeQueryProjectionCases
from .native_query_protocol_cases import NativeQueryProtocolCases
from ....native_query_test_support import create_native_gateway

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared import (
    validate_manifest,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared import (
    extension_directory,
    polling_source_watcher,
)


MCP = Path(__file__).resolve().parents[4]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"

CONTROL = ".anechoic_anechoic"
MANIFEST = "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md"
OLD_PATH = ".anechoic_legacy/03_plan/CA-P-9--old-task.md"
UNNUMBERED_PATH = ".anechoic_legacy/03_plan/archive/old-task.md"
STAGING_COPY_PATH = "migration-evidence/03_plan/old-task-copy.md"


def _native_inputs():
    from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryInputs

    return NativeQueryInputs(
        validate_manifest=validate_manifest,
        relation_types=frozenset({"CONTAINED_BY", "CONTAINS"}),
        inverses={"CONTAINED_BY": "CONTAINS"},
        extension_directory=extension_directory(MCP.parents[2]),
        ticket_labels=("Task", "Subtask", "Sub-epic", "Epic", "Version"),
    )


def _launch_server():
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import server_main

    with polling_source_watcher():
        return server_main(
            sys.argv[1:],
            gateway_factory=lambda root, control: create_native_gateway(
                root, control, _native_inputs()
            ),
        )


class NativeJournalOwnershipTests(unittest.TestCase):
    def test_rejects_journal_outside_selected_control(self):
        from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryOwner

        with tempfile.TemporaryDirectory() as root:
            for journal in (
                "_anechoic_other/_journal",
                ".anechoic_other/_journal",
            ):
                selection = NonCallableMock(
                    spec_set=["root", "control_relative", "parameters"],
                    root=Path(root).resolve(),
                    control_relative=Path("_anechoic_anechoic"),
                    parameters={"paths": {"journal_root": journal}},
                )
                with (
                    self.subTest(journal=journal),
                    self.assertRaisesRegex(ValueError, "another records tree"),
                ):
                    NativeQueryOwner(selection, None)
            selection.parameters["paths"]["journal_root"] = "elsewhere/journal"
            with (
                patch(
                    "KERNEL_MIXER_C59.native_query_runtime.SavedQueryStore"
                ) as saved,
                patch("KERNEL_MIXER_C59.native_query_runtime.WorkspaceStore"),
                patch("KERNEL_MIXER_C59.native_query_runtime.QueryLog"),
            ):
                NativeQueryOwner(selection, None)
                self.assertEqual(
                    "elsewhere/journal", saved.call_args.kwargs["journal_root"]
                )


def _write_native_fixtures(write):
    write(
        MANIFEST,
        "AN-S-001",
        "active",
        1,
        template="project_manifest",
        body="""
## Summary

Declare the native Project.

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name="Project Manifest", instance=ProjectManifest(name="Anechoic", prefix="AN"))
```
""",
    )
    write(
        "001_TICKETS/TASKS/AN-T-009-TASK--verify-runtime.md",
        "AN-T-009",
        "active",
        2,
        body="## Summary\n\nVerify the operator's runtime.\n",
    )
    write(
        "001_TICKETS/TASKS/archived/AN-T-009@1-TASK--verify-runtime.md",
        "AN-T-009",
        "archived",
        1,
    )
    write(
        "001_TICKETS/TASKS/draft/AN-T-009@3-draft-TASK--verify-runtime.md",
        "AN-T-009",
        "draft",
        3,
    )
    write("_PMETA/AN-P-001-WORKFLOW--fixture.md", "AN-P-001", "active", 1)


def _write_legacy_fixtures(root):
    legacy = root / OLD_PATH
    legacy.parent.mkdir(parents=True)
    legacy.write_text(
        "Legacy carrier held beside the selected native tree.\n",
        encoding="utf-8",
    )
    unnumbered = root / UNNUMBERED_PATH
    unnumbered.parent.mkdir()
    unnumbered.write_text(
        "## Summary\n\nArchived task with no legacy ID.\n",
        encoding="utf-8",
    )
    (root / ".anechoic_legacy" / "anechoic_project_settings.toml").write_text(
        '[project_mcp]\nhttp_port = 18000\ntool_blacklist = ["query_run"]\n',
        encoding="utf-8",
    )


def _structure_fixture_header(metadata, structure_tier):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        carriers.header.native_carrier_header__pub import (
        canonical_native_header,
    )

    metadata["context"]["tier"] = structure_tier
    metadata["context"].setdefault("lens", "DES")
    return canonical_native_header(metadata)


class NativeQueryStdioTests(
    NativeQueryProtocolCases,
    NativeQueryProjectionCases,
    NativeQueryStartupCases,
    NativeQueryBehaviorCases,
    unittest.IsolatedAsyncioTestCase,
):
    def setUp(self):
        self.enterContext(polling_source_watcher())
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        _write_native_fixtures(self._write)
        _write_legacy_fixtures(self.root)
        self.args = [
            "-B",
            "-P",
            "-m",
            (
                "MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests."
                "test_native_query_stdio"
            ),
            "--project-root",
            str(self.root),
            "--control-root",
            CONTROL,
        ]

    def _write(
        self,
        relative,
        atom_id,
        status,
        version,
        *,
        template="task",
        body="## Summary\n\nFixture.\n",
        container=None,
        tier=None,
        lens=None,
        structure_tier=None,
        label=None,
    ):
        path = self.root / CONTROL / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "identity": {"atom_id": atom_id},
            "context": {
                "container": container or {"component": "C0"},
                "template": template,
                "tier": tier
                if tier is not None
                else -1
                if template == "project_manifest"
                else 0,
            },
            "state": {
                "version": version,
                "status": status,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        if label is not None:
            metadata["context"]["label"] = label
        if lens:
            metadata["context"]["lens"] = lens
        if structure_tier is not None:
            metadata = _structure_fixture_header(metadata, structure_tier)
        path.write_text(
            f"---\n{yaml.safe_dump(metadata)}---\n\n{body}", encoding="utf-8"
        )

    def _carrier_digests(self):
        return {
            path.relative_to(self.root): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in self.root.rglob("*")
            if path.is_file()
            and path.relative_to(self.root).parts[0]
            not in {".anechoic_runtime", ".anechoic_tmp"}
        }


if __name__ == "__main__":
    raise SystemExit(_launch_server())
