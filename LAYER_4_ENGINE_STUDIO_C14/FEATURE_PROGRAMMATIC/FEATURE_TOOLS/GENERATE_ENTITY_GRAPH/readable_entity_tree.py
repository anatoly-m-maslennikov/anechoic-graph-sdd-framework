("Render the existing typed Subject graph "
 "without admitting new model facts.")  # fmt: skip

import re
from collections import Counter

import yaml
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    readable_entity_tree_data import (
    Children,
    Nodes,
    Record,
    name_key,
    primary_tree,
    read_edges,
    read_nodes,
    record,
    rows,
    text,
    tree,
)  # fmt: skip


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    readable_model_view import (
    _sources as _sources,
    named_selection_reference as named_selection_reference,
    _projection_frontmatter as _projection_frontmatter,
    _model_header as _model_header,
    _model_rows as _model_rows,
    _occurrences as _occurrences,
    _claim_diagnostic_text as _claim_diagnostic_text,
    _append_model_constraints as _append_model_constraints,
    render_model as render_model,
)  # fmt: skip


def _fence(lines: list[str]) -> list[str]:
    width = max(
        [3]
        + [
            len(match[0]) + 1
            for line in lines
            for match in re.finditer(r"`+", line)
        ]
    )
    marker = "`" * width
    return [marker + "text", *lines, marker]


def _header(
    provenance: Record,
    updated_at: str,
    source_selection: str,
    projection_identity: Record | None = None,
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
        "## Inherency tree",
        "",
        "Source selection: " + text(source_selection, "source selection"),
        "",
        "Display selection: supplied graph nodes and Inherency relations; "
        "dependent entities appear in detail sections.",
        "",
        "Notation: / NARROWER_THAN; // INSTANCE_OF; . IS_PROPERTY_OF; "
        ": IS_ALLOWED_VALUE_OF; <+ CONTAINS (derived reverse of "
        "IS_CONTAINED_BY); >| HAS_AXIS. Relations are traversed "
        "from broader to narrower, "
        "kind to named instance (the source INSTANCE_OF direction "
        "is instance to kind), "
        "bearer to dependent, Entity to allowed value, whole to part, "
        "and Entity to Axis value.",
        "",
        "This is a derived Projection, not independent model authority.",
        "",
        "### Primary entities",
        "",
    ]


def _details(
    appearances: list[str],
    nodes: Nodes,
    children: Children,
    dependents: set[str],
) -> tuple[list[str], set[str], set[str]]:
    body: list[str] = []
    shown: set[str] = set(appearances)
    cycles: set[str] = set()
    for primary in appearances:
        if any(
            edge["kind"] in {"IS_PROPERTY_OF", "IS_BORNE_BY"}
            for _, edge in children[primary]
        ):
            lines, visited, found_cycles = tree(
                primary, dependents, nodes, children
            )
            body.extend(
                ["### " + nodes[primary]["identity"], "", *_fence(lines), ""]
            )
            shown.update(visited)
            cycles.update(found_cycles)
    return body, shown, cycles


def _detail_limitations(nodes, omitted, orphaned, cycles):
    notes = []
    if omitted:
        notes.append(
            "Incomplete relation view: omitted unsupported "
            "or unclassified edges: "
            + ", ".join(
                f"{kind} ({count})" for kind, count in sorted(omitted.items())
            )
            + ". Their nodes remain visible without inventing "
            "a relation classification."
        )
    if orphaned:
        notes.append(
            "Incomplete dependent view: components have no displayed "
            "primary bearer: "
            + "; ".join(
                nodes[key]["identity"]
                for key in sorted(
                    orphaned, key=lambda key: name_key(nodes, key)
                )
            )
            + "."
        )
    if cycles:
        notes.append(
            "Cycles are marked [cycle] at the repeated placement "
            "and are not expanded further."
        )
    notes.append(
        "No inherited facts were synthesized; unavailable source "
        "facts remain unavailable."
    )
    return notes


def _limitations(
    graph: Record,
    nodes: Nodes,
    omitted: Counter[str],
    provisional: bool,
    orphaned: set[str],
    cycles: set[str],
) -> list[str]:
    notes = []
    if (
        "native_admission" in graph
        and graph["native_admission"] != "performed"
    ):
        notes.append(
            "Native admission: "
            + str(graph.get("native_admission", "not evidenced by input"))
            + "."
        )
    if provisional:
        notes.append(
            "The input includes provisional notation; "
            "this rendering does not establish admitted model facts."
        )
    notes.extend(_detail_limitations(nodes, omitted, orphaned, cycles))
    notes.extend(str(item) for item in graph.get("diagnostics", []))
    return ["Source limitations:", "", *("- " + note for note in notes), ""]


def render_inherency(
    graph: Record,
    provenance: Record,
    *,
    updated_at: str,
    source_selection: str,
    projection_identity: Record | None = None,
) -> str:
    ("Return deterministic Markdown; "
     "only the supplied rebuild time may vary.")  # fmt: skip
    graph = record(graph)
    nodes = read_nodes(rows(graph.get("nodes")))
    children, dependents, omitted, provisional = read_edges(
        rows(graph.get("edges")), nodes
    )
    main, appearances, cycles = primary_tree(
        nodes, children, set(nodes) - dependents
    )
    details, shown, detail_cycles = _details(
        appearances, nodes, children, dependents
    )
    body = _header(
        provenance, updated_at, source_selection, projection_identity
    )
    body.extend([*_fence(main), "", *details])
    body.extend(
        _limitations(
            graph,
            nodes,
            omitted,
            provisional,
            dependents - shown,
            cycles | detail_cycles,
        )
    )
    return "\n".join(body)
