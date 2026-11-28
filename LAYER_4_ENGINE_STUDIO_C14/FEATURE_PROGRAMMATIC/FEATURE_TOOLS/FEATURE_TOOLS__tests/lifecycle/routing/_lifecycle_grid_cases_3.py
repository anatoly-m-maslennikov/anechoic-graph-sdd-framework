"""Generated lifecycle grid scenario helpers."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_placement__pub import (
    native_carrier_path,
)


class LifecycleGridCases3:
    def _check_grid_result(
        self,
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
    ):
        family, template, situation, contained, route = (
            case[k]
            for k in ("family", "template", "situation", "contained", "route")
        )
        root = project.root
        saved, saved_path = self._grid_saved_result(result, expected, root)
        expected_ref, expected_version, expected_status = (
            self._assert_grid_identity(case, saved, atom_id, status)
        )
        self._assert_grid_effects(case, result, saved)
        self._check_grid_carrier(
            case,
            saved,
            saved_path,
            expected_ref,
            expected_version,
            expected_status,
            project,
            component,
            owner_dir,
            container,
            body,
            changed,
            before,
            project_specs,
        )

    def _grid_saved_result(self, result, expected, root):
        self.assertTrue(expected, result)
        self.assertEqual("completed", result["outcome"], result)
        self.assertTrue(result["effects"], result)
        saved = result.get("savedDraft") or result["artifact"]
        saved_path = root / saved["path"]
        self.assertTrue(saved_path.is_file())
        return saved, saved_path

    def _assert_grid_identity(self, case, saved, atom_id, status):
        family, template, situation, contained, route = (
            case[k]
            for k in ("family", "template", "situation", "contained", "route")
        )
        expected_version = (
            2
            if (
                situation == "current"
                and route in {"create_draft", "update"}
                or family == "PROJECT_CONFIG"
                and situation == "draft"
                and template is not None
                and not contained
            )
            else 1
        )
        self.assertEqual(atom_id, saved["atom_id"])
        self.assertEqual(expected_version, saved["version"])
        expected_status = self._grid_saved_status(case, status)
        self.assertEqual(expected_status, saved["status"].lower())
        expected_ref = (
            f"{saved['atom_id']}@{expected_version}-draft"
            if expected_status == "draft"
            else f"{saved['atom_id']}@{expected_version}"
            if expected_status == "archived"
            else saved["atom_id"]
        )
        self.assertEqual(expected_ref, saved["ref_id"])
        return expected_ref, expected_version, expected_status

    def _grid_saved_status(self, case, status):
        family, situation, route = (
            case[k] for k in ("family", "situation", "route")
        )
        expected_status = (
            "draft"
            if route in {"create_draft", "update"}
            else "in_queue"
            if route == "create_asset"
            else {
                "TKT": "backlog",
                "SPEC": "ready",
                "PROJECT_CONFIG": "active",
            }[family]
            if route == "promote_draft"
            else status
            if route == "change_status"
            else "archived"
            if route == "archive"
            else "draft"
            if situation == "draft"
            else "in_queue"
        )
        return expected_status

    def _assert_grid_effects(self, case, result, saved):
        family, route = case["family"], case["route"]
        operations = [
            effect["operation"]
            for effect in result["effects"]
            if effect.get("evidence") != "directory"
        ]
        expected_operations = (
            ["create"]
            if route in {"create_draft", "update", "create_asset"}
            else ["modify"]
            if route == "direct_update"
            else ["create", "modify", "remove"]
            if family == "PROJECT_CONFIG" and route == "promote_draft"
            else ["create", "remove"]
        )
        self.assertEqual(expected_operations, operations)
        self.assertTrue(
            any(
                effect["target"] == saved["path"]
                for effect in result["effects"]
            )
        )

    def _check_grid_carrier(
        self,
        case,
        saved,
        saved_path,
        expected_ref,
        expected_version,
        expected_status,
        project,
        component,
        owner_dir,
        container,
        body,
        changed,
        before,
        project_specs,
    ):
        family, template, situation, route = (
            case[k] for k in ("family", "template", "situation", "route")
        )
        contained = case["contained"]
        control = project.control_root
        row = self._grid_capture_row(project, expected_ref, expected_version)
        self.assertEqual(saved["path"], row["source_path"])
        derived = native_carrier_path(
            row["header_json"],
            "Example",
            project_root=control,
            owner_directory=owner_dir
            if contained
            else component
            if family == "SPEC" and container == {"component": "C9"}
            else control,
            owner_template="task" if contained else None,
        )
        self.assertEqual(derived, saved_path)
        self.assertEqual(expected_status, row["status"])
        if family == "SPEC" and template in project_specs:
            self.assertEqual(
                0 if template in {"axiom", "project_contract"} else 2,
                row["header_json"]["tier"],
            )
        self._assert_grid_content(case, row, changed, body, before, project)

    def _grid_capture_row(self, project, expected_ref, expected_version):
        after = capture_native(project)
        self.assertFalse(after.errors, after.errors)
        exact_ref = (
            expected_ref
            if "@" in expected_ref
            else f"{expected_ref}@{expected_version}"
        )
        row = next(
            row for row in after.atoms if row["_exact_ref"] == exact_ref
        )
        return row

    def _assert_grid_content(self, case, row, changed, body, before, project):
        situation, route = case["situation"], case["route"]
        self.assertEqual(
            (
                changed
                if route in {"direct_update", "update", "create_draft"}
                and situation != "new"
                else body
            ).encode(),
            row["_content_bytes"],
        )
        self.assertNotEqual(before, self.files(project))
