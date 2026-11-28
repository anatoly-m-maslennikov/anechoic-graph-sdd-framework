"""Declaration-view test fixture."""

from __future__ import annotations

from importlib import import_module

render_declarations = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
).render_declarations


FENCE = chr(96) * 3
PROJECTION = {
    "projection_id": "CA-PROJ-901",
    "named_selection": "Relation-Types-and-Graph-Rules",
    "source_of_truth": [
        "CORE_META_MODEL selected authority",
        "current active source set",
    ],
}


def source(atom_id: str, version: int) -> dict[str, object]:
    return {"atom_id": atom_id, "version": version}


def metadata(**overrides: object) -> dict[str, object]:
    values = {
        "meaning": "a supplied relation meaning",
        "direction": "source to target",
        "inverse": "target to source",
        "authority_effect": "direct",
        "transitivity": "not transitive",
        "applicability": "selected graph",
        "status": "Active",
        "exclusive_purpose": "one purpose",
    }
    values.update(overrides)
    return values


def relation_type(
    graph_kind: str,
    canonical_name: str,
    *,
    relation_metadata: dict[str, object] | None = None,
    sources: list[dict[str, object]] | None = None,
    evidence: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    row: dict[str, object] = {
        "graph_kind": graph_kind,
        "canonical_name": canonical_name,
        "metadata": relation_metadata
        if relation_metadata is not None
        else metadata(),
        "sources": sources if sources is not None else [source("CA-R-100", 2)],
    }
    if evidence is not None:
        row["evidence"] = evidence
    return row


def render(
    catalog: dict[str, object],
    *,
    owners: list[dict[str, object]] | None = None,
    projection_identity: dict[str, object] | None = None,
) -> str:
    return render_declarations(
        catalog,
        {
            "owners": owners
            if owners is not None
            else [{"source": source("CA-R-100", 2)}]
        },
        updated_at="2026-10-20 02:30:00 +0400",
        source_selection="CORE_META_MODEL only",
        projection_identity=projection_identity or PROJECTION,
    )


def raw_yaml_block():
    return (
        FENCE
        + "yaml\n"
        + "graph_rule_type: whitelist\n"
        + "applies_to:\n"
        + "  relation_type: IS_CONTAINED_BY\n"
        + "condition:\n"
        + "  source: [Child]\n"
        + "  target: [Parent]\n"
        + FENCE
    )


def good_view_document():
    raw_yaml = raw_yaml_block()
    document = render(
        {
            "relation_types": [
                relation_type(
                    "Entities Graph",
                    "IS_CONTAINED_BY",
                    evidence=[
                        {
                            "source": source("CA-R-1368", 14),
                            "subject": "Entity/Plan",
                            ("body"): (
                                "The source Claim establishes the direct "
                                "containment direction."
                            ),
                        }
                    ],
                )
            ],
            "graph_rules": [
                {
                    "source": source("CA-R-200", 4),
                    "subject": "Entity/Plan",
                    "summary": "Plan containment rule.",
                    "yaml_block": raw_yaml,
                }
            ],
            "limitations": ["Project selection is not included."],
            "unresolved": [],
        },
        owners=[
            {"source": source("CA-R-200", 4)},
            {"source": source("CA-R-100", 2)},
            {"source": source("CA-R-100", 2)},
        ],
    )
    return document, raw_yaml


def assert_invalid_provenance(self):
    with self.assertRaisesRegex(ValueError, "Invalid source Version"):
        render(
            {
                "relation_types": [],
                "graph_rules": [],
                "limitations": [],
                "unresolved": [],
            },
            owners=[{"source": {"atom_id": "CA-R-100", "version": 0}}],
        )
