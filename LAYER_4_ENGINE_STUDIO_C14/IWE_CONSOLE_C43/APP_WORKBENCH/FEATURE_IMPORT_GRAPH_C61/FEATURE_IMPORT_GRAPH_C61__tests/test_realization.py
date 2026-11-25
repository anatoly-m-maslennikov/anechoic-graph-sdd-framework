from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
    capture, relevant_change, resolve_realization, run_graph_build,
)


_GRAPH_CLI = "IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.realization_graph_cli"


class RealizationTests(unittest.TestCase):
    def _run_graph(self, request, **options):
        stdin = StringIO(json.dumps(request))
        stdout, stderr = StringIO(), StringIO()
        with patch.object(sys, "stdin", stdin), redirect_stdout(stdout), redirect_stderr(stderr):
            status = run_graph_build(**options)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_watcher_replay_uses_one_source_capture(self):
        root = self._temporary_project()
        (root / "main.py").write_text("import pathlib\n")
        request = {"root": str(root), "config": {}}
        status, expected, stderr = self._run_graph(request)
        self.assertEqual(0, status, stderr)

        def change_other_files(*args):
            (root / ".git" / "unrelated").write_text("transient\n")
            (root / ".anechoic_runtime").mkdir()
            return {}

        with (patch(f"{_GRAPH_CLI}.capture", wraps=capture) as capture_sources,
              patch(f"{_GRAPH_CLI}._manifests") as capture_manifests):
            status, actual, stderr = self._run_graph(request, derive_rows=change_other_files, watcher_replay=True)
        self.assertEqual(0, status, stderr)
        self.assertEqual(json.loads(expected), json.loads(actual))
        capture_sources.assert_called_once_with(root, None, ())
        capture_manifests.assert_not_called()

    def test_watcher_replay_reports_git_ignore_changes_without_external_paths(self):
        root = self._temporary_project()
        (root / "main.py").write_text("import pathlib\n")
        excluded = root / ".git" / "info" / "exclude"

        def change(*args):
            excluded.write_text("main.py\n")
            return {}, []

        with patch(f"{_GRAPH_CLI}._state_projection", change):
            status, stdout, stderr = self._run_graph({"root": str(root), "config": {}}, watcher_replay=True)
        self.assertEqual(1, status)
        self.assertEqual("", stdout)
        self.assertNotIn(str(root), stderr)
        report = json.loads(stderr)
        self.assertEqual("realization_graph_inputs_changed", report["code"])
        self.assertEqual({"resolution_inputs": {"change": "changed", "fields": ["stat_signature"]}},
                         report["details"])

    def test_consistency_failure_reports_both_maps_without_rescans(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        source, dependency = root / "main.py", root / "pyproject.toml"
        source.write_text("import os\n")
        dependency.write_text("[tool]\n")

        def change(*args):
            source.write_text("import pathlib\n")
            dependency.write_text("[tool.fixture]\n")
            return {}, []

        with (patch(f"{_GRAPH_CLI}._state_projection", change),
              patch(f"{_GRAPH_CLI}.capture", wraps=capture) as capture_sources):
            status, stdout, stderr = self._run_graph({"root": str(root), "config": {}})
        self.assertEqual(1, status)
        self.assertEqual(2, capture_sources.call_count)
        self.assertEqual("", stdout)
        self.assertNotIn(str(root), stderr)
        report = json.loads(stderr)
        self.assertEqual(("ERROR", "realization_graph_inputs_changed"), (report["severity"], report["code"]))
        self.assertEqual({
            "resolution_inputs": {"change": "changed", "path": "pyproject.toml", "fields": ["stat_signature"]},
            "sources": {"change": "changed", "path": "main.py", "fields": ["signature", "imports"]},
        }, report["details"])

    def test_source_change_reports_safe_paths_only(self):
        cases = (("secret-name.py", {"change": "removed"}), ("added.py", {"change": "added", "path": "added.py"}))
        for name, details in cases:
            with self.subTest(name=name), TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                path = root / name
                if details["change"] == "removed":
                    path.write_text("import os\n")

                def change(*args):
                    if path.exists():
                        path.unlink()
                    else:
                        path.write_text("import os\n")
                    return {}, []

                with patch(f"{_GRAPH_CLI}._state_projection", change):
                    status, stdout, stderr = self._run_graph({"root": str(root), "config": {}})
                self.assertEqual((1, ""), (status, stdout))
                self.assertEqual(details, json.loads(stderr)["details"]["sources"])

    def _temporary_project(self):
        tmp_path = Path(self.enterContext(TemporaryDirectory())).resolve()
        subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
        return tmp_path

    def test_relative_imports_use_enclosing_root_for_namespace_packages(self):
        root = self._temporary_project()
        for name, content in {
            "namespace/release/images.py": "from .identity import VALUE\n",
            "namespace/release/identity.py": "VALUE = 1\n",
            "namespace/release/tests/fixture.py": (
                "from ..images import VALUE\nfrom ....outside import VALUE\n"),
            "outside.py": "VALUE = 1\n",
        }.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        _, occurrences, _, _, _ = resolve_realization(
            root, capture(root, None), ("namespace/release", "."))
        found = {(row[1], row[3]): (row[2], row[6]) for row in occurrences}
        assert found[("module:namespace/release/images.py", ".identity")] == (
            "module:namespace/release/identity.py", "internal")
        assert found[("module:namespace/release/tests/fixture.py", "..images")] == (
            "module:namespace/release/images.py", "internal")
        assert found[("module:namespace/release/tests/fixture.py", "....outside")] == (
            None, "unresolved")

    def test_test_package_flat_imports_prefer_local_directory(self):
        root = self._temporary_project()
        for name, content in {
            "helper.py": "",
            "pkg/pkg__tests/test_one.py": "import helper\nfrom helper import nested\nimport local_only\nfrom . import relative\nimport ambiguous\n",
            "pkg/pkg__tests/helper.py": "import local_only\n",
            "helper/nested.py": "",
            "pkg/pkg__tests/local_only.py": "",
            "pkg/pkg__tests/ambiguous.py": "",
            "pkg/pkg__tests/ambiguous/nested.py": "",
            "pkg/pkg__tests/relative.py": "",
            "pkg/other__tests/test_two.py": "import local_only\n",
            "pkg/other__tests/local_only.py": "",
            "pkg/production.py": "import local_only\nimport helper\n",
        }.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        _, occurrences, _, _, _ = resolve_realization(root, capture(root, None))
        found = {(row[1], row[3]): (row[2], row[6]) for row in occurrences}
        assert found[("module:pkg/pkg__tests/test_one.py", "helper")] == (
            "module:pkg/pkg__tests/helper.py", "internal")
        assert found[("module:pkg/pkg__tests/test_one.py", "ambiguous")] == (None, "ambiguous")
        assert found[("module:pkg/pkg__tests/helper.py", "local_only")] == (
            "module:pkg/pkg__tests/local_only.py", "internal")
        assert found[("module:pkg/pkg__tests/test_one.py", ".")] == (
            "module:pkg/pkg__tests/relative.py", "internal")
        assert found[("module:pkg/other__tests/test_two.py", "local_only")] == (None, "unresolved")
        assert found[("module:pkg/production.py", "local_only")] == (None, "unresolved")
        assert found[("module:pkg/production.py", "helper")] == (None, "ambiguous")

    def test_direct_test_packages_follow_source_inventory(self):
        tmp_path = self._temporary_project()
        for name in ("pkg/__init__.py", "pkg/pkg__tests/test_one.py", "pkg/other__tests/test_two.py",
                     "other/pkg__tests/test_three.py", "pkg/pkg__tests/nested/test_four.py"):
            path = tmp_path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("pass\n")
        sources = capture(tmp_path, None)
        nodes, occurrences, edges, tests, _ = resolve_realization(tmp_path, sources)
        packages = {node[0]: node for node in nodes if node[1] == "package"}
        assert ("package:local:pkg/pkg__tests", "package:local:pkg") in tests
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]
        assert packages["package:local:pkg/pkg__tests"][1] == "package"
        assert not occurrences and not edges
        assert relevant_change(tmp_path, [{"new_path": "pkg/pkg__tests", "old_path": None}], {})

    def test_installed_import_names_use_metadata_and_local_precedence(self):
        root = self._temporary_project()
        (root / "pyproject.toml").write_text('[project]\nname = "my-project"\n')
        (root / "local_name.py").write_text("")
        (root / "main.py").write_text(
            "import yaml\nimport PIL\nimport pil\nimport local_name\n"
            "import own_alias\nimport unknown_alias\nimport json\n")
        installed = {"yaml": ["PyYAML"], "PIL": ["Pillow"],
                     "local_name": ["other"], "own_alias": ["my_project", "other"]}
        with patch("IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.resolution.metadata.packages_distributions",
                   return_value=installed):
            _, occurrences, _, _, _ = resolve_realization(root, capture(root, None))
        found = {row[3]: (row[2], row[6]) for row in occurrences}
        assert found["yaml"] == ("package:external:yaml", "external")
        assert found["PIL"] == ("package:external:PIL", "external")
        assert found["pil"] == (None, "unresolved")
        assert found["local_name"] == ("module:local_name.py", "internal")
        assert found["own_alias"] == (None, "unresolved")
        assert found["unknown_alias"] == (None, "unresolved")
        assert found["json"][1] == "external"

    def test_mixed_package_and_import_pairs(self):
        root = self._temporary_project()
        for name, content in {"pkg/package.json": '{"name":"pkg"}',
                              "pkg/a.py": "import other.b\n", "pkg/app.js": "",
                              "pkg/pkg__tests/test.py": "", "pkg/pkg__tests/test.js": "",
                              "pkg/pkg__tests/package.json": '{"name":"tests"}',
                              "other/b.py": ""}.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        nodes, _, edges, tests, _ = resolve_realization(root, capture(root, None))
        packages = [node for node in nodes if node[1] == "package" and node[3] == "pkg"]
        assert len(packages) == 1
        node_by_key = {node[0]: node for node in nodes}
        assert node_by_key["module:pkg/app.js"][5] == packages[0][0] == node_by_key["module:pkg/a.py"][5]
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]
        assert {(source, target) for source, target, _, _ in edges} == {
            ("module:pkg/a.py", "module:other/b.py"), ("module:pkg/a.py", "package:local:other"),
            ("package:local:pkg", "module:other/b.py"), ("package:local:pkg", "package:local:other"),
        }
        (root / "pkg/a.py").unlink()
        (root / "pkg/pkg__tests/test.py").unlink()
        nodes, _, _, tests, _ = resolve_realization(root, capture(root, None))
        assert [node[0] for node in nodes if node[1] == "package" and node[3] == "pkg"] == ["package:local:pkg"]
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]

    def test_executables_define_packages_without_becoming_python_import_targets(self):
        root = self._temporary_project()
        (root / "main.py").write_text("import tool\nimport namespace\n")
        (root / "namespace/nested").mkdir(parents=True)
        (root / "namespace/nested/library.py").write_text("pass\n")
        for name, body in (("tool/source.rs", "fn main() {}"), ("script/run", "#!/usr/bin/env lua\n"),
                           ("binary/run", "\x00")):
            path = root / name
            path.parent.mkdir()
            path.write_text(body)
        (root / "binary/run").chmod(0o755)
        sources = capture(root, None)
        nodes, occurrences, edges, _, _ = resolve_realization(root, sources)
        assert {node[3] for node in nodes if node[1] == "package"} == {
            "tool", "script", "binary", "namespace/nested",
        }
        assert [occurrence[6] for occurrence in occurrences] == ["unresolved", "internal"]
        assert [node[1] for node in nodes if node[3] == "namespace"] == ["namespace"]
        assert len(edges) == 1

    def test_non_executable_carrier_is_excluded_when_access_reports_executable(self):
        root = self._temporary_project()
        carrier = root / "carrier 2.md"
        carrier.write_text("# Generated carrier\n")
        carrier.chmod(0o600)
        executable = root / "run"
        executable.write_text("binary content\n")
        executable.chmod(0o755)
        with patch("os.access", return_value=True):
            sources = capture(root, None)
        assert "carrier 2.md" not in sources
        assert sources["run"].language == "executable"

    def test_visible_control_tree_is_excluded_from_realization(self):
        root = self._temporary_project()
        control = root / "_anechoic_example"
        control.mkdir()
        (control / "fixture.py").write_text("pass\n")
        (root / "implementation.py").write_text("pass\n")
        assert set(capture(root, None)) == {"implementation.py"}

    def test_read_error_is_retried_on_next_capture_without_stat_change(self):
        root = self._temporary_project()
        path = root / "a.py"
        path.write_text("import os\n")
        with patch.object(Path, "read_bytes", side_effect=PermissionError("denied")) as read:
            failed = capture(root, None)
        assert read.call_count == 1
        assert failed["a.py"].status == "read_error"
        assert failed["a.py"].error_message == "denied"
        recovered = capture(root, failed, changes=[{"new_path": "other.py", "old_path": None}])
        assert recovered["a.py"].status == "parsed"
        assert recovered["a.py"].signature == failed["a.py"].signature
        assert recovered["a.py"].error_message is None
        path.unlink()
        assert capture(root, failed, changes=[{"new_path": None, "old_path": "a.py"}]) == {}
