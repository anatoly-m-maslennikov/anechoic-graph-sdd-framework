"""Applicable Methodology candidate records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.artifact_metadata import SETTINGS_PATH


DEFAULT_CONTROL_ROOT = SETTINGS_PATH.parent
FRAMEWORK_APPLICABLE_RELATIVE = Path("000_ANECHOIC_framework/00_APPLICABLE_METHODOLOGY")
OUTPUT_RELATIVE = DEFAULT_CONTROL_ROOT / FRAMEWORK_APPLICABLE_RELATIVE

@dataclass(frozen=True)
class Candidate:
    layer: str
    layer_order: int
    role: str
    role_directory: str
    atom_id: str
    version: int
    source_path: str
    source_sha256: str
    basename: str
    priority: str | None
    priority_group: str | None
    replacements: tuple[str, ...]
    incompatibilities: tuple[str, ...]
    definition_term: str | None
    definition_subject_path: str | None
    output_relative: str = OUTPUT_RELATIVE.as_posix()
    extension_id: str | None = None
    extension_revision: str | None = None
    original_relations_sha256: str = ""
    definition_namespace: str = ""

    def frontier_record(self) -> dict[str, object]:
        return {
            "source_layer": self.layer,
            "atom_id": self.atom_id,
            "source_atom_id": self.atom_id,
            "atom_revision": self.version,
            "source_atom_revision": self.version,
            "source_carrier_path": self.source_path,
            "source_carrier_sha256": self.source_sha256,
            "original_relations_sha256": self.original_relations_sha256,
            **({"extension_id": self.extension_id, "extension_revision": self.extension_revision}
               if self.extension_id is not None else {}),
        }

    def report_record(self) -> dict[str, object]:
        record = {
            **self.frontier_record(),
            "content_role": self.role,
            "output_path": f"{self.output_relative}/{self.role_directory}/{self.basename}",
        }
        if self.definition_term is not None:
            record["definition_term"] = (
                f"{self.definition_namespace} <+ Term//{self.definition_term}"
                if self.definition_namespace else self.definition_term
            )
            record["definition_namespace"] = self.definition_namespace
            record["definition_term_name"] = self.definition_term
            record["definition_subject_path"] = self.definition_subject_path
        return record
