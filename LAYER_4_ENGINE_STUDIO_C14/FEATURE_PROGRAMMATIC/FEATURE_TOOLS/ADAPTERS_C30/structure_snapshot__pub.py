"""Read one host-published Structure snapshot without caching it."""

import json
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Mapping

from pydantic import ConfigDict, ValidatorFunctionWrapHandler, field_validator
from pydantic.dataclasses import dataclass


_STRICT = ConfigDict(strict=True, extra="forbid")


def _preserve_mapping(
    value: Mapping, validate: ValidatorFunctionWrapHandler
) -> Mapping:
    """Validate the mapping while preserving its identity and mutability."""
    validate(value)
    return value


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType(
            {key: _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _object(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


@dataclass(frozen=True, config=_STRICT)
class Component:
    parent: str | None
    ref: str
    sha256: str
    fields: Mapping
    source_path: str
    purpose: str | None = None

    _validate_fields = field_validator("fields", mode="wrap")(
        _preserve_mapping
    )

    @property
    def name(self):
        return self.fields["name"]

    @property
    def layer(self):
        return self.fields.get("layer")

    @property
    def lens_whitelist(self):
        return self.fields.get("lens_whitelist")


@dataclass(frozen=True, config=_STRICT)
class ComponentSeed:
    component: str
    ref: str
    sha256: str
    fields: Mapping
    source_path: str

    _validate_fields = field_validator("fields", mode="wrap")(
        _preserve_mapping
    )


@dataclass(frozen=True, config=_STRICT)
class StructureSnapshot:
    model_sha256: str
    project: Mapping
    components: Mapping[str, Component]
    packages: Mapping[str, ComponentSeed]

    _validate_mappings = field_validator(
        "project", "components", "packages", mode="wrap"
    )(_preserve_mapping)

    def component(self, cid: str) -> Component:
        return self.components[cid]


def read_structure(path: Path) -> StructureSnapshot:
    """Load one immutable published view. Propagate read errors."""
    return parse_structure(path.read_bytes())


def _carrier(record, label):
    fields = _object(record.get("fields"), f"{label} fields")
    source_path = _string(record.get("source_path"), f"{label} source_path")
    source = PurePosixPath(source_path)
    if (
        source.is_absolute()
        or ".." in source.parts
        or "\\" in source_path
        or source_path == "."
    ):
        raise ValueError(f"{label} source_path must be control-root-relative")
    return (
        _string(record.get("ref"), f"{label} ref"),
        _string(record.get("sha256"), f"{label} sha256"),
        _freeze(fields),
        source_path,
    )


def parse_structure(content: bytes) -> StructureSnapshot:
    data = _object(
        json.loads(content.decode("utf-8"), object_pairs_hook=_unique_object),
        "snapshot",
    )
    model_sha256 = _string(data.get("model_sha256"), "model_sha256")
    project = _object(data.get("project"), "project")
    _string(project.get("ref"), "project ref")
    _string(project.get("sha256"), "project sha256")
    records = _object(data.get("components"), "components")
    components = {}
    for cid, record in records.items():
        _string(cid, "component ID")
        record = _object(record, f"component {cid}")
        if "parent" not in record:
            raise ValueError(f"component {cid} is missing parent")
        parent = record["parent"]
        if parent is not None:
            _string(parent, f"component {cid} parent")
        component = Component(
            parent, *_carrier(record, f"component {cid}"),
            purpose=record.get("purpose"),
        )
        _string(component.fields.get("name"), f"component {cid} name")
        components[cid] = component
    packages = {}
    for pid, record in _object(data.get("packages", {}), "packages").items():
        label = f"component seed {_string(pid, 'component seed ID')}"
        record = _object(record, label)
        component_id = _string(record.get("component"), f"{label} component")
        if component_id != "C00" and component_id not in components:
            raise ValueError(f"{label} has an unknown component")
        packages[pid] = ComponentSeed(component_id, *_carrier(record, label))
    return StructureSnapshot(
        model_sha256,
        _freeze(project),
        MappingProxyType(components),
        MappingProxyType(packages),
    )


__all__ = ["read_structure"]
