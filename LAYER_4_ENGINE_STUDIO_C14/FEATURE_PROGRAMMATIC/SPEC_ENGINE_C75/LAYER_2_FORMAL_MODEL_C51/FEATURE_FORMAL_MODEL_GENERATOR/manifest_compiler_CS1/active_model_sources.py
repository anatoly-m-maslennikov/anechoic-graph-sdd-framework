"""Select active native Model Claims from their sources."""

import os
from pathlib import Path, PurePosixPath
from ..FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    _check_relation_references,
    _check_node_axes,
    _native_claim_text,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
    parse_native_model_claim,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import (
    ontology_component_path,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import (
    parse_carrier,
)
from .active_source_claims import (
    ModelSourceError,
    _source_error,
    _validate_model_row,
    extend_current_status,
    is_project_model_source,
)
from .active_source_selection import (
    _collect_active_source,
    _collect_manifest_claims as _collect_manifest_claims,
)
from .active_source_inventory import _inventory_active_sources
from .active_source_address import _check_continuant_address
from .active_source_checks import (
    _check_entity_parent_anchors,
    _check_continuant_containment,
    _collect_node_metadata,
)
from .active_source_nodes import (
    _classify_typed_sources,
    _lower_ready_nodes,
    _resolve_typed_scopes,
)
from .typed_node_constraints import lower_node_constraints
from .typed_property_relation_lowering import (
    declared_relation_names,
    lower_typed_fields,
)


def _check_component_path(control, component):
    try:
        relative = component.relative_to(control).as_posix()
    except ValueError:
        relative = ""
    if ontology_component_path(relative) != PurePosixPath(relative):
        raise ValueError(
            "Meta-ontology Component must be a native C9 descendant "
            "of the control root"
        )


def read_active_model_sources(
    control_root: Path,
    component_root: Path,
    *,
    node_locations=None,
    node_metadata=None,
) -> tuple[tuple[str, str, str], ...]:
    control = Path(os.path.abspath(control_root))
    component = Path(os.path.abspath(component_root))
    _check_component_path(control, component)
    reader = ReadContext([str(control)], dict(CEILINGS))
    records, identifiers, subjects, typed = [], set(), set(), []
    if node_locations is None:
        node_locations = {}
    paths = _inventory_active_sources(reader, control, component)
    for path, is_custom in sorted(
        paths, key=lambda entry: entry[0].as_posix()
    ):
        carrier = parse_carrier(reader.read(path), path)
        _collect_active_source(
            path,
            is_custom,
            carrier.metadata,
            carrier.body,
            control,
            identifiers,
            subjects,
            records,
            typed,
            node_locations,
        )
    result = _lower_active_sources(
        records,
        subjects,
        typed,
        has_c9=component.exists() or component.is_symlink(),
        node_metadata=node_metadata,
        node_locations=node_locations,
    )
    if reader.currentness()["state"] != "unchanged":
        raise ValueError("Model source inputs changed during selection")
    return result


def _collect_rows(rows, identifiers, subjects, records, typed, node_locations):
    control = Path("/snapshot")
    seen_paths = set()
    custom_found = False
    for row in rows:
        source = row.get("source_path") if isinstance(row, dict) else None
        exact_ref = row.get("exact_ref") if isinstance(row, dict) else None
        try:
            is_custom = _validate_model_row(row, source, exact_ref, seen_paths)
            custom_found |= is_custom
            _collect_active_source(
                control / source,
                is_custom,
                row["metadata"],
                row["body"],
                control,
                identifiers,
                subjects,
                records,
                typed,
                node_locations,
            )
        except ModelSourceError as error:
            raise ModelSourceError(
                source,
                exact_ref,
                error.detail,
                code=error.code,
                subject=error.subject,
            ) from error
        except (ValueError, TypeError, KeyError) as error:
            raise ModelSourceError(source, exact_ref, str(error)) from error
    return custom_found


def compile_active_model_rows(
    rows, *, has_c9, node_locations=None, node_metadata=None
):
    """Lower ingested carrier rows; None selects the reviewed Model."""
    if type(has_c9) is not bool:
        raise ValueError("has_c9 must be a boolean")
    rows = tuple(rows)
    records, identifiers, subjects, typed = [], set(), set(), []
    if node_locations is None:
        node_locations = {}
    custom_found = _collect_rows(
        rows, identifiers, subjects, records, typed, node_locations
    )
    if not has_c9:
        if custom_found:
            raise ValueError("Custom Model sources require an active C9 Model")
        return None
    return _lower_rows(
        rows, records, subjects, typed, node_metadata, node_locations
    )


def _lower_rows(rows, records, subjects, typed, node_metadata, node_locations):
    try:
        return _lower_active_sources(
            records,
            subjects,
            typed,
            has_c9=True,
            node_metadata=node_metadata,
            node_locations=node_locations,
        )
    except ModelSourceError as error:
        match = next(
            (row for row in rows if row["source_path"] == error.source_path),
            None,
        )
        if match:
            raise ModelSourceError(
                error.source_path,
                match["exact_ref"],
                error.detail,
                code=error.code,
                subject=error.subject,
            ) from error
        raise
    except (ValueError, SyntaxError) as error:
        message = str(error)
        match = next(
            (
                row
                for row in rows
                if message.startswith(row["source_path"] + "@")
            ),
            None,
        )
        raise ModelSourceError(
            match["source_path"] if match else None,
            match["exact_ref"] if match else None,
            message,
        ) from error


def _lower_fields(
    field_sources,
    derived_scopes,
    addresses,
    relation_names,
    records,
    append_claim,
):
    for source, scope, text, kind in sorted(
        field_sources, key=lambda row: is_project_model_source(row[0])
    ):
        scope = derived_scopes.get(source, scope)
        if scope is None:
            raise ValueError(f"{source}: typed field requires a Model scope")
        try:
            claim = (
                lower_node_constraints(text, scope, addresses)
                if kind == "manifest_constraints"
                else lower_typed_fields(
                    kind, text, scope, addresses, relation_names=relation_names
                )
            )
        except ValueError as error:
            raise ValueError(f"{source}: {error}") from error
        _check_continuant_address(source, scope, text, kind, addresses, claim)
        _native_claim_text("```python\n" + claim + "\n```\n", source, scope)
        if (
            kind == "manifest_property"
            and is_project_model_source(source)
            and extend_current_status(source, scope, claim, records, addresses)
        ):
            continue
        append_claim(source, scope, claim)


def _validate_lowered(records, typed, has_c9):
    _check_continuant_containment(records, typed)
    _check_node_axes(
        [
            (source, subject, parse_native_model_claim(claim))
            for source, subject, claim in records
        ],
        {
            source
            for source, _, _, kind in typed
            if kind in (None, "manifest_node")
        }
        | {
            source
            for source, _, _ in records
            if is_project_model_source(source)
        },
    )
    if has_c9:
        if not records:
            raise ValueError("No active Model Claims were selected")
        _check_relation_references(records)


def _claim_appender(records, subjects):
    def append_claim(source, subject, claim):
        if subject in subjects:
            raise _source_error(
                source,
                "duplicate_model_subject",
                subject,
                "duplicate Model Subject",
            )
        subjects.add(subject)
        records.append((source, subject, claim))

    return append_claim


def _lower_active_sources(
    records,
    subjects,
    typed,
    *,
    has_c9,
    node_metadata=None,
    node_locations=None,
):
    pending, field_sources = _classify_typed_sources(typed)
    node_sources = pending[:]
    relation_names = declared_relation_names(records, field_sources)
    addresses, derived_scopes = _resolve_typed_scopes(
        records, typed, field_sources
    )
    _check_entity_parent_anchors(
        records, [(source, scope) for source, scope, _, _ in pending if scope]
    )
    for source, scope, text, kind in pending:
        if scope:
            _check_continuant_address(source, scope, text, kind, addresses)

    append_claim = _claim_appender(records, subjects)
    _lower_ready_nodes(pending, records, append_claim, require_all=False)
    _lower_fields(
        field_sources,
        derived_scopes,
        addresses,
        relation_names,
        records,
        append_claim,
    )
    _lower_ready_nodes(pending, records, append_claim, require_all=True)
    _collect_node_metadata(
        records, node_sources, addresses, node_locations, node_metadata
    )
    _validate_lowered(records, typed, has_c9)
    return tuple(records)
