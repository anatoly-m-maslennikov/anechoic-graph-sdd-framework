"""Validate public representations of a Kernel result page."""

from pathlib import PurePosixPath


def _artifact(value):
    keys = {"path", "format", "row_count", "column_count", "offset", "has_more"}
    if not isinstance(value, dict) or set(value) != keys:
        return False
    path = value["path"]
    return (isinstance(path, str) and bool(path) and not PurePosixPath(path).is_absolute()
            and ".." not in PurePosixPath(path).parts and value["format"] in ("json_matrix", "csv", "toon")
            and all(type(value[k]) is int and value[k] >= 0 for k in ("row_count", "column_count", "offset"))
            and type(value["has_more"]) is bool)


def valid_page(value):
    if not isinstance(value, dict) or not isinstance(value.get("columns"), list):
        return False
    if (not isinstance(value.get("query_id"), str) or not value["query_id"]
            or any(not isinstance(c, dict) or not isinstance(c.get("name"), str)
                   or not isinstance(c.get("type"), str) for c in value["columns"])):
        return False
    payloads = {key for key in ("rows", "csv", "result_file") if key in value}
    if value.get("outcome") == "partial" and "export_error" in value:
        return not payloads and isinstance(value["export_error"], str)
    if len(payloads) != 1:
        return False
    if "rows" in payloads:
        return isinstance(value["rows"], list) and all(isinstance(row, list) for row in value["rows"])
    if "csv" in payloads:
        return isinstance(value["csv"], str)
    return _artifact(value["result_file"])


def with_preview(fields, args):
    if "preview" in args:
        value = args["preview"]
        if type(value) is not int or value < 0:
            raise ValueError("preview must be a non-negative integer")
        fields["preview"] = value
    return fields
