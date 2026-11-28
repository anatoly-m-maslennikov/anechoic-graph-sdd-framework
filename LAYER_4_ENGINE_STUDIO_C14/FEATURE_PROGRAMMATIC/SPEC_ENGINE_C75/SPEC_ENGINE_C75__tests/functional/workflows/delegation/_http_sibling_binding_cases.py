# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88.DELEGATION_VERIFICATION_C89.\
    _package__shared import check_sibling_binding
# fmt: on
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from .test_in_process_delegation import carriers


def _http_fixture_0(root, route, detail):
    caller = carriers(
        root,
        "C2",
        1,
        {
            "client": {
                "database": {
                    "component": "C3",
                    "transport": "http",
                    "routes": [route],
                }
            }
        },
        {"kind": "trigger", "target": "caller"},
        {
            "kind": "effect",
            "target": "C3",
            "outcome": "called",
            "detail": detail,
        },
    )
    return caller


def _http_fixture_1(root, route, routes):
    provider = carriers(
        root,
        "C3",
        4,
        {
            "server": {
                "database": {
                    "transport": "http",
                    "routes": routes,
                }
            }
        },
        {
            "kind": "trigger",
            "target": "database",
            "detail": {
                "transport": "http",
                "route": route,
                "operation": "POST /database",
            },
        },
        {
            "kind": "effect",
            "target": "C3",
            "outcome": "called",
        },
        (
            ", interface='database', transport='http'"
            ", route='query', operation='POST /databa"
            "se'"
        ),
    )
    return provider


def _http_fixture_2(root, route, effect):
    caller = carriers(
        root,
        "C2",
        1,
        {
            "client": {
                "tools": {
                    "component": "C3",
                    "transport": "http",
                    "routes": [route],
                }
            }
        },
        {"kind": "trigger", "target": "caller"},
        effect,
    )
    return caller


def _http_fixture_3(root, route, binding):
    provider = carriers(
        root,
        "C3",
        4,
        {
            "server": {
                "tools": {
                    "transport": "http",
                    "routes": [route, "POST /other"],
                }
            }
        },
        {
            "kind": "trigger",
            "target": "tools",
            "detail": {"operation": "run", **binding},
        },
        {"kind": "effect", "target": "C3", "outcome": "called"},
        (
            ", interface='tools', transport='http', r"
            "oute='POST /tools', operation='run'"
        ),
    )
    return provider


def _http_fixture_4(root, route, detail):
    caller = carriers(
        root,
        "C2",
        1,
        {
            "client": {
                "jobs": {
                    "component": "C3",
                    "transport": "http",
                    "routes": [route],
                }
            }
        },
        {"kind": "trigger", "target": "caller"},
        {
            "kind": "effect",
            "target": "C3",
            "outcome": "called",
            "detail": detail,
        },
    )
    return caller


def _http_fixture_5(root, route):
    provider = carriers(
        root,
        "C3",
        4,
        {"server": {"jobs": {"transport": "http", "routes": [route]}}},
        {
            "kind": "trigger",
            "target": "jobs",
            "detail": {
                "transport": "http",
                "route": route,
                "operation": "run",
            },
        },
        {"kind": "effect", "target": "C3", "outcome": "called"},
        (
            ", interface='jobs', transport='http', ro"
            "ute='POST /jobs/build', operation='run'"
        ),
    )
    return provider


class HttpSiblingBindingTests(unittest.TestCase):
    def test_provider_route_map_and_list_require_requested_route(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        route = "query"
        detail = {"interface": "database", "transport": "http", "route": route}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            caller = _http_fixture_0(root, route, detail)
            for routes, expected in (
                ({"query": "POST /database"}, "matched"),
                ({"archive": "POST /archive"}, "conflicting"),
                (["archive"], "conflicting"),
            ):
                with self.subTest(routes=routes):
                    provider = _http_fixture_1(root, route, routes)
                    result = check_sibling_binding(
                        root,
                        caller,
                        "C3",
                        provider,
                        event="invoke",
                        interface="database",
                        route=route,
                        lean=lean,
                    )
                    self.assertEqual(
                        expected,
                        result["directions"]["caller_manifest"]["status"],
                    )

    def test_named_call_selects_only_its_provider_operation(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        route = "POST /tools"
        binding = {"transport": "http", "route": route}
        effect = {
            "kind": "effect",
            "target": "C3",
            "outcome": "called",
            "detail": {"interface": "tools", "action": "run", **binding},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            caller = _http_fixture_2(root, route, effect)
            provider = _http_fixture_3(root, route, binding)
            _add_other_operation(root, provider, route)

            def check(action):
                return check_sibling_binding(
                    root,
                    caller,
                    "C3",
                    provider,
                    event="invoke",
                    interface="tools",
                    route=route,
                    action=action,
                    lean=lean,
                )

            self.assertEqual("matched", check("run")["status"])
            self.assertEqual("unresolved", check("other")["status"])
            solution = root / provider[2]["path"]
            solution.write_text(
                solution.read_text().replace(route, "POST /other")
            )
            self.assertEqual(
                "conflicting",
                check("run")["directions"]["caller_solution"]["status"],
            )

    def test_http_route_and_unsupported_caller_route(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        route = "POST /jobs/build"
        detail = {"interface": "jobs", "transport": "http", "route": route}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            caller = _http_fixture_4(root, route, detail)
            provider = _http_fixture_5(root, route)

            def check():
                return check_sibling_binding(
                    root,
                    caller,
                    "C3",
                    provider,
                    event="invoke",
                    interface="jobs",
                    route=route,
                    lean=lean,
                )

            def statuses():
                return {
                    name: row["status"]
                    for name, row in check()["directions"].items()
                }

            _assert_jobs_route(
                self, statuses, check, root, caller, provider, route
            )


def _add_other_operation(root, provider, route):
    for pin in provider[1:]:
        path = root / pin["path"]
        original = path.read_text()
        second = original[original.index("```") :].replace("'run'", "'other'")
        path.write_text(original + "\n" + second.replace(route, "POST /other"))


def _assert_jobs_route(self, statuses, check, root, caller, provider, route):
    matched = {
        "caller_manifest": "matched",
        "caller_contract": "matched",
        "caller_solution": "matched",
    }
    self.assertEqual(matched, statuses())
    self.assertTrue(
        any("response" in item.lower() for item in check()["unmodeled"])
    )
    solution = root / provider[2]["path"]
    original = solution.read_text()
    solution.write_text(original.replace(route, "POST /jobs/other"))
    self.assertEqual({**matched, "caller_solution": "conflicting"}, statuses())
    solution.write_text(original)
    manifest = root / caller[0]["path"]
    manifest.write_text(
        manifest.read_text().replace(route, "POST /jobs/other")
    )
    with self.assertRaises(ValueError):
        check()
