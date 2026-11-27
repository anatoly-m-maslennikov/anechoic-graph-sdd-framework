from hashlib import sha256
from pathlib import Path, PurePosixPath
import sys
import os
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import yaml

TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext, capture_indexed_lifecycle, capture_native,
    native_carrier_hashes, revalidate_native, status_domains,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__tests.ADAPTERS_C30__tests__shared import (
    NativeCaptureFixture,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_capture import model_inputs


class NativeCaptureTests(NativeCaptureFixture, unittest.TestCase):
    def test_structure_issue_uses_classification_and_candidate_location(self):
        alias = self.control / 'AN-S-2-SPEC-OTHER--alias.md'
        header = {'atom_family': 'SPEC', 'atom_id': 'AN-S-2', 'container': {'component': 'C00'},
                  'tier': 1, 'context': {'template': 'component_manifest', 'lens': 'SPEC'},
                  'state': {'status': 'active', 'version': 0, 'updated_at': '2026-11-19T00:00:00Z'}}
        alias.write_text('---\n' + yaml.safe_dump(header) + '---\n\n## Summary\n\nExample\n')
        off_path = self.control / '_QA/AN-S-3-SPEC-COMPONENT_MANIFEST--invalid.md'
        off_path.parent.mkdir()
        off_path.write_text('---\ninvalid: [\n---\n')
        capture = capture_native(self.selection)
        selected = SimpleNamespace(root=self.root, control_root=self.control,
                                   manifest_path=self.root / 'other', project_prefix='AN')
        capture_view = SimpleNamespace(atoms=[], ingestion_issues=capture.ingestion_issues,
                                       errors=capture.errors, classified_templates=capture.classified_templates)
        result = model_inputs(selected, capture_view, include_spec_rows=True)
        assert not result['structure_issues']
        assert result['structure_alias_issues'] == ({'relative_path': alias.relative_to(self.root).as_posix(),
                                                     'template': 'component_manifest'},)
        header['state']['version'] = 1
        alias.write_text('---\n' + yaml.safe_dump(header) + '---\n\n## Summary\n\nExample\n')
        updated = capture_native(self.selection, previous=capture,
                                 paths={PurePosixPath(alias.relative_to(self.root).as_posix())})
        assert alias.relative_to(self.root).as_posix() not in updated.classified_templates
        assert alias.relative_to(self.root).as_posix() not in updated.errors

    def test_capture_uses_admitted_family_status_domains(self):
        root = "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
        bindings = {"declarations": [
            [name, {"arguments": {"entity_name": "Status", "entity_kind": "Property",
             "relation_name": "IS_PROPERTY_OF", "base_path": root + ".Header.State",
             "applies_to_entity_classes": [root + "//" + name], "allowed_values": values}}]
            for name, values in (("Specification", ["draft", "active", "archived"]),
                                 ("Ticket", ["draft", "active", "archived"]),
                                 ("project_config", ["draft", "active", "reviewed", "archived"]))
        ]}
        for name, class_name in (("Specification", "SpecAtom"), ("Ticket", "TicketAtom"),
                                 ("project_config", "ProjectConfigAtom")):
            bindings["declarations"].append([
                "MODEL//ANECHOIC <+ " + root + "//" + name,
                {"arguments": {"entity_name": name, "entity_class": class_name}},
            ])
        unrelated = "Graph/Other/Atom"
        bindings["declarations"].append(["other", {"arguments": {
            "entity_name": "Status", "entity_kind": "Property", "relation_name": "IS_PROPERTY_OF",
            "base_path": unrelated + ".Header.State", "applies_to_entity_classes": [unrelated + "//Ticket"],
            "allowed_values": ["unrelated"],
        }}])
        for _, claim in bindings["declarations"]:
            args = claim["arguments"]
            if "allowed_values" in args:
                args["allowed_values"] = tuple(args["allowed_values"])
                args["applies_to_entity_classes"] = tuple(args["applies_to_entity_classes"])
        valid = self.write("__PROJECT_CONFIG/AN-C-1--valid.md", "AN-C-1", "reviewed", 1)
        unknown = self.write("__PROJECT_CONFIG/AN-C-2--unknown.md", "AN-C-2", "unknown", 1)
        result = capture_native(self.selection, domains=status_domains(bindings))
        row = next(row for row in result.atoms if row["id"] == "AN-C-1")
        self.assertEqual(("Current", "AN-C-1", "AN-C-1@1"),
                         (row["status_group"], row["ref"], row["_exact_ref"]))
        self.assertNotIn(valid.relative_to(self.root).as_posix(), result.errors)
        self.assertIn(unknown.relative_to(self.root).as_posix(), result.errors)
        unknown.unlink()
        result = capture_native(self.selection, domains=status_domains(bindings))
        domains = status_domains(bindings)
        self.assertEqual(domains, revalidate_native(self.selection, result).status_domains)
        descriptor = {"id": "AN-C-1", "ref": "AN-C-1", "_exact_ref": "AN-C-1@1",
                      "source_path": valid.relative_to(self.root).as_posix(), "version": 1,
                      "status": "reviewed", "status_group": "Current", "owner_kind": "Component",
                      "owner_ref": "C0", "read": True}
        indexed = capture_indexed_lifecycle(self.selection, [descriptor], {}, domains=domains)
        self.assertEqual(domains, revalidate_native(self.selection, indexed).status_domains)
        with self.assertRaisesRegex(ValueError, "identity"):
            capture_indexed_lifecycle(self.selection, [descriptor | {"status": "unknown"}], {}, domains=domains)

    def test_ingestion_issues_report_malformed_and_duplicate_carriers(self):
        malformed = self.control / "malformed.md"
        malformed.write_text("---\ninvalid: [\n---\n")
        first = self.write("AN-T-8--first.md", "AN-T-8", "active", 1)
        second = self.write("other/AN-T-8--second.md", "AN-T-8", "active", 1)
        third = self.write("AN-T-8--third.md", "AN-T-8", "active", 2)
        result = capture_native(self.selection)
        self.assertEqual("parse_error", next(i["code"] for i in result.ingestion_issues
                                             if i["relative_path"] == malformed.relative_to(self.root).as_posix()))
        for code, paths in (("duplicate_revision", [first, second]),
                            ("duplicate_current", [first, second, third])):
            relatives = sorted(p.relative_to(self.root).as_posix() for p in paths)
            issues = [i for i in result.ingestion_issues if i["code"] == code]
            self.assertEqual(relatives, sorted(i["relative_path"] for i in issues))
            self.assertTrue(all(i["related_paths"] == relatives for i in issues))
        self.assertEqual({"AN-S-001"}, {row["ref"] for row in result.atoms})
        second.unlink()
        third.unlink()
        updated = capture_native(self.selection, previous=result,
                                 paths={PurePosixPath(second.relative_to(self.root).as_posix()),
                                        PurePosixPath(third.relative_to(self.root).as_posix())})
        self.assertFalse(any(i["code"].startswith("duplicate_") for i in updated.ingestion_issues))
        self.assertEqual({"AN-S-001", "AN-T-8"}, {row["ref"] for row in updated.atoms})

    def test_indexed_capture_reads_only_addressed_and_detects_drift(self):
        path = self.write("AN-T-8--task.md", "AN-T-8", "active", 1)
        other = self.write("AN-T-9--other.md", "AN-T-9", "active", 1)
        descriptor = {"id": "AN-T-8", "ref": "AN-T-8", "_exact_ref": "AN-T-8@1",
                      "source_path": path.relative_to(self.root).as_posix(), "version": 1,
                      "status": "active", "status_group": "Current", "owner_kind": "Component",
                      "owner_ref": "C0", "read": True}
        original = ReadContext.read
        def read(reader, source, **kwargs):
            self.assertNotEqual(source, other)
            return original(reader, source, **kwargs)
        with patch.object(ReadContext, "read", read):
            path.write_text(path.read_text().replace("Example", "Changed"))
            capture = capture_indexed_lifecycle(self.selection, [descriptor], {"S": "0", "T": "9"}, lenses=["SPEC"])
            self.assertEqual({"S": 0, "T": 9}, capture.max_numbers)
            self.assertEqual(sha256(path.read_bytes()).hexdigest(), capture.atoms[0]["_source_sha256"])
            with self.assertRaisesRegex(ValueError, "changed"):
                stale = descriptor | {"version": 2, "_exact_ref": "AN-T-8@2"}
                capture_indexed_lifecycle(self.selection, [stale], {})
            with patch.object(ReadContext, "read", side_effect=AssertionError("unexpected content read")):
                self.assertEqual(capture.atoms, revalidate_native(self.selection, capture).atoms)
            original_stat = path.stat()
            path.write_text(path.read_text().replace("Changed", "Another"))
            os.utime(path, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
            with self.assertRaisesRegex(ValueError, "changed"):
                revalidate_native(self.selection, capture)
            path.unlink()
            with self.assertRaisesRegex(ValueError, "missing"):
                revalidate_native(self.selection, capture)
            path.symlink_to(other)
            with self.assertRaisesRegex(ValueError, "missing or changed"):
                revalidate_native(self.selection, capture)

    def test_hash_inventory_tracks_content_and_deletion(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        path = self.write("AN-T-8--hash.md", "AN-T-8", "active", 1)
        ignored = self.control / "000_ANECHOIC_framework" / "ignored.md"
        ignored.parent.mkdir()
        ignored.write_text("not a carrier")
        relative = path.relative_to(self.root).as_posix()
        before = native_carrier_hashes(binding)
        self.assertEqual(sha256(path.read_bytes()).hexdigest(), before[relative])
        self.assertEqual({self.manifest.relative_to(self.root).as_posix(), relative}, set(before))
        stat = path.stat()
        path.write_bytes(path.read_bytes().replace(b"Example", b"Changed"))
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        after = native_carrier_hashes(binding)
        self.assertNotEqual(before[relative], after[relative])
        path.unlink()
        self.assertNotIn(relative, native_carrier_hashes(binding))

    def test_raw_hashes_include_root_goal_and_reject_inventory_race(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        goal = self.root / "AN-S-02-SPEC-PROJECT_GOAL--goal.md"
        goal.write_bytes(b"not parsed by hashing")
        self.assertEqual(sha256(goal.read_bytes()).hexdigest(), native_carrier_hashes(binding)[goal.name])
        original = ReadContext.read
        def read_and_change(reader, path, **kwargs):
            raw = original(reader, path, **kwargs)
            if path == goal and kwargs.get("remember", True):
                (self.control / "new.md").write_text("new")
            return raw
        with patch.object(ReadContext, "read", read_and_change):
            with self.assertRaisesRegex(ValueError, "changed during capture"):
                native_carrier_hashes(binding)

    def test_current_draft_archived_and_header_containment(self):
        self.write("__TKT/TASKS/AN-T-09--task.md", "AN-T-09", "active", 2)
        self.write("__TKT/TASKS/draft/AN-T-09@3-draft--task.md", "AN-T-09", "draft", 3)
        self.write("__TKT/ASSETS/AN-T-10--asset.md", "AN-T-10", "active", 1, {"atom": "AN-T-09"})
        self.write("__TKT/TASKS/AN-T-11@1-draft--linked.md", "AN-T-11", "draft", 1, {"atom": "AN-T-09"})
        self.write("archived/AN-S-001@2--old.md", "AN-S-001", "archived", 2)
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        rows = {row["_exact_ref"]: row for row in result.atoms}
        self.assertEqual("AN-T-09", rows["AN-T-09@2"]["ref"])
        self.assertEqual("Current", rows["AN-T-09@2"]["status_group"])
        self.assertEqual("AN-T-09@3-draft", rows["AN-T-09@3-draft"]["ref"])
        self.assertEqual("Draft", rows["AN-T-11@1-draft"]["status_group"])
        self.assertEqual("AN-S-001@2", rows["AN-S-001@2"]["ref"])
        asset = next(edge for edge in result.containment if edge["source_ref"] == "AN-T-10")
        self.assertEqual(("Atom", "AN-T-09"), (asset["target_kind"], asset["target_ref"]))
        self.assertIn(b"Example", rows["AN-T-10@1"]["_content_bytes"])

    def test_root_manifest_and_goal_capture_and_incremental_revalidation(self):
        self.manifest = self.manifest.rename(self.root / self.manifest.name)
        self.selection.manifest_path = self.manifest
        goal = self.root / "AN-S-02-SPEC-PROJECT_GOAL--goal.md"
        header = {"atom_family": "SPEC", "atom_id": "AN-S-02", "container": {"component": "C00"},
                  "tier": -1, "context": {"template": "project_goal", "lens": "SPEC"},
                  "state": {"status": "active", "version": 1, "updated_at": "2026-11-19T00:00:00Z"}}
        text = "---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\n"
        goal.write_text(text + "Goal\n")
        (self.root / "AN-S-03-SPEC--unrelated.md").write_text("Unrelated Markdown")
        first = capture_native(self.selection)
        self.assertEqual({}, first.errors)
        self.assertEqual({self.manifest.name, goal.name}, {row["source_path"] for row in first.atoms})

        goal.write_text(text + "Updated goal\n")
        updated = revalidate_native(self.selection, first)
        row = next(row for row in updated.atoms if row["source_path"] == goal.name)
        self.assertIn(b"Updated goal", row["_content_bytes"])
        goal.unlink()
        remaining = revalidate_native(self.selection, updated)
        self.assertEqual([self.manifest.name], [row["source_path"] for row in remaining.atoms])

    def test_canonical_header_controls_identity_and_preserves_authored_metadata(self):
        path = self.control / "__TKT" / "arbitrary-name.md"
        path.parent.mkdir(parents=True)
        header = {"atom_family": "SPEC", "atom_id": "AN-S-20",
                  "structure": {"container": {"component": "C0"}, "tier": 3},
                  "context": {"lens": "example"},
                  "state": {"status": "active", "version": 1,
                            "updated_at": "2026-11-19T00:00:00Z"}}
        path.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n")
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        row = next(row for row in result.atoms if row["id"] == "AN-S-20")
        self.assertEqual(header, row["header_json"])
        self.assertEqual(3, row["tier"])
        self.assertEqual("AN-S-20", row["ref"])
        self.assertEqual("C0", next(edge for edge in result.containment
                                     if edge["source_ref"] == "AN-S-20")["target_ref"])

        duplicate = self.control / "elsewhere.md"
        duplicate.write_bytes(path.read_bytes())
        self.assertTrue(any("Duplicate" in error for error in capture_native(self.selection).errors.values()))

    def test_complete_ticket_asset_is_current(self):
        path = self.control / "001_TICKETS/ASSETS/08_complete/AN-T-14--asset.md"
        path.parent.mkdir(parents=True)
        header = {"atom_family": "TKT", "atom_id": "AN-T-14", "container": {"component": "C0"},
                  "priority": 2, "context": {"template": "analysis_report"},
                  "state": {"status": "complete", "version": 2, "updated_at": "2026-11-19T00:00:00Z"}}
        path.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n")
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        row = next(row for row in result.atoms if row["id"] == "AN-T-14")
        self.assertEqual(("Current", "AN-T-14", "AN-T-14@2"),
                         (row["status_group"], row["ref"], row["_exact_ref"]))

    def test_ticket_in_queue_is_current_and_in_progress_is_invalid(self):
        self.write("AN-T-12--queued.md", "AN-T-12", "in_queue", 2)
        self.write("AN-T-13--working.md", "AN-T-13", "in_progress", 1)
        result = capture_native(self.selection)
        row = next(row for row in result.atoms if row["id"] == "AN-T-12")
        self.assertEqual(("Current", "AN-T-12", "AN-T-12@2"),
                         (row["status_group"], row["ref"], row["_exact_ref"]))
        self.assertEqual(1, len(result.errors))
        self.assertIn("status", next(iter(result.errors.values())))

    def test_ready_is_current_only_for_spec(self):
        self.write("02_ready/AN-S-2--ready.md", "AN-S-2", "ready", 2)
        self.write("AN-T-3--invalid.md", "AN-T-3", "ready", 1)
        self.write("_PMETA/AN-P-4--invalid.md", "AN-P-4", "ready", 1)
        result = capture_native(self.selection)
        row = next(row for row in result.atoms if row["id"] == "AN-S-2")
        self.assertEqual(("Current", "AN-S-2", "AN-S-2@2"),
                         (row["status_group"], row["ref"], row["_exact_ref"]))
        self.assertEqual(2, len(result.errors))
        self.assertTrue(all("status" in error for error in result.errors.values()))
        self.write("AN-S-2--active.md", "AN-S-2", "active", 3)
        self.assertTrue(any("Duplicate" in error for error in capture_native(self.selection).errors.values()))

    def test_new_folder_names_accept_legacy_headers(self):
        for folder, atom_id in (("001_TICKETS/TASKS/01_draft", "AN-T-10"),
                                ("002_PROJECT_CONFIG/09_archived", "AN-P-10"),
                                ("__TICKETS/TASKS/01_draft", "AN-T-11"),
                                ("__PROJECT_CONFIG/09_archived", "AN-P-11")):
            status = "draft" if "01_draft" in folder else "archived"
            ref = f"{atom_id}@1" + ("-draft" if status == "draft" else "")
            path = self.control / folder / f"{ref}--example.md"
            path.parent.mkdir(parents=True)
            header = {"identity": {"atom_id": atom_id}, "context": {"container": {"component": "C0"}},
                      "state": {"status": status, "version": 1, "updated_at": "2026-11-19T00:00:00Z"}}
            path.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n")
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        self.assertEqual({"AN-T-10@1-draft", "AN-P-10@1", "AN-T-11@1-draft", "AN-P-11@1"},
                         {row["ref"] for row in result.atoms if row["id"] in {"AN-T-10", "AN-P-10", "AN-T-11", "AN-P-11"}})

    def test_mixed_project_config_markers_and_nested_definitions(self):
        self.write("002_PROJECT_CONFIG/AN-P-20--legacy.md", "AN-P-20", "active", 1)
        self.write("002_PROJECT_CONFIG/CUSTOM_MODEL/AN-C-21--definition.md", "AN-C-21", "active", 2,
                   {"atom": "AN-P-20"})
        self.write("002_PROJECT_CONFIG/AN-C-21@3-draft--definition.md", "AN-C-21", "draft", 3)
        self.write("002_PROJECT_CONFIG/AN-C-21@1--definition.md", "AN-C-21", "archived", 1)
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        rows = {row["_exact_ref"]: row for row in result.atoms}
        self.assertEqual(("Current", "AN-C-21"), (rows["AN-C-21@2"]["status_group"], rows["AN-C-21@2"]["ref"]))
        self.assertEqual("AN-C-21@3-draft", rows["AN-C-21@3-draft"]["ref"])
        self.assertEqual("AN-C-21@1", rows["AN-C-21@1"]["ref"])
        self.assertEqual("AN-P-20", next(edge for edge in result.containment
                                         if edge["source_ref"] == "AN-C-21")["target_ref"])

    def test_invalid_and_duplicate_carriers_are_reported(self):
        self.write("one/AN-S-1--one.md", "AN-S-1", "active", 1)
        self.write("two/AN-S-1--two.md", "AN-S-1", "active", 2)
        self.write("AN-T-2--bad.md", "AN-T-2", "bogus", 1)
        result = capture_native(self.selection)
        self.assertEqual(3, len(result.errors))
        self.assertTrue(any("Duplicate" in error for error in result.errors.values()))
        self.assertTrue(any("status" in error for error in result.errors.values()))

    def test_installed_methodology_copies_are_excluded(self):
        active = self.write("AN-S-2--definition.md", "AN-S-2", "active", 1)
        copy = self.control / "000_ANECHOIC_framework/sources" / active.name
        copy.parent.mkdir(parents=True)
        copy.write_bytes(active.read_bytes())
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        self.assertEqual({"AN-S-001@1", "AN-S-2@1"}, {row["_exact_ref"] for row in result.atoms})

    def test_incremental_capture_reads_changes_and_matches_full_after_move(self):
        old = self.write("AN-S-2--old.md", "AN-S-2", "active", 1)
        untouched = self.write("AN-S-3--untouched.md", "AN-S-3", "active", 1)
        previous = capture_native(self.selection)
        new = old.with_name("AN-S-2--new.md")
        old.rename(new)
        changed = {PurePosixPath(path.relative_to(self.root).as_posix()) for path in (old, new)}
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ReadContext
        read = ReadContext.read
        with patch.object(ReadContext, "read", autospec=True, side_effect=read) as reads:
            result = capture_native(self.selection, previous=previous, paths=changed)
        self.assertNotIn(untouched, [call.args[1] for call in reads.call_args_list])
        self.assertEqual(capture_native(self.selection), result)

    def test_incremental_duplicate_and_repair(self):
        original = self.write("one/AN-S-2--one.md", "AN-S-2", "active", 1)
        duplicate = self.control / "two" / original.name
        duplicate.parent.mkdir()
        previous = capture_native(self.selection)
        duplicate.write_bytes(original.read_bytes())
        changed = {PurePosixPath(duplicate.relative_to(self.root).as_posix())}
        result = capture_native(self.selection, previous=previous, paths=changed)
        self.assertTrue(any("Duplicate" in error for error in result.errors.values()))
        duplicate.unlink()
        repaired = capture_native(self.selection, previous=result, paths=changed)
        self.assertEqual(capture_native(self.selection), repaired)
        self.assertEqual(repaired, revalidate_native(self.selection, result))

    def test_manifest_drift_refuses_capture(self):
        self.manifest.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Manifest changed"):
            capture_native(self.selection)

    def test_revalidation_refuses_new_carrier_between_inventory_passes(self):
        previous = capture_native(self.selection)

        def capture_then_add(*args, **kwargs):
            captured = capture_native(*args, **kwargs)
            self.write("new/AN-S-2--added.md", "AN-S-2", "active", 1)
            return captured

        with patch(f"{capture_native.__module__}.capture_native", side_effect=capture_then_add):
            with self.assertRaisesRegex(ValueError, "carriers changed during capture"):
                revalidate_native(self.selection, previous)

    def test_archive_rejects_a_draft_marker_and_wrong_tree(self):
        self.write("archived/AN-S-2@1-draft--withdrawn.md", "AN-S-2", "archived", 1)
        self.write("__TKT/ASSETS/AN-S-3--wrong-tree.md", "AN-S-3", "active", 1)
        reports = capture_native(self.selection).errors
        self.assertEqual(2, len(reports))
        self.assertTrue(any("Filename marker" in error for error in reports.values()))
        self.assertTrue(any("logical tree" in error for error in reports.values()))


if __name__ == "__main__":
    unittest.main()
