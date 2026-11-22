"""Compose a syntax graph from supplied current Atom Subjects, without history."""



from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import subject_notation__pub as notation
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import carrier_read_view

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_common import (
    Record, _identifier, _is_declaration, subject_facts,
)

def _occurrences(carrier: Record, diagnostics: list[str]) -> list[Record]:
    source, subjects = carrier["source"], carrier["subjects"]
    if not isinstance(subjects, dict):
        diagnostics.append(f"{source['path']}: Subjects mapping is unavailable.")
        return []
    try:
        subjects = carrier_read_view({"subjects": subjects})["subjects"]
    except ValueError as error:
        raise ValueError(f"{source['path']}: {error}") from error
    result = []
    for role in ("governs", "depends_on"):
        value = subjects.get(role, [])
        values = value if isinstance(value, list) else [value]
        for index, subject in enumerate(values):
            locator = f"{source['path']}#subjects.{role}[{index}]"
            if not isinstance(subject, str) or not subject:
                diagnostics.append(f"{locator}: Subject is not nonempty text; no identity guessed.")
                continue
            result.append({"id": locator, "subject": subject, "source": source, "role": role})
    return result


def _add_path(
    occurrence: Record, nodes: dict[str, Record], edges: dict[str, Record], diagnostics: list[str],
    *, native_class_narrowing: bool = False,
) -> None:
    subject, origin = occurrence["subject"], occurrence["id"]
    try:
        supplied_nodes, facts, target = subject_facts(subject, native_class_narrowing=native_class_narrowing)
    except (notation.SubjectNotationError, ValueError) as error:
        raise ValueError(f"{origin}: Subject projection failed: {error}") from error
    for supplied in supplied_nodes:
        identity = supplied["identity"]
        child_id = _identifier("subject:", identity)
        node = nodes.setdefault(child_id, {
            **supplied, "id": child_id, "occurrence_ids": set(), "is_full_target": False,
        })
        for key, value in supplied.items():
            if key in node and node[key] != value:
                raise ValueError(f"{origin}: conflicting Subject projection metadata for {identity}: {key}")
            node[key] = value
        node["occurrence_ids"].add(origin)
        node["is_full_target"] |= identity == target
    for supplied in facts:
        source_id = _identifier("subject:", supplied["source"])
        target_id = _identifier("subject:", supplied["target"])
        metadata = {key: value for key, value in supplied.items() if key not in {"source", "target"}}
        edge_id = _identifier("subject-edge:", [metadata, source_id, target_id])
        edge = edges.setdefault(edge_id, {
            **metadata, "id": edge_id, "relation_source": source_id,
            "relation_target": target_id, "occurrence_ids": set(),
        })
        edge["occurrence_ids"].add(origin)


def _native_subjects(carriers):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import extract_claim_constraints
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import model_class_target
    native_subjects = set()
    for carrier in carriers:
        if not _is_declaration(carrier):
            continue
        constraints, _ = extract_claim_constraints(carrier)
        for clause in constraints:
            if clause.get("kind") != "native_class":
                continue
            subjects = carrier.get("subjects") or {}
            subject = carrier_read_view({"subjects": subjects})["subjects"].get("governs")
            if isinstance(subject, str) and model_class_target(subject, clause.get("entity_name")):
                native_subjects.add((carrier["source"]["path"], subject))
    return native_subjects


def compose_current_graph(
    carriers: list[Record], *, unsupported_as_diagnostics: bool = False,
) -> tuple[Record, Record]:
    """Use only the passed current sources; Subject roles add no cross-path edges."""
    nodes: dict[str, Record] = {}
    edges: dict[str, Record] = {}
    diagnostics: list[str] = []
    native_subjects = _native_subjects(carriers)
    occurrences = [row for carrier in carriers for row in _occurrences(carrier, diagnostics)]
    for occurrence in occurrences:
        try:
            _add_path(occurrence, nodes, edges, diagnostics,
                      native_class_narrowing=(occurrence["role"] == "governs" and
                                              (occurrence["source"]["path"], occurrence["subject"]) in native_subjects))
        except ValueError as error:
            if not unsupported_as_diagnostics:
                raise
            diagnostics.append(str(error))
    for row in [*nodes.values(), *edges.values()]:
        row["occurrence_ids"] = sorted(row["occurrence_ids"])
    graph = {
        "kind": "current_atom_subjects",
        "source_basis": "current_atom_carriers",
        "native_admission": "not_performed",
        "nodes": sorted(nodes.values(), key=lambda row: (row["identity"], row["id"])),
        "edges": sorted(edges.values(), key=lambda row: row["id"]),
        "diagnostics": sorted(diagnostics),
    }
    provenance = {
        "owners": [{"source": carrier["source"]} for carrier in carriers],
        "occurrences": occurrences,
    }
    return graph, provenance


