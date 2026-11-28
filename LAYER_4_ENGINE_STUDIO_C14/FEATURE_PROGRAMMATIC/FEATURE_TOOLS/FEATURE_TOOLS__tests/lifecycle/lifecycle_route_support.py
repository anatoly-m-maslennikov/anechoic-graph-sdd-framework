"""Generated native lifecycle paths; each case uses a fresh project."""

from hashlib import sha256
from pathlib import Path
import sys
import tempfile

import yaml

import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.drafts.test_native_lifecycle_draft as fixtures
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    NativeProjectSelection,
)

TOOLS = Path(__file__).resolve().parents[2]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / "IWE_CONSOLE_C43")]


class LifecycleRouteSupport:
    def project(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / ".git").mkdir()
        control = root / ".anechoic_test"
        control.mkdir()
        manifest = control / "AN-S-1-PROJECT_MANIFEST--manifest.md"
        owner = control / "001_TICKETS/TASKS/AN-T-1-TASK--owner.md"
        owner.parent.mkdir(parents=True)
        for path, identity, template in (
            (manifest, "AN-S-1", "project_manifest"),
            (owner, "AN-T-1", "task"),
        ):
            header = {
                "identity": {"atom_id": identity},
                "context": {
                    "container": {"component": "C00"},
                    "template": template,
                },
                "state": {
                    "status": "active",
                    "version": 1,
                    "updated_at": "2026-01-01",
                },
            }
            path.write_text(
                "---\n"
                + yaml.safe_dump(header)
                + "---\n\n## Summary\n\nOwner\n"
            )
        return NativeProjectSelection(
            root=root,
            control_root=control,
            control_relative=control.relative_to(root),
            instance_id="a" * 64,
            project_name="Test",
            project_prefix="AN",
            manifest_path=manifest,
            manifest_ref="AN-S-1@1",
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )

    def files(self, project):
        return {
            p.relative_to(project.root): p.read_bytes()
            for p in project.control_root.rglob("*")
            if p.is_file()
        }

    write = fixtures.NativeDraftTests.write

    def _grid_expected(self, case, assets, project_specs):
        family, template, situation, contained, route = (
            case[key]
            for key in (
                "family",
                "template",
                "situation",
                "contained",
                "route",
            )
        )
        if family == "TKT":
            return self._grid_ticket_route(
                case, assets, route, template, situation
            )
        if contained:
            return False
        if family == "PROJECT_CONFIG":
            return template is not None and (
                route in {"create_draft", "update"}
                and situation == "current"
                or route == "promote_draft"
                and situation == "draft"
            )
        return family == "SPEC" and self._grid_spec_route(
            route, template, situation, project_specs
        )

    def _grid_ticket_route(self, case, assets, route, template, situation):
        if route == "change_status" and situation == "current":
            return self._grid_ticket_transition_supported(case)
        return (
            route == "create_draft"
            and situation in {"new", "current"}
            and template in {"task", "epic"}
            or route == "update"
            and situation == "current"
            and template in {"task", "epic"}
            or route == "create_asset"
            and situation == "new"
            and template in assets
            or route == "direct_update"
            and situation in {"current", "draft"}
            and template in assets
            or route == "promote_draft"
            and situation == "draft"
            and template in {"task", "epic"}
        )

    @staticmethod
    def _grid_spec_route(route, template, situation, project_specs):
        return (
            route == "create_draft"
            and situation == "new"
            and template in project_specs
            or route in {"create_draft", "update", "change_status"}
            and situation == "current"
            and template not in {"project_manifest", "component_contract"}
            or route == "promote_draft"
            and situation == "draft"
            and template in {None} | project_specs
            or route == "archive"
            and (
                situation == "draft"
                or situation == "current"
                and template != "project_manifest"
            )
        )

    def _grid_ticket_transition_supported(self, case):
        template = case["template"]
        source = case.get("source_status", "in_queue")
        target = case.get(
            "target_status",
            "resolved"
            if template
            in {"problem", "question", "code_spec_mismatch", "opportunity"}
            else "done",
        )
        if template in {"task", "epic"}:
            return (
                source == "backlog"
                and target == "in_queue"
                or source in {"in_queue", "active"}
                and target in {"done", "canceled"}
                or source == "active"
                and target == "in_queue"
            )
        if template in {
            "problem",
            "question",
            "code_spec_mismatch",
            "opportunity",
        }:
            return (
                source == "backlog"
                and target == "in_queue"
                or source in {"in_queue", "active"}
                and target in {"resolved", "canceled"}
                or source == "active"
                and target == "in_queue"
            )
        return template in {
            "analysis_report",
            "work_report",
            "work_log",
            "spec_proposal",
        } and (
            target == "done"
            or not case["contained"]
            and source == "in_queue"
            and target == "complete"
        )
