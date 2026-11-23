from __future__ import annotations

import hashlib
import os
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_content  # noqa: E402
def extension_directory(root: Path) -> Path:
    """Use the suite-prepared DuckPGQ cache, overridable for local runs."""
    return Path(os.environ.get(
        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
        root / ".anechoic_tmp" / "workbench" / "extensions",
    ))


class QueryStoreFixture:
    def setUp(self) -> None:
        self.store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))

    def tearDown(self) -> None:
        self.store.close()

    @staticmethod
    def atom(
        ref: str | None,
        edges: list[dict] | None = None,
        *,
        source_path: str | None = None,
        body: str = "# Claim\n",
    ) -> dict:
        base_id = ref.split("@", 1)[0] if ref else None
        return {
            "source_path": source_path or f"{ref or 'anonymous'}.md",
            "status_group": "Draft" if ref and "@" in ref else "Current",
            "id": base_id,
            "ref": ref,
            "version": 2 if ref and "@" in ref else 1,
            "status": "Active",
            "current_scope_unit": None,
            "claim_target_scope_unit": None,
            "role": "Requirement",
            "form": "Declaration",
            "tier": 4,
            "updated_at": None,
            "header_json": {
                "atom_id": base_id,
                "version": 2 if ref and "@" in ref else 1,
                "status": "Active",
                "role": "Requirement",
                "form": "Declaration",
                "tier": 4,
                "present": True,
                "nested": {"zero": 0, "empty": None},
            },
            "content_markdown": body,
            "content_properties_json": parse_content(body, tolerate_duplicate_siblings=True),
            "relation_edges_json": edges or [],
            "hash": f"atom-{ref or 'anonymous'}",
        }

    @staticmethod
    def scope(name: str, edges: list[dict] | None = None) -> dict:
        return {
            "name": name,
            "scope_unit_id": None,
            "parent_name": None,
            "declared_label": None,
            "ordered": False,
            "order_number": None,
            "declaration_source_path": f"{name}.declaration.md",
            "declaration_version": 1,
            "relation_edges_json": edges or [],
            "hash": f"scope-{name}",
        }

    @staticmethod
    def edge(source_kind: str, source_ref: str, target_kind: str, target_ref: str,
             relation_type: str = "CONTAINS", derived: bool = False) -> dict:
        return {
            "source_kind": source_kind,
            "source_ref": source_ref,
            "target_kind": target_kind,
            "target_ref": target_ref,
            "relation_type": relation_type,
            "derived": derived,
        }

    @staticmethod
    def mapping_hash(value: dict) -> str:
        return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

