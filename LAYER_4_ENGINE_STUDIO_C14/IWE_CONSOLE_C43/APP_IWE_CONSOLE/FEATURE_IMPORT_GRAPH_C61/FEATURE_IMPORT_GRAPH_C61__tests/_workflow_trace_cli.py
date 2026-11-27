import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
    FEATURE_IMPORT_GRAPH_C61__tests._workflow_trace_fixtures import (
        correlation_machine, machine,
    )  # fmt: skip


def _workflows():
    workflows = []
    for action in ("run", "check"):
        config = machine()
        config["states"]["start"]["on"]["NEXT"][0]["guard"]["params"][
            "outcome"
        ] = action
        workflows.append(
            f"```python\ncomponent_workflow(component='C61', "
            f"action={action!r}, machine={config!r})\n```"
        )
    return workflows


def render_case(self):
    workflows = _workflows()
    with TemporaryDirectory() as directory:
        path = Path(directory) / "solution.md"
        path.write_text(
            "## Claim\n\n### Formal Claim\n\n" + "\n\n".join(workflows),
            encoding="utf-8",
        )
        command = [
            sys.executable,
            "-B",
            "-m",
            "IWE_CONSOLE_C43.APP_IWE_CONSOLE."
            "FEATURE_IMPORT_GRAPH_C61.workflow_spec",
            str(path),
            "render",
        ]
        selected = subprocess.run(
            [*command, "--action", "check"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, selected.returncode, selected.stderr)
        self.assertIn("outcome=#quot;check#quot;", selected.stdout)
        for arguments, error in (
            ([], "Specify --action"),
            (["--action", "missing"], "Unknown Solution action"),
        ):
            with self.subTest(arguments=arguments):
                rejected = subprocess.run(
                    [*command, *arguments],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(3, rejected.returncode)
                self.assertIn(error, rejected.stderr)


def _rows(generation, reply, retry):
    details = {"reply_id": reply, "sql": "current"}
    if generation is not None:
        details["generation"] = generation
    events = [
        ("trigger", "start", None, {"id": "r1", "generation": 2}),
        ("effect", "retry", None, {"id": retry}),
        ("output", "finish", "ok", details),
    ]
    rows = [
        [
            "recorded",
            "C61",
            "run",
            seq,
            kind,
            name,
            None,
            outcome,
            detail,
        ]
        for seq, (kind, name, outcome, detail) in enumerate(events)
    ]
    return rows


def _check_cases(self, command):
    columns = [
        "run_id",
        "component",
        "action",
        "sequence",
        "kind",
        "name",
        "target",
        "outcome",
        "detail",
    ]
    for generation, reply, retry, status, index in (
        (2, "r1", "r1", "matched", None),
        (3, "r1", "r1", "different", 2),
        (2, "r2", "r1", "different", 2),
        (2, "r2", "r2", "different", 1),
        (None, "r1", "r1", "different", 2),
    ):
        rows = _rows(generation, reply, retry)
        with self.subTest(generation=generation, reply=reply, retry=retry):
            run = subprocess.run(
                command,
                input=json.dumps({"columns": columns, "rows": rows}),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            self.assertEqual(
                int(status == "different"),
                run.returncode,
                run.stderr or run.stdout,
            )
            result = json.loads(run.stdout)
            self.assertEqual(status, result["status"])
            self.assertEqual(
                index, (result["firstDifference"] or {}).get("index")
            )


def check_case(self):
    config = correlation_machine()
    with TemporaryDirectory() as directory:
        path = Path(directory) / "solution.md"
        path.write_text(
            "## Claim\n\n### Formal Claim\n\n```python\n"
            f"component_workflow(component='C61', action='run', "
            f"machine={config!r})\n```\n",
            encoding="utf-8",
        )
        command = [
            sys.executable,
            "-B",
            "-m",
            "IWE_CONSOLE_C43.APP_IWE_CONSOLE."
            "FEATURE_IMPORT_GRAPH_C61.workflow_spec",
            str(path),
            "check",
            "-",
        ]
        _check_cases(self, command)
