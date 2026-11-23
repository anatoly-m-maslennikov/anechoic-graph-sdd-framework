"""Validate and present the Kernel's atomic public schema."""

import httpx2

from .peer_transport import tool_failure, upstream
from .projection_tools import FLOW_HISTORY, TABLE_ALIASES, TABLES


def _valid_schema(value):
    if not isinstance(value, dict) or set(value) != {"tables"} or not isinstance(value["tables"], dict):
        return False
    for table, columns in value["tables"].items():
        if table not in (*TABLES, *FLOW_HISTORY, "work_journal", "query_log", *TABLE_ALIASES) or not isinstance(columns, list):
            return False
        names = set()
        for column in columns:
            if not isinstance(column, dict) or set(column) not in ({"name", "type"}, {"name", "type", "values"}):
                return False
            name, kind = column["name"], column["type"]
            if not isinstance(name, str) or not isinstance(kind, str) or not name or not kind or name in names:
                return False
            names.add(name)
            if "values" in column:
                values = column["values"]
                if (TABLE_ALIASES.get(table, table) != "atoms" or name != "header.state.status" or not isinstance(values, list)
                        or not 1 <= len(values) <= 256 or any(not isinstance(v, str) for v in values)
                        or len(set(values)) != len(values) or any(len(v.encode("utf-8")) > 1024 for v in values)):
                    return False
    return True


async def schema(socket, instance_id, args):
    if args:
        return tool_failure("tool_input_invalid", "The schema request has no arguments")
    try:
        result = await upstream(socket, "GET", "/schema", params={"instance_id": instance_id})
        value = result.get("result")
        if not _valid_schema(value):
            raise ValueError("Invalid Kernel schema")
        return {"result": {"value": value, "text": None}}
    except (ValueError, TypeError, UnicodeError, httpx2.HTTPError):
        return tool_failure("workbench_unavailable", "Kernel schema unavailable")
