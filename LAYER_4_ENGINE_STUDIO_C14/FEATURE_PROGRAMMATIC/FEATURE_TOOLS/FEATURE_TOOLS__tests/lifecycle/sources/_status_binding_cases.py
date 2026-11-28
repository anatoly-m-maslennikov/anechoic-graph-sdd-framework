"""Check Status Specification binds against exact native sources."""

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    NATIVE_LIFECYCLE__shared import (
    NativeWorkflowDefinitionError,
    bind_status_specifications,
)

STUDIO = Path(__file__).resolve().parents[5]


class _StatusBindingCases:
    def _status_binding(self):
        methodology = Path("ONTOLOGY_SCORE_C82") / "OCCURRENT_METRONOME_C58"
        source = STUDIO.parent / "_anechoic_anechoic" / methodology
        rows = []
        for atom_id in ("AN-S-1928", "AN-S-1834", "AN-S-1831"):
            (original,) = source.rglob(f"{atom_id}-MTD-*.md")
            raw = original.read_bytes()
            header = yaml.safe_load(raw.split(b"---", 2)[1])
            native = f"{atom_id}@{header['state']['version']}"
            relative = (
                Path(self.control) / methodology / original.relative_to(source)
            )
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            rows.append(
                {
                    "_exact_ref": native,
                    "status_group": "Current",
                    "source_path": relative.as_posix(),
                    "_source_sha256": sha256(raw).hexdigest(),
                }
            )
        return rows

    def _relocated_status_binding(self):
        rows, pins = [], {}
        for index, kind in enumerate(("workflow", "step", "action"), 1):
            atom_id = f"AN-S-{index + 10}"
            relative = (
                f"{self.control}"
                "/ONTOLOGY_SCORE_C91/OCCURRENT_METRONOME_C58/_DOM/MTD/"
                f"{atom_id}"
                "-MTD-"
                f"{kind.upper()}"
                "--fixture.md"
            )
            path = self._write(
                relative,
                {
                    "identity": {"atom_id": atom_id},
                    "context": {"template": kind, "lens": "DOM/MTD"},
                    "state": {"status": "active", "version": 1},
                },
                "## Summary\n\nFixture.\n",
            )
            raw = path.read_bytes()
            pins[kind] = (
                f"{atom_id}@1",
                sha256(raw.partition(b"\n---\n")[2]).hexdigest(),
            )
            rows.append(
                {
                    "_exact_ref": f"{atom_id}@1",
                    "status_group": "Current",
                    "source_path": relative,
                    "_source_sha256": sha256(raw).hexdigest(),
                }
            )
        return rows, pins

    def test_relocated_status_binding_checks_component_and_lens(self):
        rows, pins = self._relocated_status_binding()
        with patch(
            (
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE."
                "NATIVE_LIFECYCLE.native_workflow_definition.STA"
                "TUS_SPECIFICATIONS"
            ),
            pins,
        ):
            bind_status_specifications(self.selection, current_rows=rows)()
            rows[0]["source_path"] = rows[0]["source_path"].replace(
                "OCCURRENT_METRONOME_C58", "OTHER_C8"
            )
            with self.assertRaisesRegex(NativeWorkflowDefinitionError, "path"):
                bind_status_specifications(self.selection, current_rows=rows)

    def test_native_status_binding_checks_sources_and_manifest(self):
        rows = self._status_binding()
        check = bind_status_specifications(self.selection, current_rows=rows)
        check()
        for row in rows:
            path = self.root / row["source_path"]
            original = path.read_bytes()
            path.write_bytes(original + b"changed")
            with self.assertRaisesRegex(
                NativeWorkflowDefinitionError, "changed"
            ):
                check()
            row["_source_sha256"] = sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(
                NativeWorkflowDefinitionError, "body differs"
            ):
                bind_status_specifications(self.selection, current_rows=rows)
            path.write_bytes(original)
            row["_source_sha256"] = sha256(original).hexdigest()
        self.manifest.write_bytes(self.manifest.read_bytes() + b"changed")
        with self.assertRaisesRegex(
            NativeWorkflowDefinitionError, "AN-S-1@1 changed"
        ):
            check()

    def test_native_status_binding_refuses_invalid_inventory_and_header(self):
        rows = self._status_binding()
        for invalid in (rows + rows[:1], rows[1:]):
            with self.assertRaisesRegex(
                NativeWorkflowDefinitionError, "Missing or ambiguous"
            ):
                bind_status_specifications(
                    self.selection, current_rows=invalid
                )
        path = self.root / rows[0]["source_path"]
        header, delimiter, body = path.read_bytes().partition(b"\n---\n")
        metadata = yaml.safe_load(header.removeprefix(b"---\n"))
        metadata["state"]["status"] = "draft"
        path.write_bytes(
            b"---\n"
            + yaml.safe_dump(metadata, sort_keys=False).rstrip().encode()
            + delimiter
            + body
        )
        rows[0]["_source_sha256"] = sha256(path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(
            NativeWorkflowDefinitionError, "Expected active native workflow"
        ):
            bind_status_specifications(self.selection, current_rows=rows)
