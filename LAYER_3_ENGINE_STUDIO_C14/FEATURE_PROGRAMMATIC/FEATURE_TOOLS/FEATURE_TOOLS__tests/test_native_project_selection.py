"""Explicit native binding uses the authored Manifest and preserves legacy discovery."""

import ast
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

TOOLS = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOLS), str(TOOLS.parent)]

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.native_manifest_test_support__pub import validate_manifest  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.legacy_settings_to_manifest import legacy_settings_to_manifest  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_project_selection import discover_native_project, resolve_native_project  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.project_selection import ProjectSelectionError, resolve_project  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.scope_declaration_test_support__pub import write_scope_unit_declarations  # noqa: E402


class ManifestReaderBoundaryTests(unittest.TestCase):
    def test_reader_imports_only_standard_library_and_c30(self):
        path = TOOLS / "ADAPTERS_C30" / "project_manifest__pub.py"
        imports = [node for node in ast.walk(ast.parse(path.read_text()))
                   if isinstance(node, (ast.Import, ast.ImportFrom))]
        for node in imports:
            if isinstance(node, ast.ImportFrom):
                self.assertTrue(node.level == 1 or node.module in {"datetime", "pathlib"})
            else:
                self.assertEqual([alias.name for alias in node.names], ["re"])


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
        for area in ("_PMETA", "__TKT", "draft", "archived", "archive", "SPEC/subsection"):
            self.carrier(f"{area}/{active.name}")
        native = self.select()
        self.assertEqual(("Anechoic", "AN", self.native), (native.project_name, native.project_prefix, native.control_root))
        self.assertEqual((active, "AN-S-001@3", sha256(active.read_bytes()).hexdigest()),
                         (native.manifest_path, native.manifest_ref, native.manifest_sha256))
        legacy_default = resolve_project(self.root)
        self.assertEqual(legacy, legacy_default.control_root)
        self.assertNotEqual(legacy_default.instance_id, native.instance_id)
        self.assertFalse((self.root / ".anechoic_runtime").exists())

    def test_root_manifest_takes_precedence_and_discovery_infers_control(self):
        legacy = self.carrier()
        root_manifest = legacy.rename(self.root / legacy.name)
        self.carrier(name="Other")
        (self.root / "README.md").write_text("unrelated content")
        selected = self.select()
        self.assertEqual(root_manifest, selected.manifest_path)
        self.assertEqual(root_manifest, discover_native_project(
            self.root, manifest_validator=lambda: validate_manifest).manifest_path)

    def test_root_candidate_refuses_bad_or_duplicate_and_does_not_fall_back(self):
        legacy = self.carrier()
        root_manifest = self.root / legacy.name
        root_manifest.write_text("---\ninvalid: [\n---\n")
        with self.assertRaises(ProjectSelectionError):
            self.select()
        root_manifest.write_text(legacy.read_text().replace("status: active", "status: draft"))
        with self.assertRaises(ProjectSelectionError):
            self.select()
        root_manifest.write_text(legacy.read_text())
        second = self.carrier("AN-S-002-PROJECT_MANIFEST--declare-anechoic.md", atom_id="AN-S-002")
        second.rename(self.root / second.name)
        with self.assertRaises(ProjectSelectionError):
            self.select()

    def test_root_manifest_requires_safe_existing_control(self):
        legacy = self.carrier()
        legacy.rename(self.root / legacy.name)
        self.native.rmdir()
        with self.assertRaises(ProjectSelectionError):
            self.select()

    def test_canonical_manifest_header(self):
        path = self.carrier()
        text = path.read_text()
        _, header, body = text.split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['atom_family'] = 'SPEC'
        metadata['atom_id'] = metadata.pop('identity')['atom_id']
        metadata['structure'] = {'container': metadata['context'].pop('container'),
                                 'tier': metadata['context'].pop('tier')}
        path.write_text(f"---\n{yaml.safe_dump(metadata)}---{body}")
        self.assertEqual('AN-S-001@3', self.select().manifest_ref)

    def test_refuses_missing_and_ambiguous_active_manifest(self):
        self.carrier(status="draft")
        with self.assertRaisesRegex(ProjectSelectionError, "Expected one Active"):
            self.select()
        self.carrier()
        self.carrier("AN-S-002-PROJECT_MANIFEST--declare-anechoic.md", atom_id="AN-S-002")
        with self.assertRaisesRegex(ProjectSelectionError, "Expected one Active"):
            self.select()

    def test_passes_authored_state_to_strict_model(self):
        path = self.carrier()
        header = path.read_text()

        def check(fields, component_id):
            fields = dict(fields)
            self.assertEqual("active", fields.pop("status"))
            self.assertEqual(datetime.fromisoformat("2026-11-19T00:00:00Z"), fields.pop("updated_at"))
            return validate_manifest(fields, component_id)

        def select():
            return resolve_native_project(self.root, self.native.name, validate_manifest=check,
                                          require_atom_state=True)

        select()
        timestamp_line = next(line for line in header.splitlines(keepends=True) if line.startswith("  updated_at:"))
        for bad in ("", "  updated_at: invalid\n"):
            path.write_text(header.replace(timestamp_line, bad))
            with self.assertRaises(ProjectSelectionError):
                select()

    def test_old_spec_directory_is_ignored_and_never_walked(self):
        self.carrier("SPEC/AN-S-001-PROJECT_MANIFEST--declare-anechoic.md")
        with self.assertRaisesRegex(ProjectSelectionError, "Expected one Active"):
            self.select()
        self.carrier()
        (self.native / "SPEC" / "unreadable-link").symlink_to(self.root / "missing")
        self.assertEqual(self.native / "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md", self.select().manifest_path)

    def test_refuses_manifest_added_during_native_validation(self):
        self.carrier()

        def add_manifest(fields, component):
            self.carrier("AN-S-002-PROJECT_MANIFEST--declare-anechoic.md", atom_id="AN-S-002")
            return validate_manifest(fields, component)

        with self.assertRaisesRegex(ProjectSelectionError, "changed during selection"):
            resolve_native_project(self.root, self.native.name, validate_manifest=add_manifest)

    def test_direct_root_inventory_is_bounded(self):
        self.carrier()
        (self.native / "one").touch()
        (self.native / "two").touch()
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import CEILINGS
        with patch.dict(CEILINGS, {"max_candidates": 2}), self.assertRaises(ProjectSelectionError):
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

    def test_root_prefix_and_legacy_control_root_bind_selection(self):
        for spelling, prefix in ((".anechoic_anechoic", "dot"), ("_anechoic_anechoic", "underscore")):
            with self.subTest(spelling=spelling):
                target = self.root / spelling
                if self.native != target:
                    self.native.rename(target)
                    self.native = target
                for parameters in ({}, {"project": {"root": {"prefix": prefix}}},
                                   {"paths": {"control_root": spelling}}):
                    self.carrier(parameters=parameters)
                    self.assertEqual(target, self.select().control_root)
                for parameters in ({"project": {"root": {"prefix": "dot" if prefix == "underscore" else "underscore"}}},
                                   {"project": {"root": {"prefix": "invalid"}}},
                                   {"paths": {"control_root": "wrong"}}):
                    self.carrier(parameters=parameters)
                    with self.assertRaises(ProjectSelectionError):
                        self.select()

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
        renamed = outside.rename(self.root / "outside.md")
        outside.symlink_to(renamed)
        with self.assertRaisesRegex(ProjectSelectionError, "invalid, or unsafe"):
            self.select()


if __name__ == "__main__":
    unittest.main()
