"""Run the generated C45 HTTP contract checks from the repository root.

PYTHONPATH=LAYER_4_ENGINE_STUDIO_C14 \
  HYPOTHESIS_STORAGE_DIRECTORY="$PWD/.anechoic_tmp/python/hypothesis" \
  UV_PROJECT_ENVIRONMENT="$PWD/.anechoic_tmp/python/http-contract-tests" \
  uv run --project LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine \
  --locked --no-env-file --group http-contract-tests python -B -m pytest -q \
  -p no:cacheprovider \
  LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/test_generated_http.py
"""
import json
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import httpx
import pytest
import schemathesis
import toon_format
from hypothesis import assume, given, seed, settings
from jsonschema import Draft202012Validator
from schemathesis.checks import not_a_server_error
from schemathesis.core.failures import FailureGroup
from schemathesis.openapi.checks import JsonSchemaError
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    export_openapi,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import (
    load_manifest,
)

from ._package__shared import C45_QUERY_RUN_PIN

HERE = Path(__file__).parent
ROOT = Path(__file__).resolve().parents[5]
BRIDGE = ROOT / (
    "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/"
    "FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests/"
    "generated_http_server.py"
)
PIN = {"path": "openapi_manifest.md", "atom_id": "AN-S-999999", "version": 1,
       "status": "draft", "container_component": "C45"}
SQL = "SELECT 1 AS value UNION ALL SELECT 2 AS value ORDER BY value"
CSV_ARGUMENTS = {
    "sql": SQL, "page_size": 1, "result_delivery": "file",
    "result_format": "csv",
}
RESULT_DIRECTORY = Path(".anechoic_tmp/workbench/query_results")
DOCUMENT = export_openapi(load_manifest(HERE, "C45", PIN))
OPERATION = schemathesis.openapi.from_dict(DOCUMENT)["/tools"]["post"]
REQUEST = DOCUMENT["paths"]["/tools"]["post"]["requestBody"]["content"][
    "application/json"]["schema"]
ARGUMENTS = REQUEST["properties"]["arguments"]

ARG_DOCUMENT = json.loads(json.dumps(DOCUMENT))
ARG_DOCUMENT["paths"]["/tools"]["post"]["requestBody"]["content"][
    "application/json"]["schema"] = ARGUMENTS
ARG_OPERATION = schemathesis.openapi.from_dict(ARG_DOCUMENT)["/tools"]["post"]


@pytest.fixture(scope="module")
def bridge():
    process = subprocess.Popen(
        [sys.executable, "-B", str(BRIDGE)], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, text=True, env=os.environ.copy(),
    )
    yield process
    process.stdin.close()
    process.wait(timeout=10)
    assert process.returncode == 0


def bridge_response(line):
    result = json.loads(line)
    response = httpx.Response(
        result["status"], content=result["body"], headers=result["headers"],
        request=httpx.Request("POST", "http://test/tools"),
    )
    response.elapsed = timedelta()
    return response


def invoke(bridge, body, mode="normal"):
    bridge.stdin.write(json.dumps({"body": body, "mode": mode}) + "\n")
    bridge.stdin.flush()
    return bridge_response(bridge.stdout.readline())


def envelope(arguments):
    return {"name": "query_run", "arguments": arguments, "instance_id": "test",
            "session_id": None, "public_base_url": None,
            "asserted_project_root": None}


def test_exact_outcomes_and_bad_response(bridge):
    body = envelope({"sql": "SELECT 1"})
    for payload, mode, status in ((body, "normal", 200),
                                  (envelope({}), "normal", 400),
                                  (body, "failure", 500)):
        response = invoke(bridge, payload, mode)
        assert response.status_code == status
        OPERATION.Case(
            body=payload, media_type="application/json"
        ).validate_response(response, excluded_checks=[not_a_server_error])
    bad = httpx.Response(
        200,
        json={"unexpected": True},
        request=httpx.Request("POST", "http://test/tools"),
    )
    bad.elapsed = timedelta()
    with pytest.raises(FailureGroup):
        OPERATION.Case(
            body=body, media_type="application/json"
        ).validate_response(bad)


@seed(4001)
@settings(max_examples=20, deadline=None, database=None)
@given(
    case=ARG_OPERATION.as_strategy(
        generation_mode=schemathesis.GenerationMode.POSITIVE
    )
)
def test_generated_positive(bridge, case):
    body = envelope(case.body)
    assert Draft202012Validator(REQUEST).is_valid(body)
    response = invoke(bridge, body)
    assert response.status_code == 200
    OPERATION.Case(body=body, media_type="application/json").validate_response(
            response, excluded_checks=[not_a_server_error])


@seed(4002)
@settings(max_examples=20, deadline=None, database=None)
@given(
    case=ARG_OPERATION.as_strategy(
        generation_mode=schemathesis.GenerationMode.NEGATIVE
    )
)
def test_generated_negative(bridge, case):
    assume(isinstance(case.body, dict))
    body = envelope(case.body)
    assert not Draft202012Validator(REQUEST).is_valid(body)
    response = invoke(bridge, body)
    assert response.status_code == 400
    OPERATION.Case(body=body, media_type="application/json").validate_response(
            response, excluded_checks=[not_a_server_error])


@pytest.fixture(scope="module")
def governed_operation():
    manifest = load_manifest(ROOT, "C45", C45_QUERY_RUN_PIN)
    document = export_openapi(manifest, action="query_run")
    return schemathesis.openapi.from_dict(document)["/tools"]["post"]


def provider_responses(root, calls):
    messages = "".join(
        json.dumps({"body": body, "mode": mode}) + "\n" for body, mode in calls
    )
    process = subprocess.run(
        [sys.executable, "-B", str(BRIDGE), str(root)],
        input=messages,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    return [bridge_response(line) for line in process.stdout.splitlines()]


@pytest.fixture(scope="module")
def provider_results(tmp_path_factory):
    root = tmp_path_factory.mktemp("http-provider").resolve()
    cases = {
        "stale_binding": (envelope({"sql": SQL}), "stale_binding"),
        "matrix": (envelope({
            "sql": SQL, "page_size": 1, "result_delivery": "inline",
        }), "normal"),
        "file": (envelope(CSV_ARGUMENTS), "normal"),
        "bookmark_toon": (envelope({
            **CSV_ARGUMENTS, "result_format": "toon", "save": True,
            "name": "HTTP Bookmark",
        }), "normal"),
        "query_error": (envelope({"sql": "SELECT missing_column"}), "normal"),
        "nan": (envelope({"sql": "SELECT 'NaN'::DOUBLE"}), "normal"),
        "tool_input_invalid": (envelope({}), "normal"),
        "internal": (envelope({"sql": SQL}), "failure"),
    }
    responses = provider_responses(root, cases.values())
    return root, {
        key: (body, response)
        for (key, (body, _)), response in zip(
            cases.items(), responses, strict=True
        )
    }


def validate_provider(operation, body, response):
    operation.Case(body=body, media_type="application/json").validate_response(
        response, excluded_checks=[not_a_server_error]
    )


def test_governed_matrix(governed_operation, provider_results):
    _, results = provider_results
    body, response = results["matrix"]
    assert response.status_code == 200
    validate_provider(governed_operation, body, response)
    result = response.json()["result"]
    assert result["text"] is None
    value = result["value"]
    assert value["columns"] == [{"name": "value", "type": "INTEGER",
                                 "has_values": True}]
    assert value["rows"] == [[1]]
    assert value["has_more"] is True and value["row_count"] == 2


@pytest.mark.parametrize("case", ["file", "bookmark_toon"])
def test_governed_result_file(governed_operation, provider_results, case):
    root, results = provider_results
    body, response = results[case]
    assert response.status_code == 200
    validate_provider(governed_operation, body, response)
    result = response.json()["result"]
    assert result["text"] is None
    value = result["value"]
    assert "rows" not in value and "csv" not in value
    assert value["page_size"] == 1 and value["has_more"] is True
    descriptor = value["result_file"]
    assert descriptor["format"] == body["arguments"]["result_format"]
    assert descriptor["row_count"] == 2
    assert descriptor["has_more"] is False
    relative = Path(descriptor["path"])
    assert relative.parent == RESULT_DIRECTORY
    if case == "file":
        assert (root / relative).read_bytes() == b'"value"\r\n"1"\r\n"2"\r\n'
        return
    assert toon_format.loads(
        (root / relative).read_text(encoding="utf-8")
    ) == {
        "columns": ["value"],
        "rows": [[1], [2]],
    }
    assert value["kind"] == "query" and value["name"] == "HTTP Bookmark"
    (journal,) = root.glob(
        "_anechoic_test/_journal/workbench-saved-items-*.ndjson"
    )
    saved = json.loads(journal.read_bytes())
    assert saved["saved_query_id"] == value["saved_query_id"]
    assert saved["sql"] == SQL


def test_governed_partial_export(governed_operation, tmp_path):
    root = tmp_path.resolve()
    outside = root / "outside"
    outside.mkdir()
    target = root / RESULT_DIRECTORY
    target.parent.mkdir(parents=True)
    target.symlink_to(outside, target_is_directory=True)
    body = envelope(CSV_ARGUMENTS)
    response, = provider_responses(root, [(body, "normal")])
    assert response.status_code == 200
    validate_provider(governed_operation, body, response)
    result = response.json()["result"]
    assert result["text"] is None
    value = result["value"]
    assert value["outcome"] == "partial"
    assert "symlinked directory" in value["export_error"]
    assert "result_file" not in value
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize(
    ("case", "code", "status", "outcome"),
    [
        ("stale_binding", "tool_registry_stale", 200, "rejected"),
        ("query_error", "query_error", 200, "failed"),
        ("nan", "query_error", 200, "failed"),
        ("tool_input_invalid", "tool_input_invalid", 400, "rejected"),
        ("internal", "internal", 500, "failed"),
    ],
)
def test_governed_error(
    governed_operation, provider_results, case, code, status, outcome
):
    _, results = provider_results
    body, response = results[case]
    assert response.status_code == status
    validate_provider(governed_operation, body, response)
    error = response.json()["error"]
    assert error["code"] == code
    assert error["tool_result"]["outcome"] == outcome
    assert error["tool_result"]["diagnostics"]
    if case == "nan":
        assert "NaN or infinity" in error["message"]
    if code == "internal":
        assert error["message"] == "Backend Tool operation failed"
        assert "private failure" not in response.text


@pytest.mark.parametrize(
    ("status", "case"),
    [
        (200, "tool_input_invalid"),
        (400, "internal"),
        (500, "tool_input_invalid"),
    ],
)
def test_governed_wrong_status_body(
    governed_operation, provider_results, status, case
):
    _, results = provider_results
    body, response = results[case]
    wrong = httpx.Response(
        status, json=response.json(), request=response.request
    )
    wrong.elapsed = timedelta()
    with pytest.raises(FailureGroup) as errors:
        validate_provider(governed_operation, body, wrong)
    assert errors.group_contains(JsonSchemaError)


def test_governed_mixed_result_carriers(governed_operation, provider_results):
    _, results = provider_results
    body, response = results["file"]
    wrong_body = response.json()
    wrong_body["result"]["value"]["rows"] = [[1]]
    wrong = httpx.Response(200, json=wrong_body, request=response.request)
    wrong.elapsed = timedelta()
    with pytest.raises(FailureGroup) as errors:
        validate_provider(governed_operation, body, wrong)
    assert errors.group_contains(JsonSchemaError)
