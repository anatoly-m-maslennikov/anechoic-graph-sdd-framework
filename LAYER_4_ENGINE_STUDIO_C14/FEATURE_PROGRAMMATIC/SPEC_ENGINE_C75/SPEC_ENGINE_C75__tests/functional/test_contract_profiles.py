import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    parse_cli_contract,
    parse_contract,
    parse_trace_contract,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    check_cli_spec,
    check_trace_spec,
)

from .test_cli_spec import _carrier
from .test_contract_model import CLAIM

_TRACE = "declare_trace_contract(action='run', "
_CLI = "declare_cli_contract(interface='suite', action='run', runner='uv', path='suite.py', "
_HTTP = """declare_http_contract(interface='suite', action='run', route='widgets',
    operation='POST /widgets', outcomes={'succeeded': (201, 'result'), 'failed': (409, 'typed_error')},
    checks={'interface': {'response_format': 'json'}})"""
_CASES = """effects={'approve': ('review', 'passed'), 'render': ('draft', 'ready')},
    cases={'succeeded': {'must_effect': ('render',), 'must_precede': (('approve', 'render'),)},
           'failed': {}},
    invariant={'forbid_effect': ('publish',)})"""


def _edge(destination, kind, *, target=None, outcome=None, detail=None):
    expectation = {"kind": kind}
    expectation.update(
        {
            key: value
            for key, value in (
                ("target", target),
                ("outcome", outcome),
                ("detail", detail),
            )
            if value is not None
        }
    )
    return {
        "target": destination,
        "guard": {"type": "matchesTrace", "params": expectation},
    }


def _machine(binding, success, failure, *, forbidden=None):
    states = {
        "idle": {
            "on": {
                "start": _edge(
                    "start", "trigger", target="suite", detail=binding
                )
            }
        },
        "start": {
            "on": {
                "approve": _edge(
                    "approved", "effect", target="review", outcome="passed"
                ),
                "fail": _edge(
                    "done", "output", outcome="failed", detail=failure
                ),
            }
        },
        "approved": {
            "on": {
                "render": _edge(
                    "ready", "effect", target="draft", outcome="ready"
                )
            }
        },
        "ready": {
            "on": {
                "return": _edge(
                    "done", "output", outcome="succeeded", detail=success
                )
            }
        },
        "done": {"type": "final"},
    }
    if forbidden is not None:
        states["abort"] = {"on": {"fail": states["start"]["on"]["fail"]}}
        states["start"]["on"]["fail"] = _edge(
            "abort", "effect", target=forbidden, outcome="attempted"
        )
    return {"id": "suite", "initial": "idle", "states": states}


def _claim(language, source):
    return f'## Claim\n\n### Formal Claim\n\n```{language}\n{source}\n```\n'


def _pins(root, server, language, contract, machine):
    manifest = (
        "## Formal Manifest\n\n```python\nfrom anechoic.model import ComponentManifest\n"
        "ComponentManifest(component_id='C2', name='Example', "
        f"boundaries={{'io': {{'server': {{'suite': {server!r}}}}}}})\n```\n"
    )
    solution = f"component_workflow(component='C2', action='run', machine={machine!r})"
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

    @unittest.skipUnless(shutil.which('lean'), 'Lean unavailable')
    def test_invariant_reaches_an_effect_on_failure_in_both_transports(self):
        for transport in ('cli', 'trace'):
            for forbidden, status in ((None, 'matched'), ('publish', 'conflicting')):
                with self.subTest(transport=transport, forbidden=forbidden), tempfile.TemporaryDirectory() as directory:
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
                        _CLI
                        + "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}, "
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
                        report = check_trace_spec(root, 'C2', *pins)
                    facts = report['directions']['contract_solution']['facts']
                    self.assertIn(('must_precede', 'matched'), {(row['key'], row['status']) for row in facts})
                    self.assertEqual([status], [row['status'] for row in facts
                                                if row['key'] == 'forbid_effect' and row['scope'] == 'action'])

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

    @unittest.skipUnless(shutil.which('lean'), 'Lean unavailable')
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
                success = {'status_code': code, 'envelope': 'result', 'response_format': encoding}
                failure = {'status_code': 409, 'envelope': 'typed_error', 'response_format': 'json'}
                pins = _pins(root, server, 'python contract', contract, _machine(trigger, success, failure))
                check = verify_formal_chain(root, 'C2', *pins, action='run')
                self.assertEqual('compared', check['outcome'])
                self.assertEqual([], check['uncovered_outcomes'])
                facts = check['directions']['contract_solution']['facts']
                statuses = {fact['key']: fact['status'] for fact in facts}
                self.assertEqual('matched', statuses['endpoint'])
                self.assertEqual('matched', statuses['route_name'])
                self.assertEqual(status, statuses['outcomes.succeeded'])
                self.assertEqual(status, statuses['interface.response_format'])
                self.assertEqual('matched', statuses['outcomes.failed'])

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
                success = {'response_format': 'json', **detail}
                pins = _pins(root, server, 'python contract', contract, _machine(trigger, success, failure))
                report = verify_formal_chain(root, 'C2', *pins, action='run')
                self.assertEqual('compared', report['outcome'], report)
                facts = {item['key']: item for item in report['evidence']['coverage']
                         if item['direction'] == 'contract_solution'}
                self.assertEqual(verdict, facts['outcomes.succeeded']['status'])
                for key, expected in (('request_schema', schema), ('response_schemas.succeeded', schema),
                                      ('response_schemas.failed', {})):
                    self.assertEqual(('unresolved', expected), (facts[key]['status'], facts[key]['left']))
                self.assertEqual('conflicting' if verdict == 'conflicting' else 'unresolved', report['status'])
