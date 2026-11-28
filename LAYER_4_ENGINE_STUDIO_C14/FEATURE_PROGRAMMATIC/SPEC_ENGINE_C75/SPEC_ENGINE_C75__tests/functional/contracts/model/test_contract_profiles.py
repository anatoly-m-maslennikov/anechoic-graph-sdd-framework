import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import parse_cli_contract  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import parse_contract  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import parse_trace_contract  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import check_cli_spec  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import check_trace_spec  # fmt: skip

from ._contract_profile_fixture import _edge as _edge, _machine as _machine
from ..cli.test_cli_spec import _carrier
from .test_contract_model import CLAIM

_TRACE = "declare_trace_contract(action='run', "
_CLI = (
    "declare_cli_contract(interface='suite', action='run', runner='uv', "
    "path='suite.py', "
)
_HTTP = (
    "declare_http_contract(interface='suite', action='run', route='widgets',\n"
    "    operation='POST /widgets', outcomes={'succeeded': (201, 'result'), "
    "'failed': (409, 'typed_error')},\n"
    "    checks={'interface': {'response_format': 'json'}})"
)
_CASES = (
    "effects={'approve': ('review', 'passed'), "
    "'render': ('draft', 'ready')},\n"
    "    cases={'succeeded': {'must_effect': ('render',), "
    "'must_precede': (('approve', 'render'),)},\n"
    "           'failed': {}},\n"
    "    invariant={'forbid_effect': ('publish',)})"
)


def _claim(language, source):
    return f"## Claim\n\n### Formal Claim\n\n```{language}\n{source}\n```\n"


def _pins(root, server, language, contract, machine):
    manifest = (
        "## Formal Manifest\n\n```python\n"
        "from anechoic.model import ComponentManifest\n"
        "ComponentManifest(component_id='C2', name='Example', "
        f"boundaries={{'io': {{'server': {{'suite': {server!r}}}}}}})\n```\n"
    )
    solution = (
        "component_workflow(component='C2', action='run', "
        f"machine={machine!r})"
    )
    return (
        _carrier(root, "AN-S-1", "component_manifest", "C1", "{}", manifest),
        _carrier(
            root,
            "AN-S-2",
            "component_contract",
            "C2",
            "{ANSWERS: [AN-S-1]}",
            _claim(language, contract),
        ),
        _carrier(
            root,
            "AN-S-3",
            "decision",
            "C2",
            "{IS_SOLUTION_FOR: [AN-S-2@1]}",
            _claim("python", solution),
        ),
    )


class ContractProfileTests(unittest.TestCase):
    def test_named_effects_lower_to_the_same_obligations_in_both_transports(
        self,
    ):
        legacy = parse_trace_contract(
            _TRACE + "output='succeeded', must_effect=(('draft', 'ready'),), "
            "must_precede=((('review', 'passed'), ('draft', 'ready')),))"
        )
        for claim in (
            parse_trace_contract(_TRACE + _CASES),
            parse_cli_contract(_CLI + _CASES),
        ):
            self.assertEqual(legacy, claim["cases"][0])
            self.assertEqual(
                {"action": "run", "output": "failed"}, claim["cases"][1]
            )
            self.assertEqual(
                {"forbid_effect": ["publish"]}, claim["invariant"]
            )
        for clauses in (
            _CASES.replace("('approve', 'render')", "('missing', 'render')"),
            _CASES.replace("('publish',)", "('review',)"),
        ):
            with self.assertRaises(ValueError):
                parse_trace_contract(_TRACE + clauses)

    @unittest.skipUnless(shutil.which("lean"), "Lean unavailable")
    def test_invariant_reaches_an_effect_on_failure_in_both_transports(self):
        for transport in ("cli", "trace"):
            for forbidden, status in (
                (None, "matched"),
                ("publish", "conflicting"),
            ):
                with (
                    self.subTest(transport=transport, forbidden=forbidden),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    root = Path(directory)
                    binding = {
                        "transport": transport,
                        "runner": "uv",
                        "path": "suite.py",
                    }
                    machine = _machine(
                        binding,
                        {"exit_status_class": "zero"},
                        {"exit_status_class": "nonzero"},
                        forbidden=forbidden,
                    )
                    contract = (
                        _CLI + "outcomes={'succeeded': 'zero', "
                        "'failed': 'nonzero'}, "
                        if transport == "cli"
                        else _TRACE
                    ) + _CASES
                    pins = _pins(
                        root,
                        binding if transport == "cli" else {},
                        f"python {transport}",
                        contract,
                        machine,
                    )
                    if transport == "cli":
                        report = check_cli_spec(
                            root, "C2", *pins, interface="suite"
                        )
                    else:
                        report = check_trace_spec(root, "C2", *pins)
                    self._assert_invariant(report, status)

    def _assert_invariant(self, report, status):
        facts = report["directions"]["contract_solution"]["facts"]
        self.assertIn(
            ("must_precede", "matched"),
            {(row["key"], row["status"]) for row in facts},
        )
        self.assertEqual(
            [status],
            [
                row["status"]
                for row in facts
                if row["key"] == "forbid_effect" and row["scope"] == "action"
            ],
        )

    def test_http_types_and_registered_checks(self):
        self.assertEqual("http", parse_contract(_HTTP)["profile"])
        explicit = parse_contract(
            CLAIM.replace("declare_contract", "declare_tool_api_contract")
        )
        self.assertEqual(
            {"profile": "tool_api", **parse_contract(CLAIM)}, explicit
        )
        for claim in (
            _HTTP.replace("409, 'typed_error'", "201, 'typed_error'"),
            _HTTP.replace("'failed': (409", "'invalid_input': (409"),
            _HTTP.replace("'failed': (409", "'internal_error': (409"),
            _HTTP.replace("409, 'typed_error'", "True, 'typed_error'"),
            _HTTP.replace("response_format", "unsupported"),
            CLAIM.replace("protocol", "unsupported"),
        ):
            with self.subTest(claim=claim), self.assertRaises(ValueError):
                parse_contract(claim)

    @unittest.skipUnless(shutil.which("lean"), "Lean unavailable")
    def test_pinned_http_chain_compares_typed_responses_and_checks(self):
        server = {"transport": "http", "routes": {"POST /widgets": "widgets"}}
        trigger = {
            "transport": "http",
            "route": "POST /widgets",
            "operation": "widgets",
        }
        contract = _HTTP.replace(
            "route='widgets'", "route_name='widgets'"
        ).replace("operation='POST /widgets'", "endpoint='POST /widgets'")
        for code, encoding, status in (
            (201, "json", "matched"),
            (200, "html", "conflicting"),
            (None, None, "unresolved"),
        ):
            with (
                self.subTest(code=code),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                success = {
                    "status_code": code,
                    "envelope": "result",
                    "response_format": encoding,
                }
                failure = {
                    "status_code": 409,
                    "envelope": "typed_error",
                    "response_format": "json",
                }
                pins = _pins(
                    root,
                    server,
                    "python contract",
                    contract,
                    _machine(trigger, success, failure),
                )
                check = verify_formal_chain(root, "C2", *pins, action="run")
                self.assertEqual("compared", check["outcome"])
                self.assertEqual([], check["uncovered_outcomes"])
                self._assert_http_check(check, status)

    def _assert_http_check(self, check, status):
        facts = check["directions"]["contract_solution"]["facts"]
        statuses = {fact["key"]: fact["status"] for fact in facts}
        self.assertEqual("matched", statuses["endpoint"])
        self.assertEqual("matched", statuses["route_name"])
        self.assertEqual(status, statuses["outcomes.succeeded"])
        self.assertEqual(status, statuses["interface.response_format"])
        self.assertEqual("matched", statuses["outcomes.failed"])

    @unittest.skipUnless(shutil.which("lean"), "Lean unavailable")
    def test_http_reports_unchecked_schemas_and_partial_response_conflicts(
        self,
    ):
        server = {"transport": "http", "routes": {"POST /widgets": "widgets"}}
        trigger = {
            "transport": "http",
            "route": "POST /widgets",
            "operation": "widgets",
        }
        schema = {"type": "object", "required": ["id"]}
        contract = _HTTP[:-1] + (
            f", request_schema={schema!r}, "
            f"response_schemas={{'succeeded': {schema!r}, 'failed': {{}}}})"
        )
        failure = {
            "status_code": 409,
            "envelope": "typed_error",
            "response_format": "json",
        }
        for detail, verdict in (
            ({"status_code": 201, "envelope": "result"}, "matched"),
            ({"status_code": 201}, "unresolved"),
            ({"status_code": 202}, "conflicting"),
            ({"envelope": "empty"}, "conflicting"),
        ):
            with (
                self.subTest(detail=detail),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                success = {"response_format": "json", **detail}
                pins = _pins(
                    root,
                    server,
                    "python contract",
                    contract,
                    _machine(trigger, success, failure),
                )
                report = verify_formal_chain(root, "C2", *pins, action="run")
                self.assertEqual("compared", report["outcome"], report)
                self._assert_http_coverage(report, verdict, schema)

    def _assert_http_coverage(self, report, verdict, schema):
        facts = {
            item["key"]: item
            for item in report["evidence"]["coverage"]
            if item["direction"] == "contract_solution"
        }
        self.assertEqual(verdict, facts["outcomes.succeeded"]["status"])
        for key, expected in (
            ("request_schema", schema),
            ("response_schemas.succeeded", schema),
            ("response_schemas.failed", {}),
        ):
            self.assertEqual(
                ("unresolved", expected),
                (facts[key]["status"], facts[key]["left"]),
            )
        self.assertEqual(
            "conflicting" if verdict == "conflicting" else "unresolved",
            report["status"],
        )
