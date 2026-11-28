"""Bind native class names to selected Model Declaration targets."""

from collections import defaultdict
from collections.abc import Mapping
from ..model.formal_claim__pub import iter_formal_claims
from ..model.model_class_subject__pub import model_class_target
from ..carriers.content.carrier_compat__pub import (
    is_current_requirement_declaration,
)
from ..carriers.carriers__shared import (
    matches_named_value,
)


def class_bindings(selected_carriers):
    from ..model.claims.native_model_claim__pub import parse_native_model_claim

    declarations = defaultdict(list)
    for carrier in selected_carriers:
        view = carrier.get("read_view", {})
        if not matches_named_value(
            view.get("content_role"), "Requirement"
        ) or not matches_named_value(view.get("type"), "Declaration"):
            continue
        subjects = carrier.get("subjects")
        if not isinstance(subjects, Mapping):
            continue
        subject = subjects.get("governs")
        for code in iter_formal_claims(carrier.get("body", "")):
            declaration = parse_native_model_claim(code)
            if declaration is None or declaration["kind"] != "entity":
                continue
            name = declaration["arguments"].get("entity_class")
            target = model_class_target(
                subject, declaration["arguments"].get("entity_name")
            )
            if (
                target is not None
                and name is not None
                and any(row["name"] == name for row in declaration["classes"])
            ):
                declarations[name].append((target, dict(carrier["source"])))
    return dict(declarations)


def bindings_from_workbench_rows(rows):
    "Build a fresh catalog from exactly the selected Workbench source rows."
    import hashlib
    from ..carriers.content.carrier_compat__pub import carrier_read_view

    carriers = []
    for row in rows:
        if not is_current_requirement_declaration(row):
            continue
        metadata = row.get("header_json")
        body = row.get("_content_bytes")
        if not isinstance(metadata, dict) or not isinstance(body, bytes):
            continue
        view = carrier_read_view(metadata)
        atom_id, version = view.get("atom_id"), view.get("version")
        if not isinstance(atom_id, str) or type(version) is not int:
            continue
        source = {
            "atom_id": atom_id,
            "version": version,
            "path": row.get("source_path", ""),
            "sha256": hashlib.sha256(body).hexdigest(),
        }
        carriers.append(
            {
                "source": source,
                "subjects": view.get("subjects"),
                "metadata": metadata,
                "read_view": view,
                "body": body.decode("utf-8"),
                "raw_body": body.decode("utf-8"),
            }
        )
    catalog = class_bindings(carriers)
    return {
        name: {records[0][0]}
        for name, records in catalog.items()
        if len(records) == 1
    }
