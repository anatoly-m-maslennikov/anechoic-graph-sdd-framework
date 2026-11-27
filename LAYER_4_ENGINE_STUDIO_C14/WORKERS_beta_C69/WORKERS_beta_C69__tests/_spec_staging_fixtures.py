"""Fixtures for Spec staging tests."""

import json
import sys
from unittest.mock import patch


def staging_client(calls, staged):
    class Response:
        def __init__(self, value):
            self.value = value

        def raise_for_status(self):
            pass

        def json(self):
            return {"result": self.value}

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def put(self, path, json):
            calls.append((path, json))
            return Response({"snapshot_id": "snap"})

        def get(self, path, params):
            calls.append((path, params))
            return Response({"snapshot_id": "snap", "rows": [staged]})

    return Client


def _snapshot_raw():
    row = {
        "source_path": "control/model.md",
        "exact_ref": "AN-S-1@1",
        "metadata": {},
        "body": "body",
        "sha256": "a" * 64,
    }
    raw = {
        "snapshot_id": "snap",
        "spec_rows": [row],
        "manifest_path": "manifest.md",
        "rows": [
            {
                **{k: row[k] for k in ("exact_ref", "metadata", "body")},
                "source_path": "model.md",
            }
        ],
        "structure_alias_issues": [
            {
                "relative_path": "control/AN-S-2-SPEC-OTHER--x.md",
                "template": "new_component",
            }
        ],
    }
    return raw


def snapshot_fixture(compiler):
    raw = _snapshot_raw()
    observed = []

    def admit(args, structure, *, compile_snapshot):
        payload = json.load(sys.stdin)
        observed.append(payload["rows"])
        with patch.object(
            compiler, "compile_structure_rows", return_value="structure"
        ) as compile_rows:
            observed.append(
                compile_snapshot(
                    args,
                    None,
                    payload["spec_rows"],
                    payload["manifest_path"],
                )
            )
        assert (
            compile_rows.call_args.kwargs["alias_issues"]
            == raw["structure_alias_issues"]
        )
        print(json.dumps({"structure": "structure"}))

    return raw, observed, admit
