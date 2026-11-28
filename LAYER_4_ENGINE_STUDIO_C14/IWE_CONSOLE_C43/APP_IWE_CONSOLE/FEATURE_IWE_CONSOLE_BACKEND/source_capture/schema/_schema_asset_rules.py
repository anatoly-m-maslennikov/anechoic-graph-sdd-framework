"""Validate delivered Content and Header schema rules."""

from __future__ import annotations

from typing import Any

from . import workbench_schema_asset as runtime


def _content_schema(payload: object) -> runtime.ContentSchema:
    if not isinstance(payload, dict) or not isinstance(
        payload.get("rules"), list
    ):
        raise ValueError("invalid delivered Content schema")
    rules = []
    for item in payload["rules"]:
        rules.append(_content_rule(item))
    schema = runtime._schema_from_rules(rules)
    if runtime._content_asset(schema) != payload:
        raise ValueError("invalid delivered Content schema shape")
    return schema


def _content_rule(item):
    if not isinstance(item, dict) or set(item) != {
        "path",
        "roles",
        "forms",
        "value_bearing",
        "prohibited",
        "source",
        "provenance",
    }:
        raise ValueError("invalid delivered Content rule")
    path = item["path"]
    if (
        not isinstance(path, list)
        or not path
        or not all(isinstance(part, str) and part for part in path)
        or type(item["value_bearing"]) is not bool
        or type(item["prohibited"]) is not bool
        or not isinstance(item["provenance"], list)
    ):
        raise ValueError("invalid delivered Content rule")
    source = runtime._content_source(item["source"])
    provenance = tuple(
        runtime._content_source(value) for value in item["provenance"]
    )
    if len(set(provenance)) != len(provenance):
        raise ValueError("duplicate delivered Content provenance")
    return runtime.ContentRule(
        tuple(path),
        runtime._selector(item["roles"]),
        runtime._selector(item["forms"]),
        item["value_bearing"],
        source,
        item["prohibited"],
        provenance,
    )


def _content_source(value: object) -> runtime.DeclarationSource:
    if not isinstance(value, dict) or set(value) != {
        "reference",
        "version",
        "source_path",
    }:
        raise ValueError("invalid delivered Content source")
    reference, version, source_path = (
        value["reference"],
        value["version"],
        value["source_path"],
    )
    if (
        reference is not None
        and not isinstance(reference, str)
        or version is not None
        and (type(version) is not int or version < 1)
        or source_path is not None
        and not isinstance(source_path, str)
    ):
        raise ValueError("invalid delivered Content source")
    return runtime.DeclarationSource(reference, version, source_path)


def _source_pin(row: dict[str, Any]) -> dict[str, Any]:
    body = row.get("_content_bytes")
    path = row.get("source_path")
    atom_id = row.get("id")
    version = row.get("version")
    if not isinstance(body, bytes):
        raise ValueError(f"{path}: captured Markdown is unavailable")
    if not isinstance(path, str) or not path:
        raise ValueError("schema source pin needs a source path")
    return {
        "atom_id": atom_id if isinstance(atom_id, str) and atom_id else None,
        "version": version if type(version) is int and version > 0 else None,
        "path": path,
        "fingerprint": runtime.hashlib.sha256(
            runtime.canonical(
                {
                    "header": row.get("header_json"),
                    "body_sha256": runtime.hashlib.sha256(body).hexdigest(),
                }
            ).encode("utf-8")
        ).hexdigest(),
    }


def _header_schema(payload: object) -> runtime.HeaderSchema:
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("invalid delivered Header schema")
    columns = payload.get("header_columns")
    if not isinstance(columns, list):
        raise ValueError("invalid delivered Header columns")
    result = []
    for item in columns:
        if not isinstance(item, dict):
            raise ValueError("invalid delivered Header column")
        path = item.get("path")
        name = item.get("name")
        format_name = item.get("format")
        populated = item.get("populated")
        reader = item.get("reader")
        if (
            not isinstance(path, list)
            or not path
            or not all(isinstance(part, str) and part for part in path)
            or not isinstance(name, str)
            or not name.startswith("header.")
            or not isinstance(format_name, str)
            or type(populated) is not bool
            or reader is not None
            and not isinstance(reader, str)
        ):
            raise ValueError("invalid delivered Header column")
        rules = item.get("rules", [])
        if not isinstance(rules, list):
            raise ValueError("invalid delivered Header rules")
        result.append(
            runtime.HeaderColumn(
                tuple(path),
                name,
                format_name,
                populated,
                reader,
                tuple(runtime._header_rule(rule) for rule in rules),
            )
        )
    return runtime.HeaderSchema(tuple(result))


def _header_rule(payload: object) -> runtime.HeaderRule:
    if not isinstance(payload, dict):
        raise ValueError("invalid delivered Header declaration rule")
    path = payload.get("path")
    format_name = payload.get("format")
    roles = runtime._selector(payload.get("roles"))
    forms = runtime._selector(payload.get("forms"))
    source = payload.get("source")
    if (
        not isinstance(path, list)
        or not path
        or not all(isinstance(part, str) and part for part in path)
        or not isinstance(format_name, str)
        or not isinstance(source, dict)
    ):
        raise ValueError("invalid delivered Header declaration rule")
    reference = source.get("reference")
    version = source.get("version")
    source_path = source.get("source_path")
    if (
        reference is not None
        and not isinstance(reference, str)
        or version is not None
        and (type(version) is not int or version < 1)
        or source_path is not None
        and not isinstance(source_path, str)
    ):
        raise ValueError("invalid delivered Header declaration source")
    provenance = _header_provenance(payload)
    format_source = _header_format_source(payload)
    return runtime.HeaderRule(
        tuple(path),
        format_name,
        roles,
        forms,
        runtime.DeclarationSource(reference, version, source_path),
        format_source,
        provenance,
    )


def _header_provenance(payload):
    raw_provenance = payload.get("provenance")
    if not isinstance(raw_provenance, list):
        raise ValueError("invalid delivered Header provenance")
    provenance = tuple(
        runtime._content_source(value) for value in raw_provenance
    )
    if len(set(provenance)) != len(provenance):
        raise ValueError("duplicate delivered Header provenance")
    return provenance


def _header_format_source(payload):
    format_source = payload.get("format_source")
    if format_source is not None:
        if not isinstance(format_source, dict) or set(format_source) != {
            "reference",
            "version",
            "source_path",
        }:
            raise ValueError("invalid delivered Header format source")
        format_reference, format_version, format_path = (
            format_source["reference"],
            format_source["version"],
            format_source["source_path"],
        )
        if (
            format_reference is not None
            and not isinstance(format_reference, str)
            or format_version is not None
            and (type(format_version) is not int or format_version < 1)
            or format_path is not None
            and not isinstance(format_path, str)
        ):
            raise ValueError("invalid delivered Header format source")
        format_source = runtime.DeclarationSource(
            format_reference, format_version, format_path
        )
    return format_source


def _selector(value: object) -> frozenset[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ValueError("invalid delivered Header declaration selector")
    return frozenset(value)
