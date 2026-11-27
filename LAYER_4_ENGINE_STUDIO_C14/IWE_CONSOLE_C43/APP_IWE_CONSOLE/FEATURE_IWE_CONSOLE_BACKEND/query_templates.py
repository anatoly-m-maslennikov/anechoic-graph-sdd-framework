"""Read-only native Atom queries with named, typed inputs."""

import re

from mcp import types

from .workbench_tools import _RUN_SCHEMA


QUERY_TEMPLATE = "query_template"
TEMPLATES = {
    "get_atom": ("reference",),
    "find_atoms": ("text",),
    "list_versions": ("reference",),
    "list_tickets": ("kind", "label", "parent", "statuses"),
    "list_atoms": ("family", "kind", "statuses"),
    "count_atoms": ("family", "kind", "statuses", "group_by"),
    "get_atom_state": ("reference",),
    "list_relations": ("reference", "direction"),
    "count_relations_by_type": (),
    "fetch_contracts": ("component",),
    "fetch_solutions": ("component",),
    "get_component_manifest": ("component",),
    "get_component_purpose": ("component",),
}
_ATOM_ID = r"[A-Z]+-[STPC]-[0-9]+"
_VERSION = r"@[1-9][0-9]*(?:-draft)?"
_STATUSES = [
    "active",
    "in_queue",
    "ready",
    "backlog",
    "draft",
    "done",
    "complete",
    "canceled",
    "resolved",
    "archived",
]
_FAMILIES = {"spec": "S", "tkt": "T", "project_config": "PC", "pmeta": "P"}
_INVENTORIES = {"list_atoms", "count_atoms", "list_tickets"}
_COMPONENT_QUERIES = {
    "fetch_contracts",
    "fetch_solutions",
    "get_component_manifest",
    "get_component_purpose",
}
_RESULT_OPTIONS = ("page_size", "result_delivery", "result_format")
_TEXT = {
    "type": "string",
    "minLength": 1,
    "maxLength": 1000,
    "pattern": r"^[^\x00]+$",
}
_ATOMS = "atoms AS a JOIN native_references AS r USING (reference)"
_SUMMARY = 'a."content.summary" AS summary'
_PATH = "concat_ws('/', nullif(a.relative_path, ''), a.filename) AS path"
_STATUS = 'a."header.state.status"'
_TEMPLATE = 'a."header.context.template"'
_LABEL = "json_extract_string(to_json(a), '$.\"header.context.label\"')"
_NORMALIZED_LABEL = f"lower(replace(replace({_LABEL}, '-', ''), ' ', ''))"
_UPDATED = 'a."header.state.updated_at"'
_NUMBER = 'a."header.state.version"'
_GROUPS = {
    "status": _STATUS,
    "status_group": "a.status_group",
    "kind": _TEMPLATE,
}
_COLUMNS = {
    "get_atom": f"r.exact_ref, {_SUMMARY}, {_STATUS} AS status, {_PATH}",
    "find_atoms": f"a.reference AS ref, {_SUMMARY}, {_PATH}",
    "list_versions": f"r.exact_ref, {_STATUS} AS status, {_UPDATED} AS updated_at, {_PATH}",
    "list_tickets": f"a.reference AS ref, {_SUMMARY}, {_TEMPLATE} AS kind, {_STATUS} AS status, {_PATH}, {_LABEL} AS label",
    "list_atoms": f"a.reference AS ref, {_SUMMARY}, {_TEMPLATE} AS kind, {_STATUS} AS status, {_PATH}",
    "count_atoms": "count(*) AS count",
    "get_atom_state": f"{_STATUS} AS status, {_NUMBER} AS version",
}


def descriptor():
    return types.Tool(
        name=QUERY_TEMPLATE,
        description=(
            "Run a named native Atom query through query_run. Small results default to inline CSV. "
            "get_atom and get_atom_state "
            "take a stable or exact reference. find_atoms searches Current summaries, IDs and paths "
            "using literal text. list_versions takes a stable reference. list_atoms and count_atoms "
            "filter by family, kind or statuses. count_atoms includes archived Atoms unless filtered "
            "and can group by status, status_group or kind. "
            "list_tickets lists Tasks and Epics with optional "
            "parent, kind, label and statuses. list_relations takes a reference and defaults to outgoing. "
            "count_relations_by_type groups relation counts by type and derived flag. "
            "fetch_contracts returns the Component Manifest when it has an embedded Contract; fetch_solutions returns Active Tier 0 Solution Atoms owned by the Component. "
            "Both accept a Component name or ID in component, as do get_component_manifest and get_component_purpose."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "template": {"type": "string", "enum": list(TEMPLATES)},
                "reference": {
                    "type": "string",
                    "pattern": f"^{_ATOM_ID}(?:{_VERSION})?$",
                },
                "text": _TEXT,
                "kind": {"type": "string", "pattern": r"^[a-z][a-z0-9_]*$"},
                "label": _TEXT,
                "family": {"type": "string", "enum": list(_FAMILIES)},
                "group_by": {"type": "string", "enum": list(_GROUPS)},
                "parent": {"type": "string", "pattern": r"^[A-Z]+-T-[0-9]+$"},
                "statuses": {"type": "array", "minItems": 1, "uniqueItems": True,
                             "items": {"type": "string", "enum": _STATUSES}},
                "direction": {"type": "string", "enum": ["outgoing", "incoming"]},
                "component": _TEXT | {"description": "Component name or ID, such as Kernel Mixer or C59."},
                **{key: _RUN_SCHEMA["properties"][key] for key in _RESULT_OPTIONS},
                "result_format": {**_RUN_SCHEMA["properties"]["result_format"], "default": "csv"},
            },
            "required": ["template"],
            "additionalProperties": False,
        },
        annotations=types.ToolAnnotations(
            read_only_hint=True, open_world_hint=False
        ),
    )


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _kind_filter(template, kind):
    if template == "list_tickets" and kind == "epic":
        return (f"({_TEMPLATE} = 'epic' OR ({_TEMPLATE} = 'task' AND "
                f"{_NORMALIZED_LABEL} IN ('epic', 'subepic')))")
    return f"{_TEMPLATE} = {_literal(kind)}"


def _inventory(template, arguments, columns):
    group = order = ""
    filters = []
    if template == "list_tickets":
        filters += [
            "split_part(r.exact_ref, '-', 2) = 'T'",
            f"{_TEMPLATE} IN ('task', 'epic')",
        ]
    if "family" in arguments:
        markers = ", ".join(map(_literal, _FAMILIES[arguments["family"]]))
        filters.append(f"split_part(r.exact_ref, '-', 2) IN ({markers})")
    if "kind" in arguments:
        filters.append(_kind_filter(template, arguments["kind"]))
    if "label" in arguments:
        label = arguments["label"].lower().replace("-", "").replace(" ", "")
        filters.append(f"{_NORMALIZED_LABEL} = {_literal(label)}")
    if "parent" in arguments:
        filters.append(
            "EXISTS (SELECT 1 FROM relations AS edge "
            "WHERE edge.source_kind = 'Atom' AND edge.source_ref = a.reference "
            "AND edge.target_kind = 'Atom' AND edge.relation_type IN ('IS_CONTAINED_BY', 'CONTAINED_BY') "
            f"AND NOT edge.derived AND edge.target_ref = {_literal(arguments['parent'])})"
        )
    if "statuses" in arguments:
        statuses = ", ".join(map(_literal, arguments["statuses"]))
        filters.append(f"{_STATUS} IN ({statuses})")
    elif template != "count_atoms":
        filters.append("a.status_group <> 'Archived'")
    where = " AND ".join(filters)
    if template != "count_atoms":
        order = f"{_UPDATED} DESC, ref"
    elif "group_by" in arguments:
        order = arguments["group_by"]
        group = _GROUPS[order]
        columns = f"{group} AS {order}, {columns}"
    return columns, where, group, order


def _component(template, arguments):
    label = arguments["component"].strip()
    if not label:
        raise ValueError("A Component name or ID is required")
    cid = (
        _literal(label.upper())
        if re.fullmatch(r"[Cc][0-9]+", label)
        else f"(SELECT component_id FROM components WHERE lower(name) = lower({_literal(label)}))"
    )
    columns = f"r.exact_ref, {_SUMMARY}, {_PATH}"
    order = "r.exact_ref"
    if template == "get_component_manifest":
        where = f"r.exact_ref = (SELECT manifest_ref FROM components WHERE component_id = {cid})"
    elif template == "get_component_purpose":
        where = f"r.exact_ref IN (SELECT unnest(purpose_refs) FROM components WHERE component_id = {cid})"
    elif template == "fetch_contracts":
        where = (
            f"{_STATUS} = 'active' AND r.exact_ref = "
            f"(SELECT manifest_ref FROM components WHERE component_id = {cid} AND has_contract)"
        )
    else:
        tier = (
            "coalesce(json_extract_string(to_json(a), '$.\"header.tier\"'), "
            "json_extract_string(to_json(a), '$.\"header.structure.tier\"'), "
            "json_extract_string(to_json(a), '$.\"header.context.tier\"'))"
        )
        where = (
            "a.status_group = 'Current' AND split_part(a.reference, '-', 2) = 'S' "
            f"AND {_STATUS} = 'active' AND {tier} = '0' AND lower({_TEMPLATE}) = 'solution' "
            "AND EXISTS (SELECT 1 FROM relations AS edge WHERE edge.source_ref = a.reference "
            "AND edge.source_kind = 'Atom' AND edge.target_kind = 'Component' "
            f"AND edge.relation_type IN ('IS_CONTAINED_BY', 'CONTAINED_BY') AND NOT edge.derived AND edge.target_ref = {cid})"
        )
    return columns, where, order


def _query_parts(template, arguments):
    table = _ATOMS
    columns = _COLUMNS.get(template)
    group = ""
    order = ""
    if template in {"get_atom", "get_atom_state"}:
        reference = arguments["reference"]
        column = "exact_ref" if "@" in reference else "stable_ref"
        where = f"r.{column} = {_literal(reference)}"
        order = "r.exact_ref"
    elif template == "list_versions":
        reference = arguments["reference"]
        if "@" in reference:
            raise ValueError("list_versions requires a stable Atom ID")
        where = f"split_part(r.exact_ref, '@', 1) = {_literal(reference)}"
        order = f"{_NUMBER} DESC, r.exact_ref"
    elif template == "find_atoms":
        text = _literal(arguments["text"])
        where = (f"a.status_group = 'Current' AND (contains(lower(summary), lower({text})) "
                 f"OR contains(lower(ref), lower({text})) OR contains(lower(path), lower({text})))")
        order = "ref"
    elif template in _INVENTORIES:
        columns, where, group, order = _inventory(template, arguments, columns)
    elif template == "list_relations":
        side, other = (
            ("target", "source")
            if arguments.get("direction") == "incoming"
            else ("source", "target")
        )
        table = "relations"
        columns = f"relation_type, {other}_ref AS related_ref, derived"
        reference = _literal(arguments["reference"])
        where = (
            f"{side}_kind = 'Atom' AND ({side}_ref = {reference} OR {side}_ref IN "
            f"(SELECT reference FROM native_references WHERE exact_ref = {reference}))"
        )
        order = "relation_type, related_ref, derived"
    elif template == "count_relations_by_type":
        table = "relations"
        columns = "relation_type, derived, count(*) AS count"
        where = ""
        group = order = "relation_type, derived"
    elif template in _COMPONENT_QUERIES:
        columns, where, order = _component(template, arguments)
    return table, columns, where, group, order


def run_arguments(arguments: dict) -> dict:
    """Build a normal Workbench query from registry-validated template arguments."""
    template = arguments["template"]
    fields = set(arguments) - {"template", *_RESULT_OPTIONS}
    allowed = set(TEMPLATES[template])
    required = (
        allowed - {"direction"} if template not in _INVENTORIES else set()
    )
    if fields - allowed or required - fields:
        raise ValueError(
            f"Invalid arguments for {template}. Supported fields: {', '.join(TEMPLATES[template])}"
        )

    table, columns, where, group, order = _query_parts(template, arguments)
    sql = f"SELECT {columns} FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if group:
        sql += f" GROUP BY {group}"
    if order:
        sql += f" ORDER BY {order}"
    options = {
        key: arguments[key] for key in _RESULT_OPTIONS if key in arguments
    }
    options.setdefault("result_format", "csv")
    return {"sql": sql, **options}
