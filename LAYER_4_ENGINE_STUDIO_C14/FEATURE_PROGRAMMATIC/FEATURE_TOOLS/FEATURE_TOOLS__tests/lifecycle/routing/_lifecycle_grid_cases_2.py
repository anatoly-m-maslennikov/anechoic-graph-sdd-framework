"""Generated lifecycle grid scenario helpers."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    NATIVE_LIFECYCLE__shared import (
    execute_native_lifecycle,
)

from .asset_routes._lifecycle_spec_asset_cases_1 import ProjectSpecFixtureModel


class LifecycleGridCases2:
    def _grid_arguments(self, case, atom_id, container, body, changed):
        family, template, situation, contained, route = (
            case[k]
            for k in ("family", "template", "situation", "contained", "route")
        )
        version = (
            2
            if family == "PROJECT_CONFIG"
            and situation == "draft"
            and template is not None
            and not contained
            else 1
        )
        ref = atom_id + (
            {"draft": f"@{version}-draft", "archived": "@1"}.get(situation, "")
        )
        target = {"ref_id": ref, "version": version}
        values = {"template": template, "container": container, "body": body}
        if family == "SPEC":
            values["lens"] = "SPEC"
        return self._grid_route_arguments(
            case, family, template, situation, route, values, target, changed
        )

    def _grid_route_arguments(
        self, case, family, template, situation, route, values, target, changed
    ):
        status = None
        if route in {"create_draft", "update"}:
            args = (
                {"newAtom": values}
                if situation == "new"
                else {"sourceCurrent": target, "changes": {"body": changed}}
            )
        elif route == "create_asset":
            args = (
                {"newAtom": values}
                if situation == "new"
                else {"target": target}
            )
        elif route == "direct_update":
            args = {"target": target, "changes": {"body": changed}}
        elif route == "promote_draft":
            args = {
                "target": target,
                "targetStatus": {
                    "TKT": "backlog",
                    "SPEC": "ready",
                    "PROJECT_CONFIG": "active",
                }[family],
            }
        elif route == "change_status":
            status = self._grid_change_status(case, family, template)
            args = {"target": target, "targetStatus": status}
        else:
            args = {"target": target}
        return args, status

    def _grid_change_status(self, case, family, template):
        status = case.get(
            "target_status",
            "active"
            if family == "SPEC"
            else (
                "resolved"
                if template
                in {
                    "problem",
                    "question",
                    "code_spec_mismatch",
                    "opportunity",
                }
                else "done"
            ),
        )
        return status

    def _run_grid_case(
        self, case, directory, body, changed, assets, project_specs
    ):
        (
            project,
            component,
            snapshot,
            owner_dir,
            container,
            atom_id,
            capture,
            before,
            args,
            status,
            expected,
            route,
        ) = self._prepare_grid_case(
            case, directory, body, changed, assets, project_specs
        )
        result = self._execute_grid_case(
            project, route, args, capture, snapshot
        )
        if result["outcome"] != "completed":
            return self._assert_grid_rejected(
                result, expected, before, project
            )
        self._check_grid_result(
            case,
            result,
            project,
            component,
            owner_dir,
            container,
            body,
            changed,
            before,
            atom_id,
            status,
            project_specs,
            expected,
        )
        return "accepted"

    def _prepare_grid_case(
        self, case, directory, body, changed, assets, project_specs
    ):
        family, template, contained, route = (
            case[k] for k in ("family", "template", "contained", "route")
        )
        project, component, snapshot, owner_dir = self._grid_project(
            directory, body
        )
        container = (
            {"atom": "AN-T-1"}
            if contained
            else {
                "component": "C00"
                if template in project_specs
                or template == "project_manifest"
                or family != "SPEC"
                else "C9"
            }
        )
        atom_id = self._grid_carrier(
            case, project, component, owner_dir, container, body
        )
        capture = capture_native(project)
        self.assertFalse(capture.errors, capture.errors)
        before = self.files(project)
        args, status = self._grid_arguments(
            case, atom_id, container, body, changed
        )
        expected = self._grid_expected(case, assets, project_specs)
        return (
            project,
            component,
            snapshot,
            owner_dir,
            container,
            atom_id,
            capture,
            before,
            args,
            status,
            expected,
            route,
        )

    def _execute_grid_case(self, project, route, args, capture, snapshot):
        model = ProjectSpecFixtureModel(lambda *args: None)
        return execute_native_lifecycle(
            project,
            "atom_lifecycle_" + route,
            args,
            capture,
            None,
            previous_capture=None,
            ticket_labels=(),
            validate_project_spec=model.validate,
            admitted_structure=snapshot,
        )

    def _assert_grid_rejected(self, result, expected, before, project):
        self.assertFalse(expected, result)
        self.assertFalse(result["effects"], result)
        if result["outcome"] == "needs_input":
            self.assertTrue(result["requested_input"], result)
        else:
            self.assertEqual("failed", result["outcome"], result)
            self.assertEqual(
                ["source_changed"],
                [item["code"] for item in result["errors"]],
            )
        self.assertEqual(before, self.files(project))
        return "rejected"
