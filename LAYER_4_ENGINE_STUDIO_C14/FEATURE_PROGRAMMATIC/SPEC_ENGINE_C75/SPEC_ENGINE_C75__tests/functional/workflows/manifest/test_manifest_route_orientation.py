import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85.\
    _package__shared import (http_routes, manifest_shape,
                            validate_manifest)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import (_manifest_binding, manifest_tool_api)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88.\
    DELEGATION_VERIFICATION_C89.\
    _package__shared import (_declares_client, check_sibling_binding,
                            check_sibling_outcome)  # fmt: skip


def _manifest(io):
    boundaries = {"io": io}
    return {
        "source": {"container_component": "C1"},
        "fields": {
            "component_id": "C2",
            "name": "Example",
            "boundaries": boundaries,
        },
        "boundaries": boundaries,
    }


class ManifestRouteOrientationTests(unittest.TestCase):
    def test_route_consumers_lower_both_orientations(self):
        endpoint = "POST /tools"
        canonical = {endpoint: "invoke", "GET /tools": "catalog"}
        for routes in (
            canonical,
            {name: route for route, name in canonical.items()},
        ):
            declaration = {
                "interface": "tool_api",
                "transport": "http",
                "routes": routes,
                "component": "C2",
            }
            manifest = _manifest({"server": {"tool_api": declaration}})
            with self.subTest(routes=routes):
                self.assertEqual(canonical, http_routes(routes))
                self.assertFalse(validate_manifest(manifest)["issues"])
                required = dict(
                    interface="tool_api",
                    transport="http",
                    endpoint=endpoint,
                    route_name="invoke",
                )
                self.assertEqual(
                    required, _manifest_binding(manifest, required)
                )
                self._check_route_clients(declaration, endpoint)

    def _check_route_clients(self, declaration, endpoint):
        for route in (endpoint, "invoke"):
            self.assertTrue(
                _declares_client([declaration], "C2", "tool_api", route)
            )
        self.assertTrue(
            _declares_client(
                [declaration],
                "C2",
                "tool_api",
                {"endpoint": endpoint, "route_name": "invoke"},
            )
        )
        self.assertFalse(
            _declares_client(
                [declaration],
                "C2",
                "tool_api",
                {"endpoint": endpoint, "route_name": "catalog"},
            )
        )
        observed, extra = manifest_tool_api(declaration)
        self.assertEqual([endpoint], observed["operation"])
        self.assertEqual("GET /tools", extra["routes.catalog"])

    def test_route_list_proves_membership_only(self):
        declaration = {
            "transport": "http",
            "routes": ["GET /health", "workspace and saved SQL operations"],
        }
        manifest = _manifest({"server": {"tool_api": declaration}})
        required = dict(
            interface="tool_api",
            transport="http",
            endpoint="GET /health",
            route_name="status",
        )
        self.assertEqual(
            {
                "interface": "tool_api",
                "transport": "http",
                "endpoint": "GET /health",
            },
            _manifest_binding(manifest, required),
        )
        self.assertNotIn("operation", manifest_tool_api(declaration)[0])
        self.assertIn(
            "workspace and saved SQL operations",
            http_routes(declaration["routes"]),
        )
        required["endpoint"] = "POST /tools"
        self.assertIsNone(_manifest_binding(manifest, required)["endpoint"])

    def test_mixed_and_ambiguous_route_maps_report_source_field(self):
        for routes in (
            {"GET /a": "a", "b": "GET /b"},
            {"a": "GET /a", "b": "GET /a"},
            {"GET /a": "a", "GET /b": "a"},
            {"a": "GET /a malformed"},
        ):
            declaration = {"transport": "http", "routes": routes}
            io = {"server": {"tool_api": declaration}, "client": [declaration]}
            with self.subTest(routes=routes):
                self.assertEqual(
                    {
                        "boundaries.io.server.tool_api.routes",
                        "boundaries.io.client.0.routes",
                    },
                    {
                        issue["field"]
                        for issue in validate_manifest(_manifest(io))["issues"]
                    },
                )

    def test_class_shapes_have_a_named_collection_and_lower_the_legacy_layout(
        self,
    ):
        classes = {
            "Atom": {"fields": {"header": "Header"}},
            "Plan": {"base": "Atom"},
        }
        canonical = {"class_shapes": classes}
        legacy = {"server": {"bundled_model_classes": {"classes": classes}}}
        self.assertEqual(
            manifest_shape({"io": canonical}), manifest_shape({"io": legacy})
        )
        outcomes = {
            "render": {
                "outcomes": {
                    "rendered": {"must_effect": [("display", "shown")]}
                }
            }
        }
        for io in (canonical, legacy, {**canonical, "server": outcomes}):
            report = validate_manifest(_manifest(io))
            self.assertFalse(report["issues"])
            self.assertFalse(report["unresolved"])
        report = validate_manifest(_manifest({**canonical, **legacy}))
        self.assertEqual(
            ["boundaries.io.class_shapes"],
            [issue["field"] for issue in report["issues"]],
        )


class CallerActionSelectionTests(unittest.TestCase):
    def _sibling_parties(self):
        declaration = {
            "component": "C3",
            "interface": "api",
            "transport": "http",
            "routes": ["POST /tools"],
        }
        caller = {
            "component_id": "C2",
            "manifest": _manifest({"client": [declaration]}),
            "solution": {"source": "caller"},
            "issues": [],
        }
        provider = {
            "component_id": "C3",
            "manifest": _manifest({"server": {"api": declaration}}),
            "contract": {"source": "contract", "claims": []},
            "solution": {"source": "solution"},
        }
        return caller, provider

    def _sibling_fixture(self):
        caller, provider = self._sibling_parties()
        actions = {}
        for action, output in (("first", "succeeded"), ("second", "failed")):
            detail = {
                "component": "C3",
                "action": "invoke",
                "output": output,
                "interface": "api",
                "transport": "http",
                "route": "POST /tools",
            }
            expect = {
                "kind": "effect",
                "target": "C3",
                "outcome": output,
                "detail": detail,
            }
            actions[action] = {
                "action": action,
                "states": [
                    {"transitions": [{"event": "call", "expect": expect}]}
                ],
            }
        workflow = {"operations": actions}
        compiled = {
            "claims": {"solution": workflow},
            "issues": [],
            "unresolved": [],
        }
        delegation = (
            "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
            "LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88."
            "DELEGATION_VERIFICATION_C89."
        )
        return caller, provider, workflow, compiled, delegation

    def test_public_sibling_checks_select_repeated_event_by_caller_action(
        self,
    ):
        caller, provider, workflow, compiled, delegation = (
            self._sibling_fixture()
        )
        pins = ({}, {}, {"container_component": "C2"})

        def capture(sources, obligations, **options):
            return {"selected": obligations["caller"]}

        self._check_binding(
            caller, provider, compiled, delegation, pins, capture
        )
        self._check_outcomes(
            caller, provider, workflow, compiled, delegation, pins, capture
        )

    def _check_binding(
        self, caller, provider, compiled, delegation, pins, capture
    ):
        with (
            patch(
                delegation + "sibling_delegation__pub._load_sibling_caller",
                return_value=caller,
            ),
            patch(
                delegation + "sibling_delegation__pub.load_boundary_model",
                return_value=provider,
            ),
            patch(
                delegation + "sibling_delegation__pub.compile_lean",
                return_value=compiled,
            ),
            patch(
                delegation + "sibling_delegation__pub.compare_delegation",
                side_effect=capture,
            ),
        ):
            binding = check_sibling_binding(
                ".",
                pins,
                "C3",
                (),
                event="call",
                interface="api",
                route="POST /tools",
                action="invoke",
                caller_action="second",
            )
        self.assertEqual("POST /tools", binding["selected"]["endpoint"])

    def _check_outcomes(
        self, caller, provider, workflow, compiled, delegation, pins, capture
    ):
        for action, output in (
            ("first", "succeeded"),
            ("second", "failed"),
            (None, None),
        ):
            with (
                patch(
                    delegation + "trace_delegation__pub._load_sibling_caller",
                    return_value=caller,
                ),
                patch(
                    delegation + "trace_delegation__pub.load_boundary_model",
                    return_value=provider,
                ),
                patch(
                    delegation + "trace_delegation__pub.compile_lean",
                    return_value=compiled,
                ),
                patch(
                    delegation + "trace_delegation__pub.normalize_claim",
                    return_value=(workflow, None),
                ),
                patch(
                    delegation + "trace_delegation__pub.compare_delegation",
                    side_effect=capture,
                ),
            ):
                result = check_sibling_outcome(
                    ".",
                    pins,
                    "C3",
                    (),
                    event="call",
                    interface="api",
                    caller_action=action,
                )
            self.assertEqual(output, result["selected"].get("output"))
