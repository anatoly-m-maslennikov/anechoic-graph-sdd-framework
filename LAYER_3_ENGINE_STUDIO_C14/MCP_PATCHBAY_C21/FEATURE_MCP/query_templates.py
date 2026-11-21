"""Read-only native Atom queries with named, typed inputs."""

import re

from mcp import types

from workbench_tools import _RUN_SCHEMA


QUERY_TEMPLATE = "query_template"
TEMPLATES = {
    "get_atom": ("reference",),
    "find_atoms": ("text",),
    "list_versions": ("reference",),
    "list_tickets": ("kind", "parent", "statuses"),
    "list_atoms": ("family", "kind", "statuses"),
    "count_atoms": ("family", "kind", "statuses", "group_by"),
    "get_atom_state": ("reference",),
    "list_relations": ("reference", "direction"),
    "count_relations_by_type": (),
    "resolve_legacy_ref": ("legacy_ref",),
    "resolve_legacy_path": ("original_path",),
    "fetch_contracts": ("component",),
    "fetch_solutions": ("component",),
    "get_component_manifest": ("component",),
    "get_component_purpose": ("component",),
}
_ATOM_ID = r"[A-Z]+-[STP]-[0-9]+"
_VERSION = r"@[1-9][0-9]*(?:-draft)?"
_STATUSES = ["active", "backlog", "draft", "done", "canceled", "resolved", "archived"]
_FAMILIES = {"spec": "S", "tkt": "T", "pmeta": "P"}
_INVENTORIES = {"list_atoms", "count_atoms", "list_tickets"}
_COMPONENT_QUERIES = {"fetch_contracts", "fetch_solutions", "get_component_manifest", "get_component_purpose"}
_RESULT_OPTIONS = ("page_size", "result_delivery", "result_format")
_TEXT = {"type": "string", "minLength": 1, "maxLength": 1000, "pattern": r"^[^\x00]+$"}
_ATOMS = "atoms AS a JOIN native_references AS r USING (reference)"
_SUMMARY = 'a."content.summary" AS summary'
_PATH = "concat_ws('/', nullif(a.relative_path, ''), a.filename) AS path"
_STATUS = 'a."header.state.status"'
_TEMPLATE = 'a."header.context.template"'
_UPDATED = 'a."header.state.updated_at"'
_NUMBER = 'a."header.state.version"'
_GROUPS = {"status": _STATUS, "status_group": "a.status_group", "kind": _TEMPLATE}
_COLUMNS = {
    "get_atom": f"r.exact_ref, {_SUMMARY}, {_STATUS} AS status, {_PATH}",
    "find_atoms": f"a.reference AS ref, {_SUMMARY}, {_PATH}",
    "list_versions": f"r.exact_ref, {_STATUS} AS status, {_UPDATED} AS updated_at, {_PATH}",
    "list_tickets": f"a.reference AS ref, {_SUMMARY}, {_TEMPLATE} AS kind, {_STATUS} AS status, {_PATH}",
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
            "parent, kind and statuses. list_relations takes a reference and defaults to outgoing. "
            "count_relations_by_type groups relation counts by type and derived flag. "
            "resolve_legacy_ref takes a legacy_ref, and resolve_legacy_path takes an original_path. "
            "fetch_contracts (Tier 0), fetch_solutions (Tier 1), get_component_manifest, and "
            "get_component_purpose accept a Component name or ID in component."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "template": {"type": "string", "enum": list(TEMPLATES)},
                "reference": {"type": "string", "pattern": f"^{_ATOM_ID}(?:{_VERSION})?$"},
                "text": _TEXT,
                "kind": {"type": "string", "pattern": r"^[a-z][a-z0-9_]*$"},
                "family": {"type": "string", "enum": list(_FAMILIES)},
                "group_by": {"type": "string", "enum": list(_GROUPS)},
                "parent": {"type": "string", "pattern": r"^[A-Z]+-T-[0-9]+$"},
                "statuses": {"type": "array", "minItems": 1, "uniqueItems": True,
                             "items": {"type": "string", "enum": _STATUSES}},
                "direction": {"type": "string", "enum": ["outgoing", "incoming"]},
                "legacy_ref": {"type": "string", "pattern": rf"^[A-Z]+-[A-Z]-[0-9]+(?:{_VERSION})?$"},
                "original_path": _TEXT,
                "component": _TEXT | {"description": "Component name or ID, such as Kernel Mixer or C59."},
                **{key: _RUN_SCHEMA["properties"][key] for key in _RESULT_OPTIONS},
                "result_format": {**_RUN_SCHEMA["properties"]["result_format"], "default": "csv"},
            },
            "required": ["template"],
            "additionalProperties": False,
        },
        annotations=types.ToolAnnotations(read_only_hint=True, open_world_hint=False),
    )


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def run_arguments(arguments: dict) -> dict:
    """Build a normal Workbench query from registry-validated template arguments."""
    template = arguments["template"]
    fields = set(arguments) - {"template", *_RESULT_OPTIONS}
    allowed = set(TEMPLATES[template])
    required = allowed - {"direction"} if template not in _INVENTORIES else set()
    if fields - allowed or required - fields:
        raise ValueError(f"Invalid arguments for {template}. Supported fields: {', '.join(TEMPLATES[template])}")

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
        filters = []
        if template == "list_tickets":
            filters += ["split_part(r.exact_ref, '-', 2) = 'T'", f"{_TEMPLATE} IN ('task', 'epic')"]
        if "family" in arguments:
            filters.append(f"split_part(r.exact_ref, '-', 2) = '{_FAMILIES[arguments['family']]}'")
        if "kind" in arguments:
            filters.append(f"{_TEMPLATE} = {_literal(arguments['kind'])}")
        if "parent" in arguments:
            filters.append(
                "EXISTS (SELECT 1 FROM relations AS edge "
                "WHERE edge.source_kind = 'Atom' AND edge.source_ref = a.reference "
                "AND edge.target_kind = 'Atom' AND edge.relation_type = 'CONTAINED_BY' "
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
    elif template == "list_relations":
        side, other = ("target", "source") if arguments.get("direction") == "incoming" else ("source", "target")
        table = "relations"
        columns = f"relation_type, {other}_ref AS related_ref, derived"
        reference = _literal(arguments["reference"])
        # Current edges use the stable reference. Resolve exact Current references the same way as archived ones.
        where = (f"{side}_kind = 'Atom' AND ({side}_ref = {reference} OR {side}_ref IN "
                 f"(SELECT reference FROM native_references WHERE exact_ref = {reference}))")
        order = "relation_type, related_ref, derived"
    elif template == "count_relations_by_type":
        table = "relations"
        columns = "relation_type, derived, count(*) AS count"
        where = ""
        group = order = "relation_type, derived"
    elif template == "resolve_legacy_ref":
        table = "native_legacy_references"
        columns = "exact_ref, original_path"
        reference = arguments["legacy_ref"]
        column = "legacy_ref" if "@" in reference else "split_part(legacy_ref, '@', 1)"
        where = f"{column} = {_literal(reference)}"
        order = "exact_ref, original_path"
    elif template in _COMPONENT_QUERIES:
        label = arguments["component"].strip()
        if not label:
            raise ValueError("A Component name or ID is required")
        cid = (_literal(label.upper()) if re.fullmatch(r"[Cc][0-9]+", label)
               else f"(SELECT component_id FROM components WHERE lower(name) = lower({_literal(label)}))")
        columns = f"r.exact_ref, {_SUMMARY}, {_PATH}"
        order = "r.exact_ref"
        if template == "get_component_manifest":
            where = f"r.exact_ref = (SELECT manifest_ref FROM components WHERE component_id = {cid})"
        elif template == "get_component_purpose":
            where = f"r.exact_ref IN (SELECT unnest(purpose_refs) FROM components WHERE component_id = {cid})"
        else:
            tier = 0 if template == "fetch_contracts" else 1
            where = ("a.status_group = 'Current' AND split_part(a.reference, '-', 2) = 'S' "
                     "AND coalesce(json_extract_string(to_json(a), '$.\"header.structure.tier\"'), "
                     f"json_extract_string(to_json(a), '$.\"header.context.tier\"')) = '{tier}' "
                     "AND EXISTS (SELECT 1 FROM relations AS edge WHERE edge.source_ref = a.reference "
                     "AND edge.source_kind = 'Atom' AND edge.target_kind = 'Component' "
                     f"AND edge.relation_type = 'CONTAINED_BY' AND NOT edge.derived AND edge.target_ref = {cid})")
    else:
        table = "native_migration_paths"
        columns = "exact_ref"
        where = f"original_path = {_literal(arguments['original_path'])}"

    sql = f"SELECT {columns} FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if group:
        sql += f" GROUP BY {group}"
    if order:
        sql += f" ORDER BY {order}"
    options = {key: arguments[key] for key in _RESULT_OPTIONS if key in arguments}
    options.setdefault("result_format", "csv")
    return {"sql": sql, **options}
