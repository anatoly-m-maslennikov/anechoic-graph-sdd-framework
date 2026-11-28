"""Transient View result ownership over the shared Kernel query cache."""

import re

import duckdb

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.results.results__shared import query, validate_select
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.results.result_delivery import deliver, validate_delivery
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.saved_queries.saved_query_runs import save_run_fields, save_sql, validate_name, validate_run_save


_VIEW = re.compile(
    (
        "VIEW (?:TABLE|DOC(?:UMENT)?|STRUCTURE|(?:GRAPH|IMPORTS)(?: "
        "(?:VERTICAL|HORIZONTAL))?)(?: ;)?"
    ),
    re.I | re.ASCII,
)


def _view_sql(sql):
    """Remove a trailing directive formed by plain, top-level SQL tokens."""
    source = sql.encode("utf-8")
    tokens = duckdb.tokenize(sql)
    words, depth = [], 0
    for index, (start, kind) in enumerate(tokens):
        end = tokens[index + 1][0] if index + 1 < len(tokens) else len(source)
        value = source[start:end].decode("utf-8").strip()
        if kind == duckdb.token_type.comment:
            if value.startswith("/*"):
                markers = re.findall(r"/\*|\*/", value)
                if markers.count("/*") != markers.count("*/"):
                    return sql
            continue
        words.append((value, depth, start))
        depth += (value in ("(", "[", "{")) - (value in (")", "]", "}"))
    for index, (value, level, start) in enumerate(words):
        if value.upper() == "VIEW" and level == 0:
            suffix = words[index:]
            if all(item[1] == 0 for item in suffix) and _VIEW.fullmatch(
                " ".join(item[0] for item in suffix)
            ):
                return source[:start].decode("utf-8").rstrip()
    return sql


class ViewQueries:
    def __init__(
        self,
        store,
        connection,
        queries,
        journal_sync=None,
        project_root=None,
        *,
        saved_queries=None,
    ):
        self.store, self.connection, self.queries = store, connection, queries
        self.journal_sync = journal_sync
        self.project_root = project_root
        self.saved_queries = saved_queries
        self.results = {}

    def replace_results(self, replacements):
        for metadata in self.results.values():
            replacement = replacements.get(metadata.get("query_id"))
            if replacement is not None:
                metadata.update(replacement)

    def invoke(self, operation, args):
        if operation == "view_save":
            return self._save_view(args)
        if operation in {"view_run", "view_check", "view_fetch"}:
            if (
                self.connection.execute(
                    "SELECT id FROM ops_generation"
                ).fetchone()
                is None
            ):
                raise ValueError("Generation admission required")
            return self._query_operation(operation, args)
        result = self.store.invoke(operation, args)
        if operation == "view_remove":
            previous = self.results.pop(
                (args["workspace_id"], args["view_id"]), None
            )
            if previous and previous.get("query_id"):
                self.queries.pins.discard(previous["query_id"])
        return self._overlay(result)

    def _overlay(self, result):
        workspace_id = result.get("workspace_id")
        if isinstance(result.get("views"), list):
            result["views"] = [
                self._overlay_view(workspace_id, view)
                for view in result["views"]
            ]
        elif "view_id" in result and "revision" in result:
            result = self._overlay_view(workspace_id, result)
        return result

    def _overlay_view(self, workspace_id, view):
        metadata = self.results.get(
            (workspace_id, view.get("view_id", view.get("id")))
        )
        return view | {"result": metadata} if metadata else view

    @staticmethod
    def _validate(operation, args):
        required = {"workspace_id", "view_id"}
        options = {
            "view_run": {"cursor_position", "preview", "save", "name"},
            "view_check": {"cursor_position"},
            "view_fetch": {
                "offset",
                "page_size",
                "preview",
                "grid",
                "result_delivery",
                "result_format",
            },
        }[operation]
        if not required <= args.keys() <= required | options:
            raise ValueError(f"invalid {operation} arguments")
        if (
            "preview" in args
            and args["preview"] is not None
            and (type(args["preview"]) is not int or args["preview"] < 0)
        ):
            raise ValueError("preview must be a non-negative integer")
        if operation == "view_run":
            validate_run_save(args)
        if operation == "view_fetch":
            if "grid" in args and type(args["grid"]) is not dict:
                raise ValueError("grid must be an object")
            validate_delivery(
                args.get("result_delivery", "inline"),
                args.get("result_format", "json_matrix"),
            )

    @staticmethod
    def _cursor(sql, cursor):
        if cursor is None:
            return
        if type(cursor) is not int or cursor < 0:
            raise ValueError("cursor_position must be a UTF-16 integer")
        units = 0
        for char in sql:
            if units == cursor:
                return
            units += 2 if ord(char) > 0xFFFF else 1
            if units > cursor:
                raise ValueError("cursor_position must be a UTF-16 boundary")
        if units != cursor:
            raise ValueError("cursor_position is outside SQL")

    def _query_operation(self, operation, args):
        self._validate(operation, args)
        view = self.store.invoke(
            "view_get", {key: args[key] for key in ("workspace_id", "view_id")}
        )
        identity = {key: view[key] for key in ("workspace_id", "view_id")}
        key = tuple(identity.values())
        if operation != "view_fetch":
            self._cursor(view["sql"], args.get("cursor_position"))
            if self.journal_sync is not None:
                self.journal_sync()
        if operation == "view_check":
            result = query(self.connection, _view_sql(view["sql"]))
            return identity | {
                "valid": True,
                "columns": result["columns"],
                "row_count": len(result["rows"]),
                "column_count": len(result["columns"]),
            }
        if operation == "view_run":
            return (
                identity
                | {"revision": view["revision"]}
                | self._run_view(key, view["sql"], args)
            )
        return self._fetch_view(key, identity, args)

    def _fetch_view(self, key, identity, args):
        metadata = self.results.get(key)
        if not metadata or metadata["status"] != "success":
            raise ValueError("view has no current result")
        offset, size = args.get("offset", 0), args.get("page_size", 100)
        if type(offset) is not int or offset < 0:
            raise ValueError("offset must be a non-negative integer")
        if type(size) is not int or not 1 <= size <= 1000:
            raise ValueError("page_size must be an integer from 1 to 1000")
        if args.get("preview") is not None:
            size = min(size, args["preview"])
        page = self.queries.page(
            metadata["query_id"], offset, size, args.get("grid")
        )
        page = deliver(
            self.queries,
            self.project_root,
            page,
            args.get("result_delivery", "inline"),
            args.get("result_format", "json_matrix"),
            grid=args.get("grid"),
        )
        return identity | page

    def _run_view(self, key, sql, args):
        prior = self.results.pop(key, None)
        if prior and prior.get("query_id"):
            self.queries.drop(prior["query_id"])
        try:
            page = self.queries.run(
                self.connection, _view_sql(sql), 1, preview=args.get("preview")
            )
            self.queries.pins.add(page["query_id"])
            metadata = {
                "status": "success",
                "error": None,
                "query_id": page["query_id"],
                "row_count": page["row_count"],
                "column_count": page["column_count"],
            }
        except (ValueError, TypeError, duckdb.Error) as error:
            metadata = {
                "status": "failed",
                "error": str(error),
                "query_id": None,
                "row_count": None,
                "column_count": None,
            }
        self.results[key] = metadata
        if metadata["status"] == "success" and args.get("save", False):
            return metadata | save_run_fields(
                self.saved_queries, sql, args.get("name")
            )
        return metadata

    def _save_view(self, args):
        if set(args) == {"workspace_id", "view_id"}:
            source = self.store.invoke("view_get", args)
        elif set(args) in ({"sql"}, {"sql", "name"}):
            if "name" in args:
                validate_name(args["name"])
            source = args
        else:
            raise ValueError("invalid view_save arguments")
        sql = source["sql"]
        validate_select(self.connection, _view_sql(sql))
        return save_sql(self.saved_queries, sql, "view", source.get("name"))
