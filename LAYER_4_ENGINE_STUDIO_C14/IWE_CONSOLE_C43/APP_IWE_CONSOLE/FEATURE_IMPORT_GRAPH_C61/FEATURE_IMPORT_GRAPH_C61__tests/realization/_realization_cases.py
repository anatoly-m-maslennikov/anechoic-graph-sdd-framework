from unittest.mock import patch

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
    SOURCE_CAPTURE.SOURCE_CAPTURE__shared import capture  # fmt: skip
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
    SOURCE_CAPTURE.SOURCE_CAPTURE__shared import relevant_change  # fmt: skip
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
    RESOLUTION.RESOLUTION__shared import resolve_realization  # fmt: skip


class RealizationCases:
    def test_relative_imports_use_enclosing_root_for_namespace_packages(self):
        root = self._temporary_project()
        for name, content in {
            "namespace/release/images.py": "from .identity import VALUE\n",
            "namespace/release/identity.py": "VALUE = 1\n",
            "namespace/release/tests/fixture.py": (
                "from ..images import VALUE\nfrom ....outside import VALUE\n"
            ),
            "outside.py": "VALUE = 1\n",
        }.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        _, occurrences, _, _, _ = resolve_realization(
            root, capture(root, None), ("namespace/release", ".")
        )
        found = {(row[1], row[3]): (row[2], row[6]) for row in occurrences}
        assert found[("module:namespace/release/images.py", ".identity")] == (
            "module:namespace/release/identity.py",
            "internal",
        )
        assert found[
            ("module:namespace/release/tests/fixture.py", "..images")
        ] == ("module:namespace/release/images.py", "internal")
        assert found[
            ("module:namespace/release/tests/fixture.py", "....outside")
        ] == (None, "unresolved")

    def test_test_package_flat_imports_prefer_local_directory(self):
        root = self._temporary_project()
        self._write_flat_import_fixtures(root)
        _, occurrences, _, _, _ = resolve_realization(
            root, capture(root, None)
        )
        found = {(row[1], row[3]): (row[2], row[6]) for row in occurrences}
        assert found[("module:pkg/pkg__tests/test_one.py", "helper")] == (
            "module:pkg/pkg__tests/helper.py",
            "internal",
        )
        assert found[("module:pkg/pkg__tests/test_one.py", "ambiguous")] == (
            None,
            "ambiguous",
        )
        assert found[("module:pkg/pkg__tests/helper.py", "local_only")] == (
            "module:pkg/pkg__tests/local_only.py",
            "internal",
        )
        assert found[("module:pkg/pkg__tests/test_one.py", ".")] == (
            "module:pkg/pkg__tests/relative.py",
            "internal",
        )
        assert found[
            ("module:pkg/other__tests/test_two.py", "local_only")
        ] == (None, "unresolved")
        assert found[("module:pkg/production.py", "local_only")] == (
            None,
            "unresolved",
        )
        assert found[("module:pkg/production.py", "helper")] == (
            None,
            "ambiguous",
        )

    def _write_flat_import_fixtures(self, root):
        for name, content in {
            "helper.py": "",
            "pkg/pkg__tests/test_one.py": (
                "import helper\nfrom helper import nested\n"
                "import local_only\nfrom . import relative\n"
                "import ambiguous\n"
            ),
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

    def test_direct_test_packages_follow_source_inventory(self):
        tmp_path = self._temporary_project()
        for name in (
            "pkg/__init__.py",
            "pkg/pkg__tests/test_one.py",
            "pkg/other__tests/test_two.py",
            "other/pkg__tests/test_three.py",
            "pkg/pkg__tests/nested/test_four.py",
        ):
            path = tmp_path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("pass\n")
        sources = capture(tmp_path, None)
        nodes, occurrences, edges, tests, _ = resolve_realization(
            tmp_path, sources
        )
        packages = {node[0]: node for node in nodes if node[1] == "package"}
        assert ("package:local:pkg/pkg__tests", "package:local:pkg") in tests
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]
        assert packages["package:local:pkg/pkg__tests"][1] == "package"
        assert not occurrences and not edges
        assert relevant_change(
            tmp_path, [{"new_path": "pkg/pkg__tests", "old_path": None}], {}
        )

    def test_installed_import_names_use_metadata_and_local_precedence(self):
        root = self._temporary_project()
        (root / "pyproject.toml").write_text(
            '[project]\nname = "my-project"\n'
        )
        (root / "local_name.py").write_text("")
        (root / "main.py").write_text(
            "import yaml\nimport PIL\nimport pil\nimport local_name\n"
            "import own_alias\nimport unknown_alias\nimport json\n"
        )
        installed = {
            "yaml": ["PyYAML"],
            "PIL": ["Pillow"],
            "local_name": ["other"],
            "own_alias": ["my_project", "other"],
        }
        with patch(
            "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61."
            "RESOLUTION.RESOLUTION__shared.metadata.packages_distributions",
            return_value=installed,
        ):
            _, occurrences, _, _, _ = resolve_realization(
                root, capture(root, None)
            )
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
        for name, content in {
            "pkg/package.json": '{"name":"pkg"}',
            "pkg/a.py": "import other.b\n",
            "pkg/app.js": "",
            "pkg/pkg__tests/test.py": "",
            "pkg/pkg__tests/test.js": "",
            "pkg/pkg__tests/package.json": '{"name":"tests"}',
            "other/b.py": "",
        }.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        nodes, _, edges, tests, _ = resolve_realization(
            root, capture(root, None)
        )
        packages = [
            node for node in nodes if node[1] == "package" and node[3] == "pkg"
        ]
        assert len(packages) == 1
        node_by_key = {node[0]: node for node in nodes}
        assert (
            node_by_key["module:pkg/app.js"][5]
            == packages[0][0]
            == node_by_key["module:pkg/a.py"][5]
        )
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]
        assert {(source, target) for source, target, _, _ in edges} == {
            ("module:pkg/a.py", "module:other/b.py"),
            ("module:pkg/a.py", "package:local:other"),
            ("package:local:pkg", "module:other/b.py"),
            ("package:local:pkg", "package:local:other"),
        }
        (root / "pkg/a.py").unlink()
        (root / "pkg/pkg__tests/test.py").unlink()
        nodes, _, _, tests, _ = resolve_realization(root, capture(root, None))
        assert [
            node[0]
            for node in nodes
            if node[1] == "package" and node[3] == "pkg"
        ] == ["package:local:pkg"]
        assert tests == [("package:local:pkg/pkg__tests", "package:local:pkg")]
