"""Render model graph details and shared Projection metadata."""

import yaml
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    readable_entity_tree_data import Record, record, rows, text  # fmt: skip


def _sources(provenance: Record) -> list[str]:
    sources = set()
    for owner in rows(record(provenance).get("owners")):
        source = record(owner.get("source"))
        atom_id = text(source.get("atom_id"), "source Atom ID")
        version = source.get("version")
        if (
            isinstance(version, bool)
            or not isinstance(version, int)
            or version < 1
        ):
            raise ValueError("Invalid source Version")
        sources.add(f"{atom_id}@{version}")
    return sorted(sources)


def named_selection_reference(value: object) -> str:
    """Render the carrier value as the declared Named Selection reference."""
    selection = text(value, "Projection.Source.Named Selection")
    return (
        selection
        if selection.startswith("Named Selection//")
        else "Named Selection//" + selection
    )


def _projection_frontmatter(
    provenance: Record,
    updated_at: str,
    projection_identity: Record | None,
    *,
    form: str,
) -> Record:
    """Build the admitted Projection carrier fields for a rendered view."""
    identity = record(projection_identity)
    return {
        "artifact_form": "Projection",
        "projection_id": text(identity.get("projection_id"), "projection_id"),
        "form": text(form, "Projection.Form"),
        "source": {
            "named_selection": named_selection_reference(
                identity.get("named_selection")
            ),
            "atoms": _sources(provenance),
        },
        "updated_at": text(updated_at, "updated_at"),
    }


def _model_header(
    provenance: Record,
    updated_at: str,
    source_selection: str,
    projection_identity: Record | None,
) -> list[str]:
    frontmatter = yaml.safe_dump(
        _projection_frontmatter(
            provenance, updated_at, projection_identity, form="Map"
        ),
        allow_unicode=True,
        sort_keys=False,
    ).rstrip()
    return [
        "---",
        frontmatter,
        "---",
        "",
        "## Model graph",
        "",
        "Source selection: " + text(source_selection, "source selection"),
        "",
        "Display selection: direct Declaration targets, "
        "selected Subject expressions, "
        "Relations, Axes and constraint records. Literal values, Formats "
        "and cardinalities remain constraints, not graph Nodes.",
        "",
        "This is a derived Projection, not independent model authority.",
        "",
    ]


def _model_rows(
    title: str, rows_to_render: list[Record], formatter
) -> list[str]:
    lines = ["## " + title, ""]
    if not rows_to_render:
        return [*lines, "- None supplied.", ""]
    lines.extend("- " + formatter(row) for row in rows_to_render)
    lines.append("")
    return lines


def _occurrences(row: Record) -> str:
    values = row.get("occurrence_ids")
    return (
        "" if not values else " — " + ", ".join(str(value) for value in values)
    )


def _claim_diagnostic_text(row: Record) -> str:
    expression = row.get("expression")
    if isinstance(expression, str) and expression.strip():
        return expression
    return text(row.get("message"), "Claim diagnostic message")


def _append_primary_rows(body, model):
    body.extend(
        _model_rows(
            "Primary Nodes",
            rows(model.get("primary_nodes")),
            lambda row: (
                "`"
                + text(row.get("identity"), "node identity")
                + "`"
                + _occurrences(row)
            ),
        )
    )
    body.extend(
        _model_rows(
            "Properties",
            rows(model.get("properties")),
            lambda row: (
                "`"
                + text(row.get("identity"), "Property identity")
                + "`"
                + _occurrences(row)
            ),
        )
    )
    body.extend(
        _model_rows(
            "Instances",
            rows(model.get("instances")),
            lambda row: (
                "`"
                + text(row.get("identity"), "instance identity")
                + "`"
                + _occurrences(row)
            ),
        )
    )


def _relation_text(row: Record) -> str:
    if "identity" in row:
        return "`" + text(row.get("identity"), "Relation identity") + "`"
    return (
        "`"
        + text(row.get("kind"), "Relation")
        + "` `"
        + text(row.get("source"), "Relation source")
        + "` → `"
        + text(row.get("target"), "Relation target")
        + "`"
    )


def _classification_text(row: Record) -> str:
    return (
        "`"
        + text(row.get("source"), "axis subject")
        + "` >| `"
        + text(row.get("target"), "axis")
        + "`"
    )


def render_model(
    graph: Record,
    provenance: Record,
    *,
    updated_at: str,
    source_selection: str,
    projection_identity: Record | None = None,
) -> str:
    """Render the bounded enhanced graph view without executing Claim code."""

    graph = record(graph)
    model = record(graph.get("model"))
    body = _model_header(
        provenance, updated_at, source_selection, projection_identity
    )
    _append_primary_rows(body, model)

    body.extend(
        _model_rows(
            "Relations",
            rows(model.get("relations")),
            lambda row: _relation_text(row) + _occurrences(row),
        )
    )
    body.extend(
        _model_rows(
            "Axes",
            rows(model.get("axes")),
            lambda row: _classification_text(row) + _occurrences(row),
        )
    )
    _append_model_constraints(body, model, graph)
    return "\n".join(body)


def _append_model_literals(body, model):
    body.extend(
        _model_rows(
            "Allowed literals",
            rows(model.get("allowed_literals")),
            lambda row: (
                "`"
                + text(row.get("property"), "literal Property")
                + ": "
                + text(row.get("literal"), "literal value")
                + "`"
                + _occurrences(row)
            ),
        )
    )
    body.extend(
        _model_rows(
            "Selected Subject Expressions",
            rows(model.get("selected_subject_expressions")),
            lambda row: (
                "`"
                + text(row.get("expression"), "Subject expression")
                + "`"
                + " — "
                + text(
                    record(row.get("source")).get("atom_id"),
                    "Subject source Atom",
                )
            ),
        )
    )


def _append_model_constraints(body, model, graph):
    _append_model_literals(body, model)
    body.extend(
        _model_rows(
            "Constraints",
            rows(graph.get("constraints")),
            lambda row: (
                "`"
                + text(row.get("kind"), "constraint kind")
                + "`: `"
                + text(row.get("expression"), "constraint expression")
                + "`"
                + " — "
                + text(
                    record(row.get("source")).get("atom_id"),
                    "constraint source Atom",
                )
            ),
        )
    )
    body.extend(
        _model_rows(
            "Python Formal Claim diagnostics",
            rows(graph.get("claim_diagnostics")),
            lambda row: (
                "`"
                + text(row.get("code"), "Claim diagnostic code")
                + "`: `"
                + _claim_diagnostic_text(row)
                + "`"
                + (
                    " — "
                    + text(
                        record(row.get("source")).get("atom_id"),
                        "Claim source Atom",
                    )
                    if row.get("source")
                    else ""
                )
            ),
        )
    )
