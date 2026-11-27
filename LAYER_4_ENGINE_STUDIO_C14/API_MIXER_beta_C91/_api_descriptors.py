"""Build read-only query Tool descriptors."""


def _grid(number):
    order = {
        "type": "object",
        "properties": {
            "column": number,
            "direction": {"type": "string", "enum": ["asc", "desc"]},
        },
        "required": ["column", "direction"],
        "additionalProperties": False,
    }
    filt = {
        "type": "object",
        "properties": {
            "column": number,
            "operator": {"const": "contains"},
            "value": {"type": "string"},
        },
        "required": ["column", "operator", "value"],
        "additionalProperties": False,
    }
    grid = {
        "type": "object",
        "properties": {
            "sort": {"type": "array", "items": order},
            "filters": {"type": "array", "items": filt},
            "group_by": order,
        },
        "additionalProperties": False,
    }
    return grid


def _definitions(number, page_size, delivery, fmt, grid):
    return {
        "query_check": (
            "Check read-only SQL without retaining the result.",
            {"sql": {"type": "string"}, "cursor_position": number},
            ["sql"],
        ),
        "query_page": (
            "Read a page of a retained Project query result.",
            {
                "query_id": {"type": "string"},
                "offset": number,
                "page_size": page_size,
                "preview": number,
                "result_delivery": delivery,
                "result_format": fmt,
                "grid": grid,
            },
            ["query_id"],
        ),
        "query_schema": (
            "Read the selected Project's public SQL schema.",
            {},
            [],
        ),
    }


def query_descriptors(descriptor):
    annotations = {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
    number = {"type": "integer", "minimum": 0}
    page_size = {"type": "integer", "minimum": 1, "maximum": 1000}
    grid = _grid(number)
    delivery = {
        "type": "string",
        "enum": ["file", "inline", "auto"],
        "default": "file",
    }
    fmt = {"type": "string", "enum": ["json_matrix", "csv", "toon"]}
    definitions = _definitions(number, page_size, delivery, fmt, grid)
    result = {"query_run": descriptor()}
    for name, (description, properties, required) in definitions.items():
        result[name] = {
            "name": name,
            "description": description,
            "annotations": annotations,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        }
    return result
