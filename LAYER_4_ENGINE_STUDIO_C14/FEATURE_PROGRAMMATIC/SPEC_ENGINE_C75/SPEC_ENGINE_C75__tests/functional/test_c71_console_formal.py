"""Check pinned draft claims and generated contrary effects."""
import ast
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import (
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    compare_trace_values,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_1_SOURCE_ADAPTERS_C95._package__shared import (
    SpecSnapshot,
)

ROOT = next(path for path in Path(__file__).resolve().parents if (path / '_anechoic_anechoic').is_dir())
PINS = ({'path': '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/01_draft/AN-S-3333@35-draft-SPEC-COMPONENT_MANIFEST--declare-database-server-beta.md', 'atom_id': 'AN-S-3333', 'version': 35, 'status': 'draft', 'container_component': 'C67'}, {'path': '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/01_draft/AN-S-5041@1-draft-DES-SOLUTION--serve-view-sql-and-structure.md', 'atom_id': 'AN-S-5041', 'version': 1, 'status': 'draft', 'container_component': 'C71'})


def rows():
    result = []
    for pin in PINS:
        path = ROOT / pin['path']
        raw = path.read_bytes()
        carrier = parse_carrier(raw, path)
        result.append(
            {
                "source_path": pin["path"],
                "exact_ref": f"{pin['atom_id']}@{pin['version']}-draft",
                "metadata": carrier.metadata,
                "body": carrier.body,
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return result


class FormalCandidateTest(unittest.TestCase):
    def test_admission_generated_contrary_effect(self):
        self.check_claim(
            "admit_structure_projection",
            "'target': 'C71.structure_projection', 'outcome': 'committed'",
            "committed",
        )

    def test_save_generated_contrary_effect(self):
        self.check_claim('save_view_sql',
                         "'target': 'C71.view_select', 'outcome': 'validated'", 'validated')

    def test_check_generated_contrary_effect(self):
        self.check_claim(
            "check_view_sql",
            "'target': 'C71.view_select', 'outcome': 'validated'",
            "validated",
        )

    def test_run_generated_contrary_effect(self):
        self.check_claim(
            "run_view_sql",
            "'target': 'C71.view_select', 'outcome': 'validated'",
            "validated",
        )

    def check_claim(self, action, original, outcome):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        if not lean:
            self.skipTest('Lean is unavailable')
        sources = rows()
        result = verify_formal_chain(SpecSnapshot(sources), 'C71', PINS[0], solution=PINS[1], action=action, lean=lean)
        self.assertEqual('compared', result['outcome'], result)
        self.assertNotIn('conflicting', [fact['status'] for fact in result['evidence']['coverage']])
        contrary = original.replace(outcome, 'generated_contrary')
        source = sources[1]['body']
        start = source.index("action=" + repr(action))
        end = source.index('```', start)
        self.assertEqual(1, source[start:end].count(original))
        body = (
            source[:start]
            + source[start:end].replace(original, contrary, 1)
            + source[end:]
        )
        sources[1] = {
            **sources[1],
            "body": body,
            "sha256": hashlib.sha256(body.encode()).hexdigest(),
        }
        result = verify_formal_chain(
            SpecSnapshot(sources),
            "C71",
            PINS[0],
            solution=PINS[1],
            action=action,
            lean=lean,
        )
        self.assertEqual("compared", result["outcome"], result)
        expected = "unresolved" if action == "save_view_sql" else "conflicting"
        self.assertEqual(
            expected,
            result["directions"]["manifest_solution"]["status"],
            result,
        )


PIN = 'a' * 64
BINDING = {'instance_id': 'instance'}


class UnixHTTP(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__('localhost', timeout=5)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


class Client:
    def __init__(self, path):
        self.path = path

    def request(self, method, path, payload):
        connection = UnixHTTP(self.path)
        try:
            connection.request(
                method,
                path,
                json.dumps(payload),
                {"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()


def generation():
    model = json.dumps(
        {
            "model_sha256": "b" * 64,
            "binding_schema": 1,
            "modules": {"__init__.py": hashlib.sha256(b"").hexdigest()},
            "module_sources": {"__init__.py": ""},
            "module_order": [],
            "class_modules": {},
            "bindings": {},
        },
        indent=2,
    )
    structure = json.dumps(
        {
            "model_sha256": "b" * 64,
            "project": {"ref": "AN-S-1", "sha256": PIN},
            "components": {},
        },
        indent=2,
    )
    return BINDING | {
        "snapshot": {
            "manifest_sha256": PIN,
            "atoms": [{"reference": "one", "summary": "first"}],
        },
        "model": model,
        "structure": structure,
        "graph": None,
        "receipt": {
            "manifest_sha256": PIN,
            "model_sha256": "b" * 64,
            "graph_sha256": hashlib.sha256(b"null").hexdigest(),
            "model_descriptor_sha256": hashlib.sha256(
                model.encode()
            ).hexdigest(),
            "structure_sha256": hashlib.sha256(structure.encode()).hexdigest(),
        },
    }


@contextmanager
def _server(_database, *arguments):
    with TemporaryDirectory(
        prefix="ane-formal-server-", dir="/tmp"
    ) as directory:
        path = str(Path(directory).resolve() / "db.sock")
        module = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"
        env = os.environ | {
            "PYTHONPATH": str(ROOT / "LAYER_4_ENGINE_STUDIO_C14")
        }
        extensions = ROOT / ".anechoic_tmp/workbench/extensions"
        if extensions.is_dir():
            env.setdefault(
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(extensions)
            )
        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                module,
                "--socket",
                path,
                "--instance-id",
                "instance",
                "--manifest-sha256",
                PIN,
                *arguments,
            ],
            env=env,
        )
        try:
            until = time.monotonic() + 10
            while not Path(path).exists() and process.poll() is None and time.monotonic() < until:
                time.sleep(.03)
            if not Path(path).exists():
                raise AssertionError('Database server did not start')
            yield Client(path)
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=10)


def call(client, operation, arguments):
    return client.request(
        "POST",
        "/workspace",
        BINDING | {"operation": operation, "arguments": arguments},
    )


class ViewSavedValuesTest(unittest.TestCase):
    def test_saved_sql_matches_supplied_sql(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean is unavailable')
        source = (ROOT / PINS[0]['path']).read_text()
        claims = (ast.parse(text).body[0].value for text in re.findall(r'```python trace\n(.*?)\n```', source, re.S))
        for claim in claims:
            args = {
                arg.arg: ast.literal_eval(arg.value) for arg in claim.keywords
            }
            if args.get("action") == "save_view_sql":
                case = {
                    "action": args["action"],
                    "output": "succeeded",
                    **args["cases"]["succeeded"],
                }
                break
        else:
            self.fail("save_view_sql contract is missing")
        with (
            TemporaryDirectory(dir="/tmp") as directory,
            _server(
                None,
                "--project-root",
                str(Path(directory).resolve()),
                "--journal-relative",
                "control/journal",
            ) as client,
        ):
            self.assertEqual(
                200, client.request("PUT", "/generation", generation())[0]
            )
            for index, sql in enumerate(
                (
                    "SELECT 1",
                    "SELECT 'VIEW TABLE' AS label VIEW GRAPH HORIZONTAL",
                    "  -- Ignore this label: VIEW GRAPH\r\nSELECT 'préservé 🎵' AS label\r\n"
                    "VIEW /* layout */ DOC -- keep this comment  \r\n",
                )
            ):
                with self.subTest(sql=sql):
                    self.assert_saved_values(client, case, lean, sql, index)

    def assert_saved_values(self, client, case, lean, sql, index):
        opened = call(
            client,
            "workspace_open",
            {"session_id": f"formal-view-values-{index}"},
        )[1]["result"]
        view = {
            "workspace_id": opened["workspace_id"],
            "view_id": opened["active_view_id"],
        }
        updated = call(
            client, "view_update", view | {"sql": sql, "expected_revision": 0}
        )
        self.assertEqual(200, updated[0], updated[1])
        saved = call(client, 'view_save', view)
        self.assertEqual(200, saved[0], saved[1])
        loaded = call(
            client,
            "query_load",
            {"reference": saved[1]["result"]["saved_query_id"]},
        )
        self.assertEqual(200, loaded[0], loaded[1])
        events = [
            {"event": "view_requested", "detail": {"authored_sql": sql}},
            {
                "event": "view_saved",
                "detail": {"authored_sql": loaded[1]["result"]["sql"]},
            },
        ]
        report = compare_trace_values(case, events, lean=lean)
        self.assertEqual('matched', report['status'], report)
