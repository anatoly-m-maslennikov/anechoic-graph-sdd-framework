"""Native project SPEC and asset route scenarios."""

from dataclasses import replace
from hashlib import sha256
import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_placement__pub import (
    native_carrier_path,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
    SourceChanged,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_spec_archive import (
    archive_spec_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_update_spec__shared import (
    change_spec_status,
)
import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.drafts.test_native_lifecycle_draft as fixtures
from ._lifecycle_spec_asset_cases_1 import ProjectSpecFixtureModel


class LifecycleSpecAssetCases2:
    def test_project_spec_templates_and_draft_archive(self):
        for template in ("axiom", "applicable_principle"):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    self._check_project_spec_template(template, contained)

    def test_project_spec_checks_candidate_status_before_writing(self):
        project = self._candidate_status_project()
        values = {
            "template": "axiom",
            "container": {"component": "C00"},
            "lens": "SPEC",
            "body": "\n## Summary\n\nExample\n",
        }

        def reject(template, header, owner, body):
            if header["state"]["status"] != "draft":
                raise ValueError("Status is not enabled")

        def publish(draft, validate):
            target = {"ref_id": draft["ref_id"], "version": draft["version"]}
            return promote_draft(
                project,
                {"target": target, "targetStatus": "ready"},
                current_rows=capture_native(project).atoms,
                validate_project_spec_model=validate,
            )

        allow = ProjectSpecFixtureModel(lambda *_: None).validate
        reject_model = ProjectSpecFixtureModel(reject).validate
        first = create_draft(
            project,
            {"newAtom": values},
            current_rows=capture_native(project).atoms,
            validate_project_spec_model=allow,
        )["savedDraft"]
        before = self.files(project)
        with self.assertRaisesRegex(InputError, "Status is not enabled"):
            publish(first, reject_model)
        self.assertEqual(before, self.files(project))

        self._assert_rejected_current_status(
            project, first, allow, reject_model, publish
        )

    def _candidate_status_project(self):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        project.manifest_path.write_text(
            project.manifest_path.read_text().replace(
                "component: C0}", "component: C00}"
            )
        )
        return replace(
            project,
            manifest_sha256=sha256(
                project.manifest_path.read_bytes()
            ).hexdigest(),
        )

    def _assert_rejected_current_status(
        self, project, first, allow, reject, publish
    ):
        ready = publish(first, allow)["artifact"]
        target = {"ref_id": ready["ref_id"], "version": ready["version"]}
        revision = create_draft(
            project,
            {"sourceCurrent": target},
            current_rows=capture_native(project).atoms,
            validate_project_spec_model=allow,
        )
        before = self.files(project)
        with self.assertRaisesRegex(InputError, "Status is not enabled"):
            publish(revision["savedDraft"], reject)
        with self.assertRaisesRegex(InputError, "Status is not enabled"):
            change_spec_status(
                project,
                {"target": target, "targetStatus": "active"},
                current_rows=capture_native(project).atoms,
                validate_project_spec_model=reject,
            )
        self.assertEqual(before, self.files(project))

    def test_archive_rejects_manifest_property_with_a_plain_des_filename(self):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        owner = project.control_root / "META_ONTOLOGY_C9"
        header = canonical_native_header(
            {
                "identity": {"atom_id": "AN-S-2"},
                "context": {
                    "container": {"component": "C9"},
                    "tier": 4,
                    "lens": "DES",
                    "template": "manifest_property",
                },
                "state": {
                    "status": "active",
                    "version": 1,
                    "updated_at": "2026-01-01",
                },
            }
        )
        canonical = native_carrier_path(
            header,
            "Example",
            project_root=project.control_root,
            owner_directory=owner,
        )
        path = canonical.with_name("AN-S-2-DES--example.md")
        path.parent.mkdir(parents=True)
        path.write_text(
            "---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n"
        )
        before = self.files(project)
        capture = capture_native(project)
        with self.assertRaisesRegex(InputError, "path disagrees"):
            change_spec_status(
                project,
                {
                    "target": {"ref_id": "AN-S-2", "version": 1},
                    "targetStatus": "archived",
                },
                current_rows=capture.atoms,
                previous_capture=capture,
            )
        self.assertEqual(before, self.files(project))

    def _check_project_spec_template(self, template, contained):
        self.selection = project = self._candidate_status_project()

        def rows():
            return capture_native(project).atoms

        calls = []

        def observe(kind, header, component, body):
            calls.append((kind, component, body))

        validate = ProjectSpecFixtureModel(observe).validate
        values = {
            "template": template,
            "container": {"atom": "AN-T-1"}
            if contained
            else {"component": "C00"},
            "lens": "SPEC",
            "body": "\n## Summary\n\nExample\n",
        }
        before = self.files(project)
        if contained:
            with self.assertRaises(InputError):
                create_draft(
                    project,
                    {"newAtom": values},
                    current_rows=rows(),
                    validate_project_spec_model=validate,
                )
            self.assertEqual(before, self.files(project))
            return
        self._check_spec_lifecycle(
            project, template, values, rows, validate, calls, before
        )

    def _check_spec_lifecycle(
        self, project, template, values, rows, validate, calls, before
    ):
        carrier_root = project.control_root
        self._assert_invalid_axiom(
            project, template, values, rows, validate, before
        )
        created = create_draft(
            project,
            {"newAtom": values},
            current_rows=rows(),
            validate_project_spec_model=validate,
        )
        self.assertEqual("completed", created["outcome"])
        self.assertEqual([(template, "C00", values["body"])], calls)
        draft = created["savedDraft"]
        self.assertEqual(
            carrier_root / "01_draft", (project.root / draft["path"]).parent
        )
        if template == "axiom":
            self.assertTrue(draft["ref_id"].startswith("AN-S-"))
        target = {"ref_id": draft["ref_id"], "version": 1}
        before = self.files(project)
        with self.assertRaises(InputError):
            promote_draft(
                project,
                {"target": target, "targetStatus": "active"},
                current_rows=rows(),
                validate_project_spec_model=validate,
            )
        self.assertEqual(before, self.files(project))
        self._assert_spec_status_moves(
            project, template, values, rows, validate, carrier_root
        )
        self._assert_spec_draft_archive(project, rows, target, carrier_root)

    def _assert_spec_draft_archive(self, project, rows, target, carrier_root):
        result = archive_spec_draft(
            project, {"target": target}, current_rows=rows()
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("archived", result["artifact"]["status"])
        self.assertEqual(
            carrier_root / "09_archived",
            (project.root / result["artifact"]["path"]).parent,
        )
        before = self.files(project)
        with self.assertRaises((InputError, SourceChanged)):
            archive_spec_draft(
                project, {"target": target}, current_rows=rows()
            )
        self.assertEqual(before, self.files(project))

    def _assert_invalid_axiom(
        self, project, template, values, rows, validate, before
    ):
        if template == "axiom":
            for invalid in (
                {"tier": -1},
                {"lens": "DES"},
                {"container": {"component": "C9"}},
            ):
                with (
                    self.subTest(invalid=invalid),
                    self.assertRaises(InputError),
                ):
                    create_draft(
                        project,
                        {"newAtom": {**values, **invalid}},
                        current_rows=rows(),
                        validate_project_spec_model=validate,
                    )
            self.assertEqual(before, self.files(project))

    def _assert_spec_status_moves(
        self, project, template, values, rows, validate, carrier_root
    ):
        second = create_draft(
            project,
            {"newAtom": {**values, "body": "\n## Summary\n\nSecond\n"}},
            current_rows=rows(),
            validate_project_spec_model=validate,
        )
        second_target = {
            "ref_id": second["savedDraft"]["ref_id"],
            "version": 1,
        }
        ready = promote_draft(
            project,
            {"target": second_target, "targetStatus": "ready"},
            current_rows=rows(),
            validate_project_spec_model=validate,
        )
        self.assertEqual("ready", ready["artifact"]["status"])
        self.assertEqual(
            carrier_root / "02_ready",
            (project.root / ready["artifact"]["path"]).parent,
        )
        current = {"ref_id": ready["artifact"]["ref_id"], "version": 1}
        for status, directory in (
            ("active", "_SPEC" if template == "applicable_principle" else ""),
            ("archived", "09_archived"),
        ):
            moved = change_spec_status(
                project,
                {"target": current, "targetStatus": status},
                current_rows=rows(),
                validate_project_spec_model=validate,
            )
            self.assertEqual(status, moved["artifact"]["status"])
            self.assertEqual(
                carrier_root / directory,
                (project.root / moved["artifact"]["path"]).parent,
            )
