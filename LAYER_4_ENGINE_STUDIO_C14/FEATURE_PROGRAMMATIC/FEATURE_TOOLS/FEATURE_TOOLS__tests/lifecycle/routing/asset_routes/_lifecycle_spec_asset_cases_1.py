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
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
    archive_ticket,
)
import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.drafts.test_native_lifecycle_draft as fixtures


class Model:
    enabled = True

    def project_spec_template(self, template):
        return ("Probe", 0, self.enabled) if template == "probe" else None

    def validate_project_spec(self, template, header, owner, body):
        context = header.get("context", {})
        if (
            template != "probe"
            or owner != "C00"
            or header.get("tier") != 0
            or context.get("lens") != "SPEC"
            or "## Guarantee" not in body
        ):
            raise ValueError("Invalid Project SPEC")


class ProjectSpecFixtureModel:
    def __init__(self, check):
        self.check = check

    def project_spec_template(self, template):
        tier = {
            "axiom": 0,
            "project_contract": 0,
            "applicable_principle": 2,
        }.get(template)
        return (template, tier, True) if tier is not None else None

    def validate(self, template, header, owner, body):
        if template == "axiom" and (
            header["tier"] != 0 or header["context"]["lens"] != "SPEC"
        ):
            raise ValueError("Invalid Axiom Tier or Lens")
        self.check(template, header, owner, body)


class LifecycleSpecAssetCases1:
    def test_project_template_creation_and_disabled_history(self):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        project.manifest_path.write_text(
            project.manifest_path.read_text().replace(
                "component: C0}", "component: C00}"
            )
        )
        project = replace(
            project,
            manifest_sha256=sha256(
                project.manifest_path.read_bytes()
            ).hexdigest(),
        )
        values = {
            "template": "probe",
            "container": {"component": "C00"},
            "lens": "SPEC",
            "body": "\n## Summary\n\nProbe\n\n## Guarantee\n\nThe Project records the decision.\n",
        }

        model = Model()
        validate = model.validate_project_spec
        created = create_draft(
            project,
            {"newAtom": values},
            current_rows=capture_native(project).atoms,
            validate_project_spec_model=validate,
        )
        self.assertEqual("completed", created["outcome"], created)
        for invalid in (
            {"tier": 2},
            {"lens": "DES"},
            {"template": "unknown"},
            {"body": "\n## Summary\n\nMissing Guarantee\n"},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(InputError):
                create_draft(
                    project,
                    {"newAtom": {**values, **invalid}},
                    current_rows=capture_native(project).atoms,
                    validate_project_spec_model=validate,
                )
        self._assert_disabled_history(
            model, project, values, validate, created
        )

    def _assert_disabled_history(
        self, model, project, values, validate, created
    ):
        model.enabled = False
        before = self.files(project)
        with self.assertRaises(InputError):
            create_draft(
                project,
                {"newAtom": values},
                current_rows=capture_native(project).atoms,
                validate_project_spec_model=validate,
            )
        self.assertEqual(before, self.files(project))
        self._assert_project_revision_history(project, validate, created)

    def _assert_project_revision_history(self, project, validate, created):
        target = {"ref_id": created["savedDraft"]["ref_id"], "version": 1}
        self.assertTrue(
            any(
                row["_exact_ref"] == target["ref_id"]
                for row in capture_native(project).atoms
            )
        )
        ready = promote_draft(
            project,
            {"target": target, "targetStatus": "ready"},
            current_rows=capture_native(project).atoms,
            validate_project_spec_model=validate,
        )
        self.assertEqual("ready", ready["artifact"]["status"], ready)
        current = {"ref_id": ready["artifact"]["ref_id"], "version": 1}
        revision = create_draft(
            project,
            {"sourceCurrent": current},
            current_rows=capture_native(project).atoms,
        )
        self.assertEqual("completed", revision["outcome"], revision)
        promoted = promote_draft(
            project,
            {
                "target": {
                    "ref_id": revision["savedDraft"]["ref_id"],
                    "version": 2,
                },
                "targetStatus": "ready",
            },
            current_rows=capture_native(project).atoms,
            validate_project_spec_model=validate,
        )
        self.assertEqual("ready", promoted["artifact"]["status"], promoted)
        self.assertTrue(
            any(
                row["id"] == current["ref_id"]
                and row["version"] == 1
                and row["status_group"] == "Archived"
                for row in capture_native(project).atoms
            )
        )

    def test_flat_ticket_archive_requires_replacement(self):
        templates = (
            "task",
            "epic",
            "problem",
            "question",
            "code_spec_mismatch",
            "opportunity",
            "analysis_report",
            "work_report",
            "work_log",
            "spec_proposal",
        )
        for template in templates:
            for situation in ("current", "draft"):
                with self.subTest(template=template, situation=situation):
                    self._flat_archive_case(template, situation)

    def _flat_archive_case(self, template, situation):
        project = self.project()
        path, target = self._write_flat_archive_source(
            project, template, situation
        )
        before = self.files(project)
        with self.assertRaises(InputError):
            archive_ticket(
                project,
                {"target": target},
                current_rows=capture_native(project).atoms,
            )
        self.assertEqual(before, self.files(project))
        self._write_flat_replacement(project)
        outcome = archive_ticket(
            project,
            {"target": target},
            current_rows=capture_native(project).atoms,
        )
        self.assertEqual("completed", outcome["outcome"], outcome)
        self.assertEqual("AN-T-2@1", outcome["artifact"]["ref_id"])
        self.assertFalse(path.exists())

    def _write_flat_archive_source(self, project, template, situation):
        status = "draft" if situation == "draft" else "in_queue"
        header = canonical_native_header(
            {
                "identity": {"atom_id": "AN-T-2"},
                "context": {
                    "container": {"component": "C00"},
                    "template": template,
                },
                "state": {
                    "status": status,
                    "version": 1,
                    "updated_at": "2026-01-01",
                },
            }
        )
        path = native_carrier_path(
            header,
            "Example",
            project_root=project.control_root,
            owner_directory=project.control_root,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\n"
            + yaml.safe_dump(header, sort_keys=False)
            + "---\n\n## Summary\n\nExample\n"
        )
        ref = "AN-T-2@1-draft" if situation == "draft" else "AN-T-2"
        target = {"ref_id": ref, "version": 1}
        return path, target

    def _write_flat_replacement(self, project):
        replacement = canonical_native_header(
            {
                "identity": {"atom_id": "AN-T-3"},
                "context": {
                    "container": {"component": "C00"},
                    "template": "task",
                },
                "state": {
                    "status": "in_queue",
                    "version": 1,
                    "updated_at": "2026-01-01",
                },
                "relations": {"IS_REPLACEMENT_FOR": ["AN-T-2"]},
            }
        )
        replacement_path = native_carrier_path(
            replacement,
            "Replacement",
            project_root=project.control_root,
            owner_directory=project.control_root,
        )
        replacement_path.parent.mkdir(parents=True, exist_ok=True)
        replacement_path.write_text(
            "---\n"
            + yaml.safe_dump(replacement, sort_keys=False)
            + "---\n\n## Summary\n\nReplacement\n"
        )
