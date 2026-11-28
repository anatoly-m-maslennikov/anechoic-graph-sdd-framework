"""Compile and validate the delivered Workbench schema asset."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    ContentRule as ContentRule,
    ContentSchema,
    DeclarationSource as DeclarationSource,
    _schema_from_rules as _schema_from_rules,
)
from ._schema_asset_rules import (
    _content_schema as _content_schema,
    _content_source as _content_source,
    _source_pin as _source_pin,
    _header_schema as _header_schema,
    _header_rule as _header_rule,
    _selector as _selector,
)

from .declared_axes import compile_role_folders as compile_role_folders
from .declared_axes import compile_status_groups as compile_status_groups
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    HeaderRule as HeaderRule,
    compile_header_rules,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    HeaderColumn as HeaderColumn,
    HeaderSchema,
    declared_header_schema,
    infer_header_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    canonical,
)


DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "workbench_schema.json"


class SchemaCompilation(BaseModel):
    """The two admitted Header modes plus one declared Content schema."""

    model_config = ConfigDict(
        strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True
    )

    mode_one: HeaderSchema
    mode_two: HeaderSchema
    content: ContentSchema
    status_groups: tuple[tuple[str, str, str], ...] = ()
    role_folders: tuple[tuple[str, str], ...] | None = None

    def header(self, mode: int) -> HeaderSchema:
        if mode == 1:
            return self.mode_one
        if mode == 2:
            return self.mode_two
        raise ValueError("workbench.schema_mode must be 1 or 2")


def compile_schema(
    atoms: list[dict[str, Any]],
    content: ContentSchema,
    declared_header: HeaderSchema | None = None,
    status_groups: tuple[tuple[str, str, str], ...] = (),
    role_folders: tuple[tuple[str, str], ...] | None = None,
) -> SchemaCompilation:
    """Build both projections from the one accepted source capture."""
    return SchemaCompilation(
        mode_one=declared_header
        or declared_header_schema(compile_header_rules(atoms)),
        mode_two=infer_header_schema(atoms),
        content=content,
        status_groups=status_groups,
        role_folders=role_folders,
    )


def schema_asset(
    atoms: list[dict[str, Any]],
    compilation: SchemaCompilation,
) -> bytes:
    """Serialize a deterministic asset without retaining source bodies."""
    payload: dict[str, Any] = {
        "schema_version": 2,
        "modes": {
            "1": {
                "header": compilation.mode_one.asset(),
                "content": _content_asset(compilation.content),
            },
            "2": {
                "header": compilation.mode_two.asset(),
                "content": _content_asset(compilation.content),
            },
        },
        "sources": sorted(
            (_source_pin(row) for row in atoms),
            key=lambda source: source["path"],
        ),
    }
    if compilation.status_groups:
        payload["schema_version"] = 3
        payload["status_groups"] = [
            list(row) for row in compilation.status_groups
        ]
    if compilation.role_folders is not None:
        payload["schema_version"] = 4
        payload["status_groups"] = [
            list(row) for row in compilation.status_groups
        ]
        payload["role_folders"] = [
            list(row) for row in compilation.role_folders
        ]
    payload["input_digest"] = hashlib.sha256(
        canonical(payload).encode("utf-8")
    ).hexdigest()
    return (
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        + b"\n"
    )


def _content_asset(schema: ContentSchema) -> dict[str, object]:
    payload = schema.asset()
    payload["rules"] = [
        {
            "path": list(rule.path),
            "roles": sorted(rule.roles) if rule.roles is not None else None,
            "forms": sorted(rule.forms) if rule.forms is not None else None,
            "value_bearing": rule.value_bearing,
            "prohibited": rule.prohibited,
            "source": rule.source.asset(),
            "provenance": [source.asset() for source in rule.provenance],
        }
        for rule in schema.rules
    ]
    return payload


def load_image_schema(path: Path = DEFAULT_SCHEMA_PATH) -> SchemaCompilation:
    """Load and validate the self-contained schema delivered in the image.

    This checks the asset itself, never the current source tree. A missing or
    invalid image asset is an error and requires rebuilding the image.
    """
    try:
        payload = _read_schema_payload(path)
        groups, folders = _axis_rows(payload)
        _validate_source_pins(payload["sources"])
        modes = payload["modes"]
        if not isinstance(modes, dict) or set(modes) != {"1", "2"}:
            raise ValueError("invalid schema modes")
        if any(
            not isinstance(mode, dict) or set(mode) != {"header", "content"}
            for mode in modes.values()
        ):
            raise ValueError("invalid schema mode")
        content = _content_schema(modes["1"]["content"])
        if modes["2"]["content"] != _content_asset(content):
            raise ValueError("inconsistent content schemas")
        headers = [
            _header_schema(modes[mode]["header"]) for mode in ("1", "2")
        ]
        if any(
            headers[index].asset() != modes[mode]["header"]
            for index, mode in enumerate(("1", "2"))
        ):
            raise ValueError("invalid header schema shape")
        return SchemaCompilation(
            mode_one=headers[0],
            mode_two=headers[1],
            content=content,
            status_groups=groups,
            role_folders=folders,
        )
    except (OSError, KeyError, TypeError, UnicodeError, ValueError) as exc:
        raise ValueError(f"invalid delivered Workbench schema: {exc}") from exc


def _read_schema_payload(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("schema asset is missing or is a symlink")
    payload = json.loads(path.read_bytes())
    if not isinstance(payload, dict) or set(payload) not in (
        {"schema_version", "modes", "sources", "input_digest"},
        {
            "schema_version",
            "modes",
            "sources",
            "input_digest",
            "status_groups",
        },
        {
            "schema_version",
            "modes",
            "sources",
            "input_digest",
            "status_groups",
            "role_folders",
        },
    ):
        raise ValueError("invalid schema asset shape")
    digest = payload.pop("input_digest")
    if (
        not isinstance(digest, str)
        or digest
        != hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    ):
        raise ValueError("schema asset digest mismatch")
    if (
        type(payload["schema_version"]) is not int
        or payload["schema_version"] not in (2, 3, 4)
        or (payload["schema_version"] >= 3) != ("status_groups" in payload)
        or (payload["schema_version"] == 4) != ("role_folders" in payload)
    ):
        raise ValueError("unsupported schema asset version")
    return payload


def _axis_rows(
    payload: dict[str, Any],
) -> tuple[
    tuple[tuple[str, str, str], ...], tuple[tuple[str, str], ...] | None
]:
    groups = payload.get("status_groups", [])
    if (
        not isinstance(groups, list)
        or any(
            not isinstance(row, list)
            or len(row) != 3
            or any(not isinstance(value, str) or not value for value in row)
            for row in groups
        )
        or groups != sorted(groups)
        or len({tuple(row[:2]) for row in groups}) != len(groups)
    ):
        raise ValueError("invalid Status Groups")
    folders = payload.get("role_folders")
    if folders is not None and (
        not isinstance(folders, list)
        or any(
            not isinstance(row, list)
            or len(row) != 2
            or any(not isinstance(value, str) or not value for value in row)
            for row in folders
        )
        or folders != sorted(folders)
        or len({row[0] for row in folders}) != len(folders)
        or len({row[1] for row in folders}) != len(folders)
    ):
        raise ValueError("invalid Role folders")
    return tuple(map(tuple, groups)), None if folders is None else tuple(
        map(tuple, folders)
    )


def _validate_source_pins(value: object) -> None:
    sources = value
    if not isinstance(sources, list):
        raise ValueError("invalid schema source pins")
    for source in sources:
        if (
            not isinstance(source, dict)
            or set(source) != {"atom_id", "version", "path", "fingerprint"}
            or source["atom_id"] is not None
            and (
                not isinstance(source["atom_id"], str) or not source["atom_id"]
            )
            or source["version"] is not None
            and (type(source["version"]) is not int or source["version"] < 1)
            or not isinstance(source["path"], str)
            or not source["path"]
            or not isinstance(source["fingerprint"], str)
            or len(source["fingerprint"]) != 64
            or any(c not in "0123456789abcdef" for c in source["fingerprint"])
        ):
            raise ValueError("invalid schema source pin")
    if sources != sorted(sources, key=lambda source: source["path"]):
        raise ValueError("invalid schema source pin order")
