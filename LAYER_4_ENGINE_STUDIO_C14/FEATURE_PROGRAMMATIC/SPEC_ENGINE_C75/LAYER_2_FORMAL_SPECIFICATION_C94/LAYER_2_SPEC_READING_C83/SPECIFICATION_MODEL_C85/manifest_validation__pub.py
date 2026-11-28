"""Validate the modeled declarations in one parsed Component Manifest."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ADAPTERS_C30.structure.code_access_rules__pub import (
    parse_code_access,
)  # fmt: skip

from ...LAYER_1_DIAGNOSTICS_C90._package__shared import finding
from .trace_manifest__pub import http_routes, outcome_cases
from .shape_model__pub import manifest_shape


def validate_manifest(manifest):
    (
        "Return source-linked issues and unresolved semantics "
        "without reading other artifacts."
    )  # fmt: skip
    source = manifest["source"]
    fields = manifest["fields"]
    if not isinstance(fields, dict):
        return {
            "issues": [
                finding(source, "fields", "Manifest fields must be a mapping")
            ],
            "unresolved": [],
        }
    issues = _field_issues(fields, source)
    boundaries = fields.get("boundaries")
    if manifest.get("boundaries") != boundaries:
        issues.append(
            finding(
                source,
                "boundaries",
                "Parsed boundaries contradict Manifest fields",
            )
        )
    _validate_state(boundaries, issues, source)
    io_complete = _validate_io(boundaries, issues, source)
    imports = exports = None
    try:
        imports, exports = parse_code_access(boundaries)
    except ValueError as error:
        issues.append(finding(source, "boundaries", str(error)))
    return {
        "issues": issues,
        "unresolved": _unresolved_boundaries(
            boundaries, imports, exports, source, io_complete
        ),
    }


def _validate_state(boundaries, issues, source):
    if isinstance(boundaries, dict) and isinstance(
        boundaries.get("state"), dict
    ):
        for name in ("reads", "writes"):
            value = boundaries["state"].get(name)
            if name in boundaries["state"] and (
                not isinstance(value, list)
                or any(not isinstance(x, str) or not x.strip() for x in value)
            ):
                issues.append(
                    finding(
                        source,
                        f"boundaries.state.{name}",
                        "Must be a list of nonblank strings",
                    )
                )


def _validate_io(boundaries, issues, source):
    io_complete = False
    try:
        _, io_complete = outcome_cases(boundaries)
    except ValueError as error:
        issues.append(finding(source, "boundaries.io.server", str(error)))
    io = boundaries.get("io") if isinstance(boundaries, dict) else None
    issues.extend(_route_issues(io, source))
    try:
        if manifest_shape(boundaries) is not None and (
            set(io) == {"class_shapes"}
            or (
                set(io) == {"server"}
                and set(io["server"]) == {"bundled_model_classes"}
            )
        ):
            io_complete = True
    except ValueError as error:
        shape_field = (
            "class_shapes"
            if "class_shapes" in io
            else "server.bundled_model_classes"
        )
        issues.append(
            finding(source, f"boundaries.io.{shape_field}", str(error))
        )
    return io_complete


def _route_issues(io, source):
    if not isinstance(io, dict):
        return
    for side in ("server", "client"):
        interfaces = io.get(side)
        entries = interfaces.items() if isinstance(interfaces, dict) else ()
        if side == "client" and isinstance(interfaces, list):
            entries = enumerate(interfaces)
        for name, interface in entries:
            if (
                isinstance(interface, dict)
                and interface.get("transport") == "http"
                and "routes" in interface
            ):
                try:
                    http_routes(interface["routes"])
                except ValueError as error:
                    yield finding(
                        source,
                        f"boundaries.io.{side}.{name}.routes",
                        str(error),
                    )


def _field_issues(fields, source):
    issues = []
    for name in ("component_id", "name"):
        if not isinstance(fields.get(name), str) or not fields[name].strip():
            issues.append(
                finding(
                    source, name, "Required field must be a nonempty string"
                )
            )
    unknown = fields.keys() - {
        "component_id",
        "name",
        "layer",
        "lens_whitelist",
        "boundaries",
    }
    issues.extend(
        finding(source, name, "Unknown Manifest field")
        for name in sorted(unknown)
    )
    if fields.get("layer") is not None and type(fields["layer"]) is not int:
        issues.append(
            finding(source, "layer", "Layer must be an integer or null")
        )
    lenses = fields.get("lens_whitelist")
    if lenses is not None and (
        not isinstance(lenses, list)
        or any(not isinstance(x, str) for x in lenses)
    ):
        issues.append(
            finding(
                source,
                "lens_whitelist",
                "Lens whitelist must be a list of strings or null",
            )
        )
    return issues


def _unresolved_boundaries(boundaries, imports, exports, source, io_complete):
    if boundaries is None or boundaries == {}:
        return [
            finding(
                source, "boundaries", "No boundary declarations are modeled"
            )
        ]
    if not isinstance(boundaries, dict):
        return []
    unresolved = [
        finding(
            source,
            f"boundaries.{name}",
            "Declaration semantics are not modeled",
        )
        for name in ("process", "state", "io")
        if name in boundaries
        and not (
            name == "state" and boundaries[name] == {"reads": [], "writes": []}
        )
        and not (name == "io" and io_complete)
    ]
    if imports is not None and imports[1]:
        unresolved.append(
            finding(
                source,
                "boundaries.code.imports",
                "Selector resolution requires external context",
            )
        )
    if exports:
        unresolved.append(
            finding(
                source,
                "boundaries.code.exports",
                "Export visibility requires external context",
            )
        )
    return unresolved
