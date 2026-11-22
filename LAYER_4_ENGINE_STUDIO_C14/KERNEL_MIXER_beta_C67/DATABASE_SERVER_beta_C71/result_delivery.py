"""Deliver bounded cached results as inline pages or Project files."""

import csv
from io import StringIO
import json
import os
from pathlib import Path
import uuid

import toon_format

from .work_journal import _open_directory


_DIRECTORY = Path(".anechoic_tmp/workbench/query_results")
_EXTENSIONS = {"json_matrix": "json", "csv": "csv", "toon": "toon"}
_INLINE_BYTES = 4096


def validate_delivery(delivery, result_format):
    if delivery not in ("inline", "file", "auto"):
        raise ValueError("result_delivery must be file, inline or auto")
    if result_format not in _EXTENSIONS:
        raise ValueError("unsupported result format")


def _matrix(columns, rows):
    if any(len(row) != len(columns) for row in rows):
        raise ValueError("result row width does not match column count")
    return {"columns": columns, "rows": [list(row) for row in rows]}


def _csv(matrix):
    stream = StringIO(newline="")
    writer = csv.writer(stream, quoting=csv.QUOTE_NOTNULL, lineterminator="\r\n")
    writer.writerow(matrix["columns"])
    for row in matrix["rows"]:
        writer.writerow([json.dumps(value, ensure_ascii=False, separators=(",", ":"))
                         if isinstance(value, (list, dict)) else value for value in row])
    return stream.getvalue()


def _encode(matrix, result_format):
    if result_format == "json_matrix":
        return json.dumps(matrix, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if result_format == "csv":
        return _csv(matrix)
    return toon_format.dumps(matrix)


def _write(root, matrix, result_format, offset, has_more):
    directory = _open_directory(Path(root), _DIRECTORY.parts, create=True, same_device=True)
    name = f"{uuid.uuid7()}.{_EXTENSIONS[result_format]}"
    try:
        descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
                stream.write(_encode(matrix, result_format))
        except BaseException:
            os.unlink(name, dir_fd=directory)
            raise
    finally:
        os.close(directory)
    return {"path": (_DIRECTORY / name).as_posix(), "format": result_format,
            "row_count": len(matrix["rows"]), "column_count": len(matrix["columns"]),
            "offset": offset, "has_more": has_more}


def deliver(queries, root, page, delivery, result_format, *, full=False, grid=None):
    validate_delivery(delivery, result_format)
    page.pop("sql", None)
    if delivery == "inline" and result_format != "csv":
        return page
    matrix = _matrix([column["name"] for column in page["columns"]], page["rows"])
    inline_candidate = delivery == "inline" or delivery == "auto" and (not full or not page["has_more"])
    if inline_candidate and result_format == "csv":
        content = _csv(matrix)
        if delivery == "inline" or len(content.encode("utf-8")) <= _INLINE_BYTES:
            page.pop("rows")
            page["csv"] = content
            return page
    elif inline_candidate and result_format == "json_matrix":
        if len(json.dumps(page).encode("utf-8")) <= _INLINE_BYTES:
            return page
    try:
        if full:
            complete = queries.page(page["query_id"], 0, 1000, grid)
            matrix = _matrix([column["name"] for column in complete["columns"]], complete["rows"])
            artifact = _write(root, matrix, result_format, 0, False)
        else:
            artifact = _write(root, matrix, result_format, page["offset"], page["has_more"])
        page.pop("rows", None)
        page["result_file"] = artifact
    except Exception as error:
        page.pop("rows", None)
        page.update(outcome="partial", export_error=str(error))
    return page
