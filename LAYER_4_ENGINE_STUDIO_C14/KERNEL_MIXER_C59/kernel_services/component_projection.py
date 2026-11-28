"""Project component manifests into the native query store."""

import json
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        ParsedCarrier,
        source_markdown,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.components.components__shared import (
        component_contract_fences,
        parse_component_manifest,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    settings.project.project__shared import (
        manifest_inputs,
        manifest_purpose,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.header.header__shared import (
        native_header_view,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    structure.structure__shared import (
        read_structure,
    )  # fmt: skip


def _component_manifest(row):
    if (
        row["status_group"] != "Current"
        or row["tier"] not in (0, 1, 4)
        or row["id"].split("-")[1] != "S"
    ):
        return None
    context = native_header_view(row["header_json"])["context"]
    if (
        context.get("template") != "component_manifest"
        or context.get("lens") != "SPEC"
    ):
        return None
    owner = context["container"].get("component")
    if owner is None:
        return None
    try:
        body = source_markdown(row)
        fields, purpose = parse_component_manifest(
            body, tier=row["tier"] or None
        )
        has_contract = (
            row["tier"] == 1 and component_contract_fences(body) is not None
        )
    except ValueError:
        return None
    values = _component_values(fields)
    if values is None:
        return None
    cid, name, layer, lenses = values
    boundaries = fields.get("boundaries")
    ref = row["_exact_ref"]
    return (
        cid,
        name,
        owner,
        layer,
        lenses,
        None if boundaries is None else json.dumps(boundaries),
        ref,
        row["source_path"],
        [ref] if purpose else [],
        has_contract,
        purpose,
    )


def _component_values(fields):
    cid = fields.get("component_id")
    name, layer, lenses = (
        fields.get("name"),
        fields.get("layer"),
        fields.get("lens_whitelist"),
    )
    if not (
        isinstance(cid, str)
        and re.fullmatch(r"C[0-9]+", cid)
        and isinstance(name, str)
        and name.strip()
        and (layer is None or type(layer) is int)
        and (
            lenses is None
            or isinstance(lenses, list)
            and all(isinstance(lens, str) for lens in lenses)
        )
    ):
        return None
    return cid, name, layer, lenses


def _root_manifest(rows, selection):
    if selection is None:
        return None
    path = selection.manifest_path.relative_to(selection.root).as_posix()
    row = next((row for row in rows if row["source_path"] == path), None)
    if row is None or row["_exact_ref"] != selection.manifest_ref:
        raise ValueError("Selected Project Manifest is missing from capture")
    body = source_markdown(row)
    if row.get("_source_sha256") != selection.manifest_sha256:
        raise ValueError(
            "Selected Project Manifest differs from its startup pin"
        )
    carrier = ParsedCarrier(
        text=body, frontmatter="", body=body, metadata=row["header_json"]
    )
    fields, owner = manifest_inputs(selection.manifest_path, carrier)
    ref = row["_exact_ref"]
    purpose = manifest_purpose(body)
    return (
        owner,
        selection.project_name,
        None,
        None,
        fields.get("lens_whitelist"),
        None,
        ref,
        path,
        [ref] if purpose else [],
        False,
        purpose,
    )


def _write_components(connection, rows, selection=None) -> None:
    manifests = [
        entry
        for row in rows
        if (entry := _component_manifest(row)) is not None
    ]
    root = _root_manifest(rows, selection)
    if root is not None:
        manifests.append(root)
    connection.execute(
        """CREATE OR REPLACE TABLE main.components (
            component_id VARCHAR, name VARCHAR, parent_component_id VARCHAR,
            layer BIGINT, lens_whitelist VARCHAR[], boundaries JSON,
            manifest_ref VARCHAR, manifest_path VARCHAR,
            purpose_refs VARCHAR[], has_contract BOOLEAN, purpose VARCHAR
        )"""
    )
    if manifests:
        connection.executemany(
            "INSERT INTO main.components "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            manifests,
        )


def _write_component_seeds(connection, selection) -> None:
    path = getattr(selection, "structure_snapshot", None)
    seeds = read_structure(path).packages if path is not None else {}
    connection.execute(
        """CREATE OR REPLACE TABLE main.component_seeds (
            seed_id VARCHAR, parent_component_id VARCHAR, manifest_ref VARCHAR,
            purpose VARCHAR, has_solution BOOLEAN
        )"""
    )
    if seeds:
        connection.executemany(
            "INSERT INTO main.component_seeds VALUES (?, ?, ?, ?, ?)",
            [
                (
                    key,
                    seed.component,
                    seed.ref,
                    seed.fields.get("purpose"),
                    seed.fields.get("solution") is not None,
                )
                for key, seed in seeds.items()
            ],
        )
