"""Native project selection fixtures and conversion cases."""

from datetime import date
from pathlib import Path
import tempfile
from unittest.mock import NonCallableMock

import yaml

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests \
    .FEATURE_PROJECT_TOOLS__tests__shared import (  # noqa: E402
        validate_manifest,
    )
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    resolve_native_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.PROJECT_SUPPORT.PROJECT_SUPPORT__shared import (
    legacy_settings_to_manifest,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project_manifest__pub import (  # noqa: E402
    ProjectSelectionError,
)
# fmt: on


def carrier_header(atom_id, component, tier, status):
    return {
        "identity": {"atom_id": atom_id},
        "context": {
            "container": {"component": component},
            "tier": tier,
            "template": "project_manifest",
        },
        "state": {
            "status": status,
            "version": 3,
            "updated_at": "2026-11-19T00:00:00Z",
        },
    }


class NativeSelectionFixture:
    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()
        self.native = self.root / ".anechoic_anechoic"
        self.native.mkdir()

    def carrier(
        self,
        relative="AN-S-001-PROJECT_MANIFEST--declare-anechoic.md",
        *,
        atom_id="AN-S-001",
        name="Anechoic",
        prefix="AN",
        status="active",
        tier=-1,
        component="C0",
        lens_whitelist=None,
        parameters=None,
    ):
        path = self.native / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = carrier_header(atom_id, component, tier, status)
        claim_lenses = (
            f", lens_whitelist={lens_whitelist!r}"
            if lens_whitelist is not None
            else ""
        )
        claim_parameters = (
            f", parameters={parameters!r}" if parameters is not None else ""
        )
        path.write_text(
            f"---\n{yaml.safe_dump(header)}---\n\n"
            "## Summary\n\nDeclare Anechoic\n\n"
            "## Claim\n\n### Formal Claim\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest\n"
            "declare_entity(entity_name='Project Manifest', "
            f"instance=ProjectManifest(name={name!r}, "
            f"prefix={prefix!r}{claim_lenses}{claim_parameters}))\n```\n",
            encoding="utf-8",
        )
        return path

    def select(self):
        return resolve_native_project(
            self.root, self.native.name, validate_manifest=validate_manifest
        )


def result(**fields):
    mock = NonCallableMock(spec_set=["name", *fields], **fields)
    mock.name = "Anechoic"
    return mock


class NativeSelectionParameterCases:
    def test_binds_validated_parameters_and_accepts_identity_only_validator(
        self,
    ):
        self.carrier(
            parameters={
                "paths": {"control_root": ".anechoic_anechoic"},
                "values": [1, False],
            }
        )
        validated = {"effective": {"list": [1, False]}}

        def check(fields, component_id):
            self.assertEqual([1, False], fields["parameters"]["values"])
            validate_manifest(fields, component_id)
            return result(prefix="AN", parameters=validated)

        selected = resolve_native_project(
            self.root, self.native.name, validate_manifest=check
        )
        validated["effective"]["list"].append(2)
        self.assertEqual(
            {"effective": {"list": [1, False]}}, selected.parameters
        )
        legacy = resolve_native_project(
            self.root,
            self.native.name,
            validate_manifest=lambda fields, component: result(prefix="AN"),
        )
        self.assertEqual(
            {
                "paths": {"control_root": ".anechoic_anechoic"},
                "values": [1, False],
            },
            legacy.parameters,
        )
        with self.assertRaisesRegex(
            ProjectSelectionError, "parameters must be a mapping"
        ):
            resolve_native_project(
                self.root,
                self.native.name,
                validate_manifest=lambda fields, component: result(
                    prefix="AN", parameters=None
                ),
            )

    def test_root_prefix_and_legacy_control_root_bind_selection(self):
        for spelling, prefix in (
            (".anechoic_anechoic", "dot"),
            ("_anechoic_anechoic", "underscore"),
        ):
            with self.subTest(spelling=spelling):
                target = self.root / spelling
                if self.native != target:
                    self.native.rename(target)
                    self.native = target
                for parameters in (
                    {},
                    {"project": {"root": {"prefix": prefix}}},
                    {"paths": {"control_root": spelling}},
                ):
                    self.carrier(parameters=parameters)
                    self.assertEqual(target, self.select().control_root)
                for parameters in (
                    {
                        "project": {
                            "root": {
                                "prefix": "dot"
                                if prefix == "underscore"
                                else "underscore"
                            }
                        }
                    },
                    {"project": {"root": {"prefix": "invalid"}}},
                    {"paths": {"control_root": "wrong"}},
                ):
                    self.carrier(parameters=parameters)
                    with self.assertRaises(ProjectSelectionError):
                        self.select()

    def test_settings_conversion_preserves_all_other_values_through_selection(
        self,
    ):
        settings = {
            "schema_version": "2.0",
            "projection": {"version": 2},
            "artifact_timestamps": {"timezone": "local"},
            "artifacts": {
                "identity": {"project_prefix": "AN", "ceiling": 999},
                "types": ["a", "b"],
            },
            "authority": {"tiers": {"ordered": ["core", "standard"]}},
            "authority_modes": {"project": "strict"},
            "git": {"required": True},
            "governance_surfaces": {"scope_hub": False},
            "paths": {"control_root": ".anechoic_anechoic"},
            "project": {"name": "Anechoic", "key": "anechoic"},
            "project_mcp": {"http_port": 56317, "ratio": 0.5},
        }
        runtime = {
            "project_mcp": {
                "startup_timeout_seconds": 90,
                "build_if_missing": True,
            },
            "workbench": {"schema_mode": "native", "result_ttl_seconds": 300},
        }
        converted = legacy_settings_to_manifest(
            settings, runtime_settings=runtime
        )
        self.carrier(**converted)
        selected = self.select()
        self.assertEqual(runtime, selected.parameters["runtime"])
        restored = converted["parameters"]
        del restored["runtime"]
        restored["project"]["name"] = selected.project_name
        restored["artifacts"]["identity"]["project_prefix"] = (
            selected.project_prefix
        )
        self.assertEqual(settings, restored)
        self.assertNotIn("name", selected.parameters["project"])
        self.assertIs(
            type(selected.parameters["project_mcp"]["http_port"]), int
        )
        self.assertIs(type(selected.parameters["git"]["required"]), bool)
        self.assertIs(type(selected.parameters["artifacts"]["types"]), list)

    def test_settings_conversion_refuses_unrepresentable_or_invalid_input(
        self,
    ):
        base = {
            "project": {"name": "Anechoic"},
            "artifacts": {"identity": {"project_prefix": "AN"}},
        }
        for extra, message in (
            ({"date": date(2026, 1, 1)}, "settings.date"),
            ({"float": float("nan")}, "settings.float"),
            ({"bad": {1: "value"}}, "non-string key"),
            ({str(i): i for i in range(17)}, "parameter limit"),
        ):
            with (
                self.subTest(extra=extra),
                self.assertRaisesRegex(ValueError, message),
            ):
                legacy_settings_to_manifest({**base, **extra})
        with self.assertRaisesRegex(ValueError, "already contain a runtime"):
            legacy_settings_to_manifest(
                {**base, "runtime": {}}, runtime_settings={}
            )
        with self.assertRaisesRegex(ValueError, "runtime.workbench.expiry"):
            legacy_settings_to_manifest(
                base,
                runtime_settings={"workbench": {"expiry": date(2026, 1, 1)}},
            )
        for change in (
            {"project": {"name": " Anechoic"}},
            {"artifacts": {"identity": {"project_prefix": "an"}}},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                legacy_settings_to_manifest({**base, **change})

    def test_project_selection_rejects_unsafe_tier_one_folder(self):
        for path in (
            "../OUTSIDE",
            "01_DRAFT",
            "01_LEVEL/NESTED",
            "01_ARCHITECTURE_C9",
        ):
            with self.subTest(path=path):
                layout = {"0": ".", "1": path, "2+": "_{lens}/{sublenses}"}
                self.carrier(
                    parameters={
                        "project": {
                            "folder_layout": {"active_spec_by_tier": layout}
                        }
                    }
                )
                with self.assertRaisesRegex(
                    ProjectSelectionError, "folder_layout.active_spec_by_tier"
                ):
                    self.select()
