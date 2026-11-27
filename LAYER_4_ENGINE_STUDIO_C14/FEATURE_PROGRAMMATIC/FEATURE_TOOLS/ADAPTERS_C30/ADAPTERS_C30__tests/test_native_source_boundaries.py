from hashlib import sha256
from pathlib import PurePosixPath
import os
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    ReadContext,
    capture_indexed_lifecycle,
    capture_native,
    revalidate_native,
    status_domains,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__tests.ADAPTERS_C30__tests__shared import (
    NativeCaptureFixture,
)  # fmt: skip


class NativeSourceBoundaryTests(NativeCaptureFixture, unittest.TestCase):
    def _status_bindings(self):
        root = "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
        bindings = {
            "declarations": [
                [
                    name,
                    {
                        "arguments": {
                            "entity_name": "Status",
                            "entity_kind": "Property",
                            "relation_name": "IS_PROPERTY_OF",
                            "base_path": root + ".Header.State",
                            "applies_to_entity_classes": [root + "//" + name],
                            "allowed_values": values,
                        }
                    },
                ]
                for name, values in (
                    ("Specification", ["draft", "active", "archived"]),
                    ("Ticket", ["draft", "active", "archived"]),
                    (
                        "project_config",
                        ["draft", "active", "reviewed", "archived"],
                    ),
                )
            ]
        }
        self._append_primary_declarations(bindings, root)
        self._add_unrelated_status(bindings)
        for _, claim in bindings["declarations"]:
            args = claim["arguments"]
            if "allowed_values" in args:
                args["allowed_values"] = tuple(args["allowed_values"])
                args["applies_to_entity_classes"] = tuple(
                    args["applies_to_entity_classes"]
                )
        return bindings

    def _append_primary_declarations(self, bindings, root):
        for name, class_name in (
            ("Specification", "SpecAtom"),
            ("Ticket", "TicketAtom"),
            ("project_config", "ProjectConfigAtom"),
        ):
            bindings["declarations"].append(
                [
                    "MODEL//ANECHOIC <+ " + root + "//" + name,
                    {
                        "arguments": {
                            "entity_name": name,
                            "entity_class": class_name,
                        }
                    },
                ]
            )

    def _add_unrelated_status(self, bindings):
        unrelated = "Graph/Other/Atom"
        bindings["declarations"].append(
            [
                "other",
                {
                    "arguments": {
                        "entity_name": "Status",
                        "entity_kind": "Property",
                        "relation_name": "IS_PROPERTY_OF",
                        "base_path": unrelated + ".Header.State",
                        "applies_to_entity_classes": [unrelated + "//Ticket"],
                        "allowed_values": ["unrelated"],
                    }
                },
            ]
        )

    def test_capture_uses_admitted_family_status_domains(self):
        bindings = self._status_bindings()
        valid = self.write(
            "__PROJECT_CONFIG/AN-C-1--valid.md", "AN-C-1", "reviewed", 1
        )
        unknown = self.write(
            "__PROJECT_CONFIG/AN-C-2--unknown.md", "AN-C-2", "unknown", 1
        )
        result = capture_native(
            self.selection, domains=status_domains(bindings)
        )
        row = next(row for row in result.atoms if row["id"] == "AN-C-1")
        self.assertEqual(
            ("Current", "AN-C-1", "AN-C-1@1"),
            (row["status_group"], row["ref"], row["_exact_ref"]),
        )
        self.assertNotIn(
            valid.relative_to(self.root).as_posix(), result.errors
        )
        self.assertIn(unknown.relative_to(self.root).as_posix(), result.errors)
        unknown.unlink()
        result = capture_native(
            self.selection, domains=status_domains(bindings)
        )
        domains = status_domains(bindings)
        self.assertEqual(
            domains, revalidate_native(self.selection, result).status_domains
        )
        self._check_indexed_domains(valid, domains)

    def _check_indexed_domains(self, valid, domains):
        descriptor = {
            "id": "AN-C-1",
            "ref": "AN-C-1",
            "_exact_ref": "AN-C-1@1",
            "source_path": valid.relative_to(self.root).as_posix(),
            "version": 1,
            "status": "reviewed",
            "status_group": "Current",
            "owner_kind": "Component",
            "owner_ref": "C0",
            "read": True,
        }
        indexed = capture_indexed_lifecycle(
            self.selection, [descriptor], {}, domains=domains
        )
        self.assertEqual(
            domains, revalidate_native(self.selection, indexed).status_domains
        )
        with self.assertRaisesRegex(ValueError, "identity"):
            capture_indexed_lifecycle(
                self.selection,
                [descriptor | {"status": "unknown"}],
                {},
                domains=domains,
            )

    def test_ingestion_issues_report_malformed_and_duplicate_carriers(self):
        malformed = self.control / "malformed.md"
        malformed.write_text("---\ninvalid: [\n---\n")
        first = self.write("AN-T-8--first.md", "AN-T-8", "active", 1)
        second = self.write("other/AN-T-8--second.md", "AN-T-8", "active", 1)
        third = self.write("AN-T-8--third.md", "AN-T-8", "active", 2)
        result = capture_native(self.selection)
        self.assertEqual(
            "parse_error",
            next(
                i["code"]
                for i in result.ingestion_issues
                if i["relative_path"]
                == malformed.relative_to(self.root).as_posix()
            ),
        )
        for code, paths in (
            ("duplicate_revision", [first, second]),
            ("duplicate_current", [first, second, third]),
        ):
            relatives = sorted(
                p.relative_to(self.root).as_posix() for p in paths
            )
            issues = [i for i in result.ingestion_issues if i["code"] == code]
            self.assertEqual(
                relatives, sorted(i["relative_path"] for i in issues)
            )
            self.assertTrue(
                all(i["related_paths"] == relatives for i in issues)
            )
        self.assertEqual({"AN-S-001"}, {row["ref"] for row in result.atoms})
        self._check_duplicate_removal(result, second, third)

    def _check_duplicate_removal(self, result, second, third):
        second.unlink()
        third.unlink()
        updated = capture_native(
            self.selection,
            previous=result,
            paths={
                PurePosixPath(second.relative_to(self.root).as_posix()),
                PurePosixPath(third.relative_to(self.root).as_posix()),
            },
        )
        self.assertFalse(
            any(
                i["code"].startswith("duplicate_")
                for i in updated.ingestion_issues
            )
        )
        self.assertEqual(
            {"AN-S-001", "AN-T-8"}, {row["ref"] for row in updated.atoms}
        )

    def test_indexed_capture_reads_only_addressed_and_detects_drift(self):
        path = self.write("AN-T-8--task.md", "AN-T-8", "active", 1)
        other = self.write("AN-T-9--other.md", "AN-T-9", "active", 1)
        descriptor = {
            "id": "AN-T-8",
            "ref": "AN-T-8",
            "_exact_ref": "AN-T-8@1",
            "source_path": path.relative_to(self.root).as_posix(),
            "version": 1,
            "status": "active",
            "status_group": "Current",
            "owner_kind": "Component",
            "owner_ref": "C0",
            "read": True,
        }
        original = ReadContext.read

        def read(reader, source, **kwargs):
            self.assertNotEqual(source, other)
            return original(reader, source, **kwargs)

        with patch.object(ReadContext, "read", read):
            path.write_text(path.read_text().replace("Example", "Changed"))
            capture = capture_indexed_lifecycle(
                self.selection,
                [descriptor],
                {"S": "0", "T": "9"},
                lenses=["SPEC"],
            )
            self.assertEqual({"S": 0, "T": 9}, capture.max_numbers)
            self.assertEqual(
                sha256(path.read_bytes()).hexdigest(),
                capture.atoms[0]["_source_sha256"],
            )
            with self.assertRaisesRegex(ValueError, "changed"):
                stale = descriptor | {"version": 2, "_exact_ref": "AN-T-8@2"}
                capture_indexed_lifecycle(self.selection, [stale], {})
            with patch.object(
                ReadContext,
                "read",
                side_effect=AssertionError("unexpected content read"),
            ):
                self.assertEqual(
                    capture.atoms,
                    revalidate_native(self.selection, capture).atoms,
                )
            self._check_indexed_drift(path, other, capture)

    def _check_indexed_drift(self, path, other, capture):
        original_stat = path.stat()
        path.write_text(path.read_text().replace("Changed", "Another"))
        os.utime(
            path, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns)
        )
        with self.assertRaisesRegex(ValueError, "changed"):
            revalidate_native(self.selection, capture)
        path.unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            revalidate_native(self.selection, capture)
        path.symlink_to(other)
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            revalidate_native(self.selection, capture)


if __name__ == "__main__":
    unittest.main()
