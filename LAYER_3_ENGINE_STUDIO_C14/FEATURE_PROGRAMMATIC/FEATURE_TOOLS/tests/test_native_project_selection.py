"""Explicit native binding uses the authored Manifest and preserves legacy discovery."""

from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOLS), str(TOOLS.parent)]

from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import validate_model_fields  # noqa: E402
from legacy_settings_to_manifest import legacy_settings_to_manifest  # noqa: E402
from native_project_selection import resolve_native_project  # noqa: E402
from project_selection import ProjectSelectionError, resolve_project  # noqa: E402
from scope_declaration_test_support import write_scope_unit_declarations  # noqa: E402


@dataclass
class ProjectManifest:
    atom_id: str
    ref_id: str
    version: int
    tier: int = field(metadata={"allowed_values": (-1,)})
    name: str
    prefix: str
    parameters: dict[str, object] = field(default_factory=dict)
    lens_whitelist: list[str] | None = None


def validate_manifest(fields, component_id):
    if component_id != "C0":
        raise ValueError("Manifest must be contained by the Project")
    validate_model_fields(ProjectManifest, fields)
    return ProjectManifest(**fields)


class NativeProjectSelectionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.native = self.root / ".anechoic_anechoic"
        self.native.mkdir()

    def carrier(self, relative="AN-S-001-PROJECT_MANIFEST--declare-anechoic.md", *, atom_id="AN-S-001",
                name="Anechoic", prefix="AN", status="active", tier=-1, component="C0", lens_whitelist=None,
                parameters=None):
        path = self.native / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {"identity": {"atom_id": atom_id},
                  "context": {"container": {"component": component}, "tier": tier, "template": "project_manifest"},
                  "state": {"status": status, "version": 3, "updated_at": "2026-11-19T00:00:00Z"}}
        claim_lenses = f", lens_whitelist={lens_whitelist!r}" if lens_whitelist is not None else ""
        claim_parameters = f", parameters={parameters!r}" if parameters is not None else ""
        path.write_text(f"---\n{yaml.safe_dump(header)}---\n\n## Summary\n\nDeclare Anechoic\n\n"
                        "## Claim\n\n### Formal Claim\n\n```python\n"
                        "from anechoic.formal_claims import declare_entity\n"
                        "from anechoic.model import ProjectManifest\n"
                        f"declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name={name!r}, "
                        f"prefix={prefix!r}{claim_lenses}{claim_parameters}))\n```\n", encoding="utf-8")
        return path

    def select(self):
        return resolve_native_project(self.root, self.native.name, validate_manifest=validate_manifest)

    def test_explicit_binding_pins_one_native_manifest_during_legacy_coexistence(self):
        legacy = self.root / ".anechoic_legacy"
        legacy.mkdir()
        (legacy / "anechoic_project_settings.toml").write_text(
            '[project]\nname="legacy"\nkey="legacy"\nrepository_slug="legacy"\n'
            '[paths]\ncontrol_root=".anechoic_legacy"\n[artifacts.identity]\nproject_prefix="CA"\n',
            encoding="utf-8",
        )
        write_scope_unit_declarations(self.root, control_root=legacy)
        active = self.carrier()
        for area in ("_PMETA", "__TKT", "draft", "archived"):
            self.carrier(f"{area}/{active.name}")
        native = self.select()
        self.assertEqual(("Anechoic", "AN", self.native), (native.project_name, native.project_prefix, native.control_root))
        self.assertEqual((active, "AN-S-001@3", sha256(active.read_bytes()).hexdigest()),
                         (native.manifest_path, native.manifest_ref, native.manifest_sha256))
        legacy_default = resolve_project(self.root)
        self.assertEqual(legacy, legacy_default.control_root)
        self.assertNotEqual(legacy_default.instance_id, native.instance_id)
        self.assertFalse((self.root / ".anechoic_runtime").exists())

    def test_refuses_missing_and_ambiguous_active_manifest(self):
        self.carrier(status="draft")
        with self.assertRaisesRegex(ProjectSelectionError, "Expected one Active"):
            self.select()
        self.carrier()
        self.carrier("AN-S-002-PROJECT_MANIFEST--declare-anechoic.md", atom_id="AN-S-002")
        with self.assertRaisesRegex(ProjectSelectionError, "Expected one Active"):
            self.select()

    def test_passes_the_authored_lens_whitelist_to_typed_validation(self):
        for lenses in ([], ["SPEC"]):
            with self.subTest(lenses=lenses):
                self.carrier(lens_whitelist=lenses)

                def check(fields, component_id):
                    manifest = validate_manifest(fields, component_id)
                    self.assertEqual(lenses, manifest.lens_whitelist)
                    return manifest

                resolve_native_project(self.root, self.native.name, validate_manifest=check)

    def test_binds_validated_parameters_and_accepts_identity_only_validator(self):
        self.carrier(parameters={"paths": {"control_root": ".anechoic_anechoic"}, "values": [1, False]})
        validated = {"effective": {"list": [1, False]}}

        def check(fields, component_id):
            self.assertEqual([1, False], fields["parameters"]["values"])
            validate_manifest(fields, component_id)
            return SimpleNamespace(name="Anechoic", prefix="AN", parameters=validated)

        selected = resolve_native_project(self.root, self.native.name, validate_manifest=check)
        validated["effective"]["list"].append(2)
        self.assertEqual({"effective": {"list": [1, False]}}, selected.parameters)
        legacy = resolve_native_project(self.root, self.native.name,
                                        validate_manifest=lambda fields, component: SimpleNamespace(name="Anechoic", prefix="AN"))
        self.assertEqual({"paths": {"control_root": ".anechoic_anechoic"}, "values": [1, False]},
                         legacy.parameters)
        with self.assertRaisesRegex(ProjectSelectionError, "parameters must be a mapping"):
            resolve_native_project(self.root, self.native.name,
                                   validate_manifest=lambda fields, component: SimpleNamespace(name="Anechoic", prefix="AN", parameters=None))

    def test_settings_conversion_preserves_all_other_values_through_selection(self):
        settings = {"schema_version": "2.0", "projection": {"version": 2},
                    "artifact_timestamps": {"timezone": "local"},
                    "artifacts": {"identity": {"project_prefix": "AN", "ceiling": 999},
                                  "types": ["a", "b"]},
                    "authority": {"tiers": {"ordered": ["core", "standard"]}},
                    "authority_modes": {"project": "strict"}, "git": {"required": True},
                    "governance_surfaces": {"scope_hub": False},
                    "paths": {"control_root": ".anechoic_anechoic"},
                    "project": {"name": "Anechoic", "key": "anechoic"},
                    "project_mcp": {"http_port": 56317, "ratio": 0.5}}
        runtime = {"project_mcp": {"startup_timeout_seconds": 90, "build_if_missing": True},
                   "workbench": {"schema_mode": "native", "result_ttl_seconds": 300}}
        converted = legacy_settings_to_manifest(settings, runtime_settings=runtime)
        self.carrier(**converted)
        selected = self.select()
        self.assertEqual(runtime, selected.parameters["runtime"])
        restored = converted["parameters"]
        del restored["runtime"]
        restored["project"]["name"] = selected.project_name
        restored["artifacts"]["identity"]["project_prefix"] = selected.project_prefix
        self.assertEqual(settings, restored)
        self.assertNotIn("name", selected.parameters["project"])
        self.assertIs(type(selected.parameters["project_mcp"]["http_port"]), int)
        self.assertIs(type(selected.parameters["git"]["required"]), bool)
        self.assertIs(type(selected.parameters["artifacts"]["types"]), list)

    def test_settings_conversion_refuses_unrepresentable_or_invalid_input(self):
        base = {"project": {"name": "Anechoic"}, "artifacts": {"identity": {"project_prefix": "AN"}}}
        for extra, message in (({"date": date(2026, 1, 1)}, "settings.date"),
                               ({"float": float("nan")}, "settings.float"),
                               ({"bad": {1: "value"}}, "non-string key"),
                               ({str(i): i for i in range(17)}, "parameter limit")):
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, message):
                legacy_settings_to_manifest({**base, **extra})
        with self.assertRaisesRegex(ValueError, "already contain a runtime"):
            legacy_settings_to_manifest({**base, "runtime": {}}, runtime_settings={})
        with self.assertRaisesRegex(ValueError, "runtime.workbench.expiry"):
            legacy_settings_to_manifest(base, runtime_settings={"workbench": {"expiry": date(2026, 1, 1)}})
        for change in ({"project": {"name": " Anechoic"}},
                       {"artifacts": {"identity": {"project_prefix": "an"}}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                legacy_settings_to_manifest({**base, **change})

    def test_refuses_contradictory_identity_and_invalid_owner(self):
        for values, error in (({"name": "other"}, "name contradicts"), ({"prefix": "XX"}, "prefix contradicts"),
                              ({"tier": 0}, "Invalid Active"), ({"component": "C43"}, "invalid, or unsafe")):
            with self.subTest(values=values), self.assertRaisesRegex(ProjectSelectionError, error):
                self.carrier(**values)
                self.select()

    def test_refuses_symlink_manifest(self):
        outside = self.carrier()
        renamed = outside.rename(self.root / outside.name)
        outside.symlink_to(renamed)
        with self.assertRaisesRegex(ProjectSelectionError, "invalid, or unsafe"):
            self.select()


if __name__ == "__main__":
    unittest.main()
