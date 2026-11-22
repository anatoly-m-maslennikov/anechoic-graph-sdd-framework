"""Check Code Access keeps individual captured import sites."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
    capture, code_access_occurrences, resolve_realization,
)


class CodeAccessOccurrenceTests(unittest.TestCase):
    def test_named_imports_and_submodule_keep_their_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pkg").mkdir()
            (root / "pkg" / "__init__.py").write_text("")
            (root / "pkg" / "api.py").write_text("")
            (root / "client.py").write_text(
                "from pkg.api import first as one, second as two\n"
                "from pkg import api\n"
                "from pkg.api import *\n"
                "from missing import unknown\n"
                "import pkg\n"
                "import pathlib\n"
            )
            fixtures = ("client.py", "pkg/__init__.py", "pkg/api.py")
            packages, facts = code_access_occurrences(root, capture(root, None, fixtures))
            self.assertEqual(packages, {"pkg"})
        self.assertEqual(len(facts), 7)
        self.assertEqual([fact.unit for fact in facts], ["first", "second", None, "*", "unknown", None, None])
        self.assertEqual([fact.target_path for fact in facts[:4]], ["pkg/api.py"] * 4)
        self.assertTrue(all(fact.target_kind == "module" for fact in facts[:4]))
        self.assertEqual([fact.written for fact in facts[:3]], [
            "from pkg.api import first", "from pkg.api import second", "from pkg import api",
        ])
        self.assertEqual((facts[0].line, facts[0].column), (1, 0))
        self.assertEqual((facts[4].target_path, facts[4].status), (None, "unresolved"))
        self.assertEqual((facts[5].target_path, facts[5].target_kind), ("pkg", "package"))
        self.assertEqual((facts[6].target_path, facts[6].status), (None, "external"))

    def test_inferred_child_roots_are_isolated_for_both_resolvers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for child in ("first", "second"):
                project = root / child
                (project / "same").mkdir(parents=True)
                (project / "pyproject.toml").write_text('[project]\nname = "' + child + '"\nversion = "1"\n')
                (project / "uv.lock").write_text("")
                (project / "same" / "__init__.py").write_text("")
                (project / "client.py").write_text("import same\nimport only_second\n")
            (root / "second" / "only_second.py").write_text("")
            sources = capture(root, None, ("first/client.py", "first/same/__init__.py",
                                           "second/client.py", "second/same/__init__.py",
                                           "second/only_second.py"))
            _, facts = code_access_occurrences(root, sources, None)
            _, occurrences, _, _, _ = resolve_realization(root, sources, None)
        by_site = {(fact.source_path, fact.line): (fact.target_path, fact.status) for fact in facts}
        self.assertEqual(by_site[("first/client.py", 1)], ("first/same", "internal"))
        self.assertEqual(by_site[("second/client.py", 1)], ("second/same", "internal"))
        self.assertEqual(by_site[("first/client.py", 2)], (None, "unresolved"))
        self.assertEqual(by_site[("second/client.py", 2)], ("second/only_second.py", "internal"))
        graph = {(row[1].removeprefix("module:"), row[4]): (row[2], row[6]) for row in occurrences}
        self.assertEqual(graph[("first/client.py", 2)], (None, "unresolved"))
        self.assertEqual(graph[("second/client.py", 1)], ("package:local:second/same", "internal"))

    def test_inferred_external_aliases_follow_owning_child_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for child in ("engine", "setup"):
                project = root / child
                project.mkdir()
                (project / "pyproject.toml").write_text('[project]\nname = "' + child + '"\nversion = "1"\n')
                (project / "uv.lock").write_text(
                    '[[package]]\nname = "engine-only-dist"\n' if child == "engine"
                    else '[[package]]\nname = "setup-lib"\n'
                )
                (project / "client.py").write_text("import engine_alias\nimport setup_alias\n")
            sources = capture(root, None, ("engine/client.py", "setup/client.py"))
            installed = {"engine_alias": ["engine_only_dist"], "setup_alias": ["setup.lib"]}
            with patch("importlib.metadata.packages_distributions", return_value=installed):
                _, facts = code_access_occurrences(root, sources, None)
                _, occurrences, _, _, _ = resolve_realization(root, sources, None)
        actual = {(fact.source_path, fact.line): fact.status for fact in facts}
        graph = {(row[1].removeprefix("module:"), row[4]): row[6] for row in occurrences}
        expected = {("engine/client.py", 1): "external", ("engine/client.py", 2): "unresolved",
                    ("setup/client.py", 1): "unresolved", ("setup/client.py", 2): "external"}
        self.assertEqual(actual, expected)
        self.assertEqual(graph, expected)

    def test_inferred_roots_use_separate_environment_locks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for child, env in (("LAYER_4_ENGINE_STUDIO_C14", "engine"),
                               ("LAYER_6_RUNTIME_SETUP", "setup")):
                (root / child).mkdir()
                (root / child / "client.py").write_text("import engine_alias\n")
                project = root / "LAYER_3_ENVIRONMENTS_C72" / env
                project.mkdir(parents=True)
                (project / "pyproject.toml").write_text('[project]\nname = "' + env + '"\n')
                (project / "uv.lock").write_text('[[package]]\nname = "engine-dist"\n' if env == "engine" else "")
            sources = capture(root, None, ("LAYER_4_ENGINE_STUDIO_C14/client.py", "LAYER_6_RUNTIME_SETUP/client.py"))
            with patch("importlib.metadata.packages_distributions", return_value={"engine_alias": ["engine-dist"]}):
                _, facts = code_access_occurrences(root, sources, None)
                _, occurrences, _, _, _ = resolve_realization(root, sources, None)
            self.assertEqual([fact.status for fact in facts], ["external", "unresolved"])
            self.assertEqual([row[6] for row in occurrences], ["external", "unresolved"])

    def test_inference_without_child_projects_uses_workspace_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "helper.py").write_text("")
            (root / "client.py").write_text("import helper\n")
            sources = capture(root, None, ("client.py", "helper.py"))
            _, facts = code_access_occurrences(root, sources, None)
            _, occurrences, _, _, _ = resolve_realization(root, sources, None)
        self.assertEqual((facts[0].target_path, facts[0].status), ("helper.py", "internal"))
        self.assertEqual((occurrences[0][2], occurrences[0][6]), ("module:helper.py", "internal"))

    def test_explicit_root_retains_legacy_src_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src" / "pkg").mkdir(parents=True)
            (root / "src" / "pkg" / "__init__.py").write_text("")
            (root / "client.py").write_text("import pkg\n")
            sources = capture(root, None, ("client.py", "src/pkg/__init__.py"))
            _, facts = code_access_occurrences(root, sources, ("src",))
            _, occurrences, _, _, _ = resolve_realization(root, sources, ("src",))
        self.assertEqual((facts[0].target_path, facts[0].status), ("src/pkg", "internal"))
        self.assertEqual((occurrences[0][2], occurrences[0][6]), ("package:local:src/pkg", "internal"))

    def test_previous_image_imports_keep_exact_source_scope_and_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "selector.py").write_text("from old.runtime import Reader\nimport other.missing\n")
            (root / "local.py").write_text("from old.runtime import Reader\n")
            sources = capture(root, None, ("selector.py", "local.py"))
            imports = {"selector.py": ("old.runtime",)}
            _, facts = code_access_occurrences(root, sources, python_image_imports=imports)
            nodes, occurrences, _, _, _ = resolve_realization(root, sources, python_image_imports=imports)
        by_site = {(fact.source_path, fact.line): fact for fact in facts}
        self.assertEqual("external", by_site["selector.py", 1].status)
        self.assertEqual("Reader", by_site["selector.py", 1].unit)
        self.assertEqual("unresolved", by_site["selector.py", 2].status)
        self.assertEqual("unresolved", by_site["local.py", 1].status)
        target = "module:external:previous-image:old.runtime"
        self.assertIn((target, "module", "python", None, "declared_previous_image", None), nodes)
        self.assertTrue(any(row[1:3] == ("module:selector.py", target) and row[6] == "external"
                            for row in occurrences))


if __name__ == "__main__":
    unittest.main()
