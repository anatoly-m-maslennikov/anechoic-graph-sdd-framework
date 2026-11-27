"""Read and decode guarded native Project Manifest carriers."""

from datetime import datetime
from pathlib import Path
import re

from .ADAPTERS_C30__pub import LimitReached, ReadContext
from .atom_reference__pub import derive_atom_ref
from .carrier_read__pub import ParsedCarrier, parse_carrier
from .formal_claim__pub import formal_claim, formal_manifest
from .native_carrier_header__pub import (
    native_header_model_fields,
    native_header_view,
)
from .native_model_claim__pub import parse_manifest_declaration
from .markdown_content__pub import parse_content


class ProjectSelectionError(ValueError):
    """An attributable refusal, without substituting another Project."""

    code = "PROJECT_SELECTION_REFUSED"
    condition = code


def _manifest_paths(reader: ReadContext, control: Path):
    for path in reader.inventory_shallow(control):
        if path.suffix == ".md":
            yield path


def manifest_sources(
    reader: ReadContext, control: Path, *, root_candidates=False
):
    for path in _manifest_paths(reader, control):
        named_manifest = bool(
            re.search(r"[-.]PROJECT_MANIFEST(?:[-.]|$)", path.name)
        )
        if root_candidates and "-PROJECT_MANIFEST--" not in path.name:
            continue
        try:
            carrier = parse_carrier(reader.read(path), path)
        except (OSError, ValueError, LimitReached) as error:
            if (
                named_manifest
                or isinstance(error, LimitReached)
                and error.limit != "max_file_bytes"
            ):
                raise
            continue
        if "atom_family" in carrier.metadata or re.match(
            r"[A-Z]+-S-", path.name
        ):
            try:
                native_header_view(carrier.metadata)
            except ValueError:
                context = carrier.metadata.get("context")
                if (
                    named_manifest
                    or isinstance(context, dict)
                    and context.get("template") == "project_manifest"
                ):
                    raise
                continue
            yield path, carrier


def active_manifest_carriers(
    reader: ReadContext, control: Path, *, root_candidates=False
):
    for path, carrier in manifest_sources(
        reader, control, root_candidates=root_candidates
    ):
        context = native_header_view(carrier.metadata).get("context")
        state = carrier.metadata.get("state")
        if (
            isinstance(context, dict)
            and context.get("template") == "project_manifest"
            and isinstance(state, dict)
            and state.get("status") == "active"
        ):
            yield path, carrier


def select_manifest_carriers(reader: ReadContext, root: Path, control: Path):
    """Select root candidates first, retaining the \
control-root compatibility path."""
    candidates = [
        path
        for path in _manifest_paths(reader, root)
        if "-PROJECT_MANIFEST--" in path.name
    ]
    if candidates:
        return active_manifest_carriers(reader, root, root_candidates=True)
    return active_manifest_carriers(reader, control)


def manifest_inputs(
    path: Path, carrier: ParsedCarrier
) -> tuple[dict[str, object], str]:
    header = native_header_view(carrier.metadata)
    context, state = header["context"], header["state"]
    container, identity = context.get("container"), header.get("identity")
    atom_id = identity.get("atom_id") if isinstance(identity, dict) else None
    version, tier = state.get("version"), context.get("tier")
    if (
        type(tier) is not int
        or tier != -1
        or type(version) is not int
        or version < 1
        or not isinstance(container, dict)
        or set(container) != {"component"}
        or not isinstance(container["component"], str)
        or not container["component"].strip()
        or not isinstance(atom_id, str)
        or re.fullmatch(r"[A-Z]+-S-[0-9]+", atom_id) is None
        or (
            "atom_family" not in carrier.metadata
            and not path.name.startswith(f"{atom_id}-")
        )
    ):
        raise ProjectSelectionError(
            "Invalid Active Project Manifest header or filename"
        )
    fields = _manifest_fields(carrier)
    return {
        "atom_id": atom_id,
        "ref_id": derive_atom_ref(atom_id, version, state["status"]),
        "version": version,
        "tier": tier,
        **fields,
    }, container["component"]


def _manifest_fields(carrier):
    source = formal_manifest(carrier.body)
    if source is None:
        fields = parse_manifest_declaration(
            formal_claim(carrier.body),
            entity_name="Project Manifest",
            class_name="ProjectManifest",
            wrapped=True,
        )
    else:
        if formal_claim(carrier.body, required=False) is not None:
            raise ProjectSelectionError("Ambiguous Project Manifest declarations")
        fields = parse_manifest_declaration(
            source,
            entity_name="Component Manifest",
            class_name="ComponentManifest",
            wrapped=False,
        )
    if (
        not {"name", "prefix"} <= fields.keys()
        or fields.keys() - {"name", "prefix", "parameters", "lens_whitelist"}
    ):
        raise ProjectSelectionError("Invalid Project Manifest fields")
    if isinstance(parameters := fields.get("parameters"), dict):
        _normalize_parameters(parameters)
    return fields


def _parameter_table(parameters, name):
    table = parameters.setdefault(name, {})
    if not isinstance(table, dict):
        raise ProjectSelectionError(f"Project Manifest {name} must be a mapping")
    return table


def _move_parameter(source, key, target, name):
    if name in target:
        raise ProjectSelectionError(f"Duplicate Project Manifest parameter: {key}")
    target[name] = source.pop(key)


def _normalize_parameters(parameters):
    # Keep one internal shape for existing runtimes and older Projects.
    for name in ("root", "folder_layout"):
        if name in parameters:
            _move_parameter(
                parameters, name, _parameter_table(parameters, "project"), name
            )
    runtime = parameters.get("runtime")
    mcp = parameters.get("project_mcp")
    if isinstance(runtime, dict):
        if "journal.storage" in runtime:
            _move_parameter(
                runtime, "journal.storage",
                _parameter_table(runtime, "journal"), "storage",
            )
        if "duck_db.storage" in runtime:
            workbench = "workbench" if (
                "workbench" in runtime and "iwe_console" not in runtime
            ) else "iwe_console"
            _move_parameter(
                runtime, "duck_db.storage",
                _parameter_table(runtime, workbench), "storage",
            )
    if isinstance(mcp, dict) and "inline_result_limit_kib" in mcp:
        runtime = _parameter_table(parameters, "runtime")
        workbench = "workbench" if (
            "workbench" in runtime and "iwe_console" not in runtime
        ) else "iwe_console"
        _move_parameter(
            mcp, "inline_result_limit_kib",
            _parameter_table(runtime, workbench), "inline_result_limit_kib",
        )


def manifest_state_fields(
    carrier: ParsedCarrier, *, include_header=False
) -> dict[str, object]:
    state = carrier.metadata["state"]
    updated_at = state.get("updated_at")
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    if not isinstance(updated_at, datetime):
        raise ValueError("Manifest State requires a datetime Updated At")
    fields = {"status": state["status"], "updated_at": updated_at}
    return (
        fields | native_header_model_fields(carrier.metadata)
        if include_header
        else fields
    )


def manifest_summary_fields(
    carrier: ParsedCarrier, *, use_title=False
) -> dict[str, object]:
    sections = parse_content(carrier.body, tolerate_duplicate_siblings=True)
    if use_title:
        titles = [
            section["heading"].strip()
            for section in sections
            if section["heading_level"] == 1
        ]
        if len(titles) != 1 or not titles[0]:
            raise ValueError("Component Seed Manifest requires one title")
        return {"summary": titles[0]}
    summaries = [
        section
        for section in sections
        if section["property_path"] == ["summary"]
    ]
    if len(summaries) > 1:
        raise ValueError("Manifest has duplicate Summary properties")
    value = summaries[0]["direct_markdown"] if summaries else None
    return {"summary": value.strip()} if value is not None else {}


def manifest_purpose(body: str) -> str | None:
    """Read the optional top-level Purpose from the Manifest carrier."""
    sections = parse_content(body, tolerate_duplicate_siblings=True)
    purposes = [
        section["section_markdown"].splitlines()[1:]
        for section in sections
        if section["heading_level"] == 2
        and section["property_path"] == ["purpose"]
    ]
    if len(purposes) > 1:
        raise ValueError("Manifest has duplicate Purpose properties")
    return ("\n".join(purposes[0]).strip() or None) if purposes else None
