"""Exercise saved SQL through the Backend's private Tool socket."""

import os
import stat
from urllib.parse import parse_qs, urlsplit
from uuid import UUID


def _caller(api, *, base=None, root=None):
    def call(name, arguments):
        return api.post("/tools", json={
            "name": name, "arguments": arguments, "instance_id": "instance", "session_id": None,
            "public_base_url": base, "asserted_project_root": root,
        }).json()
    return call


def _value(test, call, name, arguments):
    response = call(name, arguments)
    test.assertIn("result", response, response)
    return response["result"]["value"]


def _view(test, call, session, sql):
    workspace = _value(test, call, "workspace_open", {"session_id": session})
    opened = workspace["views"][0]
    ids = {"workspace_id": workspace["workspace_id"], "view_id": opened["id"]}
    _value(test, call, "view_update", ids | {"sql": sql, "expected_revision": opened["revision"]})
    return ids


def _read_saved(test, call, item, kind, sql, root):
    test.assertEqual(7, UUID(item["saved_query_id"]).version)
    test.assertEqual(kind, item["kind"])
    link = urlsplit(item["saved_query_url"])
    test.assertEqual(("http", "example.test", "/anechoic/workbench/Anechoic"),
                     (link.scheme, link.netloc, link.path))
    test.assertEqual({"query": [item["saved_query_id"]], "project_root": [str(root)]}, parse_qs(link.query))
    loaded = _value(test, call, "query_load", {"reference": item["saved_query_url"]})
    test.assertEqual((kind, sql), (loaded["kind"], loaded["sql"]))
    return loaded


def assert_saved_writes(test, api, root):
    call = _caller(api, base="http://example.test", root=str(root))
    sql = " SELECT 43 AS answer\n"
    query = _value(test, call, "query_run", {"sql": sql, "save": True, "name": "Bookmark",
                                             "result_delivery": "inline"})
    test.assertEqual([[43]], query["rows"])
    test.assertEqual("Bookmark", _read_saved(test, call, query, "query", sql, root)["name"])
    test.assertNotIn("sql", query)
    view = _view(test, call, "saved-view", sql)
    run = _value(test, call, "view_run", view | {"save": True, "name": "From View"})
    test.assertEqual("success", run["status"])
    test.assertNotIn("rows", run)
    test.assertEqual("From View", _read_saved(test, call, run, "query", sql, root)["name"])
    _value(test, call, "view_rename", view | {"name": "Named View"})
    snapshot = _value(test, call, "view_save", view)
    test.assertEqual(view, {key: snapshot[key] for key in view})
    test.assertEqual("Named View", _read_saved(test, call, snapshot, "view", sql, root)["name"])
    explicit_sql = "SELECT missing_column"
    explicit = _value(test, call, "view_save", {"sql": explicit_sql, "name": "Without execution"})
    test.assertEqual(explicit_sql, explicit["sql"])
    test.assertEqual("Without execution", _read_saved(test, call, explicit, "view", explicit_sql, root)["name"])
    outcomes = [query, run, snapshot, explicit]
    test.assertEqual(len(outcomes), len({item["saved_query_id"] for item in outcomes}))
    assert_save_rejections(test, call, view)


def assert_save_rejections(test, call, view):
    initial = _value(test, call, "query_saved_list", {})
    for args in ({"sql": "SELECT 1", "save": 1}, {"sql": "SELECT 1", "name": "bad"},
                 {"sql": "SELECT 1", "save": True, "name": 1}):
        test.assertEqual("tool_input_invalid", call("query_run", args)["error"]["code"])
    for args in ({"save": 1}, {"name": "bad"}, {"save": True, "name": 1}):
        test.assertEqual("tool_input_invalid", call("view_run", view | args)["error"]["code"])
    for args in ({}, {"workspace_id": view["workspace_id"]}, view | {"sql": "SELECT 1"},
                 view | {"name": "extra"}, {"sql": 1}):
        test.assertEqual("tool_input_invalid", call("view_save", args)["error"]["code"])
    invalid = "SELECT missing_column"
    test.assertIn("error", call("query_run", {"sql": invalid, "save": True}))
    failing = _view(test, call, "invalid-saved-view", invalid)
    result = _value(test, call, "view_run", failing | {"save": True})
    test.assertEqual("failed", result["status"])
    test.assertNotIn("saved_query_id", result)
    test.assertEqual(initial, _value(test, call, "query_saved_list", {}))


def assert_save_failures(test, api, control):
    journal = control / "_journal"
    journal.mkdir(exist_ok=True)
    mode = stat.S_IMODE(journal.stat().st_mode)
    journal.chmod(0o500)
    try:
        if os.access(journal, os.W_OK):
            return  # A privileged test process can bypass file permissions.
        call = _caller(api)
        initial = _value(test, call, "query_saved_list", {})
        result = _value(test, call, "query_run", {"sql": "SELECT 42", "save": True, "result_delivery": "file"})
        test.assertIn(b"42", (control.parent / result["result_file"]["path"]).read_bytes())
        page = _value(test, call, "query_page", {"query_id": result["query_id"], "result_delivery": "inline"})
        test.assertEqual([[42]], page["rows"])
        view = _view(test, call, "partial-save", "SELECT 43")
        run = _value(test, call, "view_run", view | {"save": True})
        fetched = _value(test, call, "view_fetch", view | {"result_delivery": "inline"})
        test.assertEqual([[43]], fetched["rows"])
        for response in (result, run):
            test.assertEqual("partial", response["outcome"])
            test.assertTrue(response["save_error"])
            test.assertNotIn("saved_query_id", response)
        test.assertIn("error", call("view_save", view))
        test.assertEqual(initial, _value(test, call, "query_saved_list", {}))
    finally:
        journal.chmod(mode)
