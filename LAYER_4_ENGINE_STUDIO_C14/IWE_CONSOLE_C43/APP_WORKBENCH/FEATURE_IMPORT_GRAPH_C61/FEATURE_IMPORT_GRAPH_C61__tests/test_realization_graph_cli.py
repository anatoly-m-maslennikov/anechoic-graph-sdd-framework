"""Exercise the provider through its process boundary."""

import json

from FEATURE_IMPORT_GRAPH_C61__tests__shared import run_provider


def test_graph_rows_are_complete_and_deterministic(tmp_path):
    package = tmp_path / "sample"
    tests = package / "sample__tests"
    tests.mkdir(parents=True)
    (package / "main.py").write_text("import sample.helper\n", encoding="utf-8")
    (package / "helper.py").write_text("value = 1\n", encoding="utf-8")
    (tests / "test_main.py").write_text("import sample.main\n", encoding="utf-8")
    config = {"python_roots": ["."]}
    first = run_provider(tmp_path, config)
    assert first.returncode == 0, first.stderr
    assert first.stdout == run_provider(tmp_path, config).stdout
    graph = json.loads(first.stdout)
    assert set(graph) == {"nodes", "occurrences", "edges", "test_edges", "read_issues", "state_effect_findings"}
    assert ["package:local:sample/sample__tests", "package", "python", "sample/sample__tests", None, None,
            "Test Package"] in graph["nodes"]
    assert ["package:local:sample/sample__tests", "package:local:sample"] in graph["test_edges"]
    assert any(row[3] == "sample.helper" and row[6] == "internal" for row in graph["occurrences"])
    assert graph["edges"] and not graph["read_issues"]


def test_rejects_invalid_options(tmp_path):
    for config in ({"unknown": True}, {"include": ["../outside.py"]},
                   {"python_image_imports": {"main.py": ["not-valid"]}}):
        result = run_provider(tmp_path, config)
        assert result.returncode != 0
        assert not result.stdout


def test_state_findings_are_unresolved_when_lean_is_unavailable(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "")
    (tmp_path / "main.py").write_text("def run():\n    return 1\n")
    result = run_provider(tmp_path, {})
    assert result.returncode == 0, result.stderr
    findings = json.loads(result.stdout)["state_effect_findings"]
    assert findings == [["module:main.py", "main.py", "python", "<module>", 1, None,
                         "unresolved", False, "[]", "[]", "Lean executable unavailable on PATH"]]


def test_component_test_edge_uses_declared_structure(tmp_path):
    control = tmp_path / "_control"
    control.mkdir()
    (control / "_SPEC").mkdir()
    (control / "Widget_C9").mkdir()
    component = tmp_path / "Widget"
    tests = component / "Widget__tests"
    tests.mkdir(parents=True)
    (tests / "test_widget.py").write_text("pass\n")
    (component / "child").mkdir()
    (component / "child" / "main.py").write_text("pass\n")
    structure = {"model_sha256": "model", "project": {"ref": "AN-S-1", "sha256": "hash"},
                 "components": {"C9": {"parent": "C00", "ref": "AN-S-2", "sha256": "hash",
                                         "fields": {"name": "Widget"},
                                         "source_path": "_SPEC/spec.md"}}, "packages": {}}
    result = run_provider(tmp_path, {"python_roots": ["."]}, structure=structure, control_root="_control")
    assert result.returncode == 0, result.stderr
    graph = json.loads(result.stdout)
    assert ["package:local:Widget/Widget__tests", "C9"] in graph["test_edges"]
    assert not any(row[0] == "C9" for row in graph["nodes"])
