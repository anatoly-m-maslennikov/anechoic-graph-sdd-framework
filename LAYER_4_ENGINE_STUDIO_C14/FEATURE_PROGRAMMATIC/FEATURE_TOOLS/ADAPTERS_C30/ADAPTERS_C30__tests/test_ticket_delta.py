"""Exercise the guarded capture of changed Ticket paths."""

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext, capture_carrier_delta, capture_ticket_delta,
)

_ENDPOINTS = {
    "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
    "CONTAINS": [{}, True],
    "HAS_REFERENCE": [{"inverse_alias": "IS_REFERENCE_FOR"}, False],
    "IS_REFERENCE_FOR": [{}, True],
}
_PATH = "_anechoic_test/__TICKETS/TASKS/AN-T-2--ticket.md"
_CAPTURE = "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli.capture_native"
_TICKET = """---
atom_family: TKT
atom_id: AN-T-2
container: {component: C00}
priority: 2
context: {template: task}
relations: {REFERENCES: [AN-S-1]}
state: {status: active, version: 1, updated_at: '2026-11-22T00:00:00Z'}
---

## Summary

Changed ticket.
"""
_SPEC = """---
atom_family: SPEC
atom_id: AN-S-2
container: {component: C00}
tier: 0
context: {lens: SPEC}
state: {status: active, version: 1, updated_at: '2026-11-22T00:00:00Z'}
---

## Summary

Valid Spec in a Ticket folder.
"""


class TicketDeltaTests(TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.control = self.root / "_anechoic_test"
        self.control.mkdir()
        self.manifest = self.root / "AN-S-1-PROJECT_MANIFEST--test.md"
        self.manifest.write_text("Pinned bytes")
        self.binding = {"root": str(self.root), "control_root": self.control.name,
                        "manifest_path": self.manifest.name,
                        "manifest_sha256": sha256(self.manifest.read_bytes()).hexdigest(),
                        "project_prefix": "AN"}

    def write(self, path=_PATH, raw=_TICKET):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(raw)
        return target

    def capture(self, *paths):
        return capture_ticket_delta(self.binding, list(paths), _ENDPOINTS)

    def test_admitted_manifest_reads_only_addressed_carrier(self):
        path = self.root / _PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_TICKET)
        reads = []
        original = ReadContext.read

        def track(reader, target, **kwargs):
            reads.append(target)
            return original(reader, target, **kwargs)

        with patch.object(ReadContext, "read", track):
            result = capture_carrier_delta(self.binding, [_PATH], _ENDPOINTS,
                                           include_hashes=True, manifest_admitted=True)
        self.assertEqual([path], reads)
        self.assertEqual(sha256(path.read_bytes()).hexdigest(), result["carrier_hashes"][_PATH])

    def test_only_supplied_tickets_and_their_relations_are_present(self):
        self.write(raw="Unrelated malformed Markdown", path="_anechoic_test/ignored.md")
        for tree in ("__TICKETS", "001_TICKETS", "__TKT"):
            with self.subTest(tree=tree):
                path = _PATH.replace("__TICKETS", tree)
                ticket = self.write(path)
                delta = self.capture(path)
                self.assertEqual([[ticket.parent.relative_to(self.root).as_posix(), ticket.name]], delta["paths"])
                snapshot = delta["snapshot"]
                self.assertEqual(2, snapshot["schema_version"])
                self.assertEqual([("AN-T-2", "Changed ticket.")],
                                 [(row["reference"], row["summary"]) for row in snapshot["atoms"]])
                self.assertEqual(set(_ENDPOINTS), {edge["relation_type"] for edge in snapshot["relations"]})

    def test_rename_and_delete_retain_absent_paths(self):
        ticket = self.write()
        renamed = ticket.rename(ticket.with_name("AN-T-2--renamed.md"))
        parent = ticket.parent.relative_to(self.root).as_posix()
        new_path = renamed.relative_to(self.root).as_posix()
        delta = self.capture(_PATH, new_path)
        self.assertEqual([[parent, renamed.name], [parent, ticket.name]], delta["paths"])
        self.assertEqual([renamed.name], [row["filename"] for row in delta["snapshot"]["atoms"]])
        renamed.unlink()
        result = self.capture(new_path)
        self.assertEqual([[parent, renamed.name]], result["paths"])
        self.assertEqual([], result["snapshot"]["atoms"])
        self.assertEqual([], result["snapshot"]["relations"])

    def test_captures_500_requested_tickets_without_reading_unrelated_files(self):
        self.write(path="_anechoic_test/ignored.md", raw="Malformed unrelated content")
        paths = []
        for number in range(1, 501):
            reference = f"AN-T-{number}"
            path = f"_anechoic_test/__TICKETS/TASKS/{reference}--ticket.md"
            self.write(path=path, raw=_TICKET.replace("AN-T-2", reference))
            paths.append(path)
        result = self.capture(*paths)
        self.assertEqual(500, len(result["paths"]))
        self.assertEqual({f"AN-T-{number}" for number in range(1, 501)},
                         {row["reference"] for row in result["snapshot"]["atoms"]})
        self.assertEqual(2000, len(result["snapshot"]["relations"]))

    def test_refuses_unsupported_paths_and_non_ticket_headers(self):
        for path in ("../other.md", self.manifest.name, "_other/__TICKETS/task.md",
                     "_anechoic_test/elsewhere/task.md", _PATH.replace(".md", ".py")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.capture(path)
        with self.assertRaises(ValueError):
            self.capture(*([_PATH] * 1025))
        self.write(raw=_SPEC)
        with self.assertRaisesRegex(ValueError, "non-Ticket Atom"):
            self.capture(_PATH)

    def test_refuses_links_and_directories(self):
        ticket = self.write()
        alias = ticket.with_name("alias.md")
        alias.symlink_to(ticket)
        with self.assertRaises(OSError):
            self.capture(alias.relative_to(self.root).as_posix())
        alias.unlink()
        alias.mkdir()
        with self.assertRaisesRegex(ValueError, "regular file"):
            self.capture(alias.relative_to(self.root).as_posix())
        link = ticket.parent.parent / "linked-parent"
        link.symlink_to(ticket.parent, target_is_directory=True)
        with self.assertRaises(OSError):
            self.capture((link / ticket.name).relative_to(self.root).as_posix())

    def test_refuses_changed_manifest_and_source(self):
        ticket = self.write()
        self.manifest.write_text("Changed binding")
        with self.assertRaisesRegex(ValueError, "Manifest changed"):
            self.capture(_PATH)
        self.manifest.write_text("Pinned bytes")
        mocked = SimpleNamespace(errors={}, versions={})
        with (patch(_CAPTURE, return_value=mocked),
              self.assertRaisesRegex(ValueError, "paths changed during capture")):
            self.capture(_PATH)
        self.assertTrue(ticket.is_file())


class CarrierDeltaTests(TestCase):
    setUp = TicketDeltaTests.setUp
    write = TicketDeltaTests.write
    def capture(self, *paths):
        return capture_carrier_delta(self.binding, list(paths), _ENDPOINTS)

    def test_captures_canonical_families_and_root_goal_with_hashes(self):
        spec_path = "_anechoic_test/spec/AN-S-2--spec.md"
        config_path = "_anechoic_test/__PROJECT_CONFIG/AN-P-3--config.md"
        goal_path = "AN-S-4-SPEC-PROJECT_GOAL--goal.md"
        self.write(spec_path, _SPEC)
        config = _SPEC.replace("atom_family: SPEC", "atom_family: PROJECT_CONFIG").replace(
            "AN-S-2", "AN-P-3").replace("tier: 0\ncontext: {lens: SPEC}", "context: {template: settings}")
        self.write(config_path, config)
        goal = _SPEC.replace("AN-S-2", "AN-S-4").replace(
            "tier: 0\ncontext: {lens: SPEC}", "tier: -1\ncontext: {lens: SPEC, template: project_goal}")
        self.write(goal_path, goal)
        self.write(_PATH, _TICKET)
        result = capture_carrier_delta(self.binding, [goal_path, _PATH, spec_path, config_path],
                                       _ENDPOINTS, include_hashes=True)
        self.assertEqual({"AN-S-2", "AN-P-3", "AN-S-4", "AN-T-2"},
                         {row["reference"] for row in result["snapshot"]["atoms"]})
        self.assertEqual({goal_path, _PATH, spec_path, config_path}, set(result["carrier_hashes"]))
        self.assertEqual(sorted(result["paths"]), result["paths"])

    def test_refuses_non_carrier_paths_and_noncanonical_header(self):
        for path in (self.manifest.name, "_anechoic_test/000_ANECHOIC_framework/item.md",
                     "_anechoic_test/build.json", "outside.md", "_other/item.md",
                     "_anechoic_test/AN-S-8-SPEC-PROJECT_MANIFEST--other.md"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.capture(path)
        self.write(_PATH, _TICKET.replace("atom_family: TKT\natom_id: AN-T-2",
                                         "identity: {atom_id: AN-T-2}"))
        with self.assertRaises(ValueError):
            self.capture(_PATH)

    def test_deletion_links_and_changed_capture(self):
        path = "_anechoic_test/spec/AN-S-2--spec.md"
        source = self.write(path, _SPEC)
        alias = source.with_name("alias.md")
        alias.symlink_to(source)
        with self.assertRaises(OSError):
            self.capture(alias.relative_to(self.root).as_posix())
        mocked = SimpleNamespace(errors={}, versions={})
        with (patch(_CAPTURE, return_value=mocked),
              self.assertRaisesRegex(ValueError, "paths changed during capture")):
            self.capture(path)
        source.unlink()
        result = self.capture(path)
        self.assertEqual([], result["snapshot"]["atoms"])
        self.assertEqual([["_anechoic_test/spec", "AN-S-2--spec.md"]], result["paths"])
