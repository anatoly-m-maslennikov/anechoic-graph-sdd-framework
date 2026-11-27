"""Validate and evaluate grid operations over one bounded cached result."""

import json
import re

import duckdb


def _order(value):
    if type(value) is not dict or set(value) != {"column", "direction"}:
        raise ValueError("grid sort must contain exactly column and direction")
    if type(value["column"]) is not int or value["column"] < 0:
        raise ValueError("grid column must be a non-negative integer")
    if value["direction"] not in ("asc", "desc"):
        raise ValueError("grid direction must be asc or desc")
    return value


def _validate_filters(filters):
    for item in filters:
        if type(item) is not dict or set(item) != {"column", "operator", "value"}:
            raise ValueError("grid filter must contain exactly column, operator and value")
        if type(item["column"]) is not int or item["column"] < 0:
            raise ValueError("grid column must be a non-negative integer")
        if item["operator"] != "contains" or type(item["value"]) is not str:
            raise ValueError("grid filter requires contains and a string value")


def parse_grid(grid, count):
    if grid is None:
        grid = {}
    if type(grid) is not dict or set(grid) - {"sort", "filters", "group_by"}:
        raise ValueError("grid must contain only sort, filters and group_by")
    sort, filters, group = grid.get("sort", []), grid.get("filters", []), grid.get("group_by")
    if type(sort) is not list or type(filters) is not list:
        raise ValueError("grid sort and filters must be lists")
    if "group_by" in grid and type(group) is not dict:
        raise ValueError("grid group_by must be an object")
    for item in sort:
        _order(item)
    if group is not None:
        _order(group)
    _validate_filters(filters)
    for item in sort + filters + ([group] if group else []):
        if item["column"] >= count:
            raise ValueError("grid column is out of range")
    return sort, filters, group


def _sort_column(names, columns, index):
    kind = columns[index]["type"] if columns else ""
    if re.fullmatch(r"(?:DECIMAL\([0-9]{1,2},[0-9]{1,2}\)|(?:U)?(?:TINYINT|SMALLINT|INTEGER|BIGINT|HUGEINT))", kind):
        return f"CAST({names[index]} AS {kind})"
    return names[index]


def grid_page(rows, count, offset, size, grid, columns=None):
    sort, filters, group = parse_grid(grid, count)
    if not rows:
        return [], 0, [] if group else None
    if not sort and not filters and group is None:
        return rows[offset:offset + size], len(rows), None
    names = [f'"c{i}"' for i in range(count)]
    values = ",".join("(" + ",".join("?" for _ in range(count + 1)) + ")" for _ in rows)
    parameters = [value for index, row in enumerate(rows) for value in (index, *row)]
    source = f'WITH source("ordinal", {", ".join(names)}) AS (VALUES {values})'
    predicates = [f'instr(lower(CAST({names[item["column"]]} AS VARCHAR)), lower(?)) > 0' for item in filters]
    filtered = source + ", filtered AS MATERIALIZED (SELECT * FROM source" + (" WHERE " + " AND ".join(predicates) if predicates else "") + ")"
    parameters += [item["value"] for item in filters]
    order = [f'{_sort_column(names, columns, item["column"])} {item["direction"].upper()} NULLS LAST'
             for item in ([group] if group else []) + sort]
    order.append('"ordinal" ASC')
    connection = duckdb.connect(":memory:")
    try:
        selection = "*" if group is None else f'*, count(*) OVER (PARTITION BY {names[group["column"]]}) AS group_count'
        query = filtered + f', page AS (SELECT {selection} FROM filtered ORDER BY {", ".join(order)} LIMIT ? OFFSET ?)'
        result = connection.execute(query + f' SELECT total.n, page.* FROM (SELECT count(*) AS n FROM filtered) total LEFT JOIN page ON true ORDER BY {", ".join(order)}', parameters + [size, offset]).fetchall()
        total = result[0][0]
        raw = [row[1:] for row in result if row[1] is not None]
    finally:
        connection.close()
    page = [list(row[1:count + 1]) for row in raw]
    groups = None
    if group is not None:
        groups, seen = [], set()
        for row, native in zip(page, raw, strict=False):
            value = row[group["column"]]
            key = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            if key not in seen:
                seen.add(key)
                groups.append({"value": value, "count": native[-1]})
    return page, total, groups
