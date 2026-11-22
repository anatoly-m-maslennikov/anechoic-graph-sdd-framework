"""Legacy Project selection and reader contracts owned by FEATURE_TOOLS."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOLS), str(TOOLS.parent)]
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.project_selection import active_selection, bind_selection, resolve_project
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.artifact_metadata import configured_timezone, project_identity
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings_context__pub import control_root
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import write_scope_unit_declarations

class ProjectStateTests(unittest.TestCase):
    def test_two_nested_projects_have_distinct_mcp_runtime_namespaces(self):
        parent = Path(tempfile.mkdtemp()).resolve()
        selections = []
        for name in ('alpha', 'beta'):
            root = parent / 'repository' / 'projects' / name
            control = root / f'.anechoic_{name}'
            control.mkdir(parents=True)
            (control / 'anechoic_project_settings.toml').write_text(
                f'[paths]\ncontrol_root=".anechoic_{name}"\n[project]\nname="{name}"\n'
                f'[project_mcp]\nhttp_port={56317 if name == "alpha" else 56318}\n')
            write_scope_unit_declarations(root, control_root=control)
            selections.append(resolve_project(root))
        left, right = selections
        for field in ('instance_id', 'compose_project', 'launcher_state'):
            self.assertNotEqual(getattr(left, field), getattr(right, field))
        for selection in selections:
            self.assertTrue(selection.launcher_state.is_relative_to(selection.root))
        left.launcher_state.mkdir(parents=True)
        (left.launcher_state / 'same-id.json').write_text('left')
        self.assertFalse((right.launcher_state / 'same-id.json').exists())


class ProjectSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        parent = Path(tempfile.gettempdir()).resolve()
        parent.mkdir(parents=True, exist_ok=True)
        self.fixture_root = Path(tempfile.mkdtemp(dir=parent))


    def project(self, name: str, *, control: str = ".anechoic_demo", port: int = 56317) -> Path:
        root = self.fixture_root / name
        carrier = root / control
        carrier.mkdir(parents=True)
        (carrier / "anechoic_project_settings.toml").write_text(
            f'[paths]\ncontrol_root = "{control}"\n[project]\nname = "{root.name}"\n'
            f'[project_mcp]\nhttp_port = {port}\n',
            encoding="utf-8",
        )
        write_scope_unit_declarations(root, control_root=carrier, project_name=root.name)
        return root


    def test_sibling_project_roots_select_only_their_direct_control_and_need_no_git(self) -> None:
        repository = self.fixture_root / "repository"
        alpha = self.project("repository/projects/alpha")
        beta = self.project("repository/projects/beta")
        (repository / ".git").mkdir(parents=True)

        selected_alpha = resolve_project(alpha)
        selected_beta = resolve_project(beta)

        self.assertEqual(alpha.resolve(), selected_alpha.root)
        self.assertEqual(beta.resolve(), selected_beta.root)
        self.assertEqual(Path(".anechoic_demo"), selected_alpha.control_relative)
        self.assertNotEqual(selected_alpha.instance_id, selected_beta.instance_id)
        self.assertEqual(56317, selected_alpha.settings["project_mcp"]["http_port"])
        self.assertEqual(
            hashlib.sha256(
                f"{alpha.resolve()}\0.anechoic_demo".encode("utf-8")
            ).hexdigest(),
            selected_alpha.instance_id,
        )
        self.assertFalse((alpha / ".git").exists())
        self.assertFalse((beta / ".git").exists())


    def test_sibling_projects_retain_distinct_configured_http_ports(self) -> None:
        alpha = self.project("repository/projects/alpha", port=56317)
        beta = self.project("repository/projects/beta", port=56318)

        self.assertEqual(56317, resolve_project(alpha).settings["project_mcp"]["http_port"])
        self.assertEqual(56318, resolve_project(beta).settings["project_mcp"]["http_port"])


    def test_explicit_direct_control_root_is_allowed_but_ambiguous_or_unsafe_selectors_refuse(self) -> None:
        project = self.project("one")
        self.assertEqual(
            project / ".anechoic_demo",
            resolve_project(project, ".anechoic_demo").control_root,
        )
        self.project("one", control=".anechoic_other")
        with self.assertRaises(ValueError):
            resolve_project(project)
        for unsafe in ("../.anechoic_demo", "/tmp/not-a-control-root", ".anechoic_demo/nested"):
            with self.subTest(selector=unsafe), self.assertRaises(ValueError):
                resolve_project(project, unsafe)


    def test_symlink_and_contradictory_control_bindings_refuse_without_sibling_fallback(self) -> None:
        project = self.project("selected")
        sibling = self.project("sibling")
        alias = project / ".anechoic_alias"
        alias.symlink_to(sibling / ".anechoic_demo", target_is_directory=True)
        with self.assertRaises(ValueError):
            resolve_project(project, ".anechoic_alias")

        settings = project / ".anechoic_demo" / "anechoic_project_settings.toml"
        settings.write_text('[paths]\ncontrol_root = ".anechoic_other"\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            resolve_project(project, ".anechoic_demo")


    def test_foreign_active_selection_context_refuses_without_substitution(self) -> None:
        alpha = self.project("repository/projects/alpha")
        beta = self.project("repository/projects/beta")
        selection_a = resolve_project(alpha)
        with bind_selection(selection_a):
            self.assertIs(selection_a, active_selection(alpha))
            with self.assertRaises(ValueError):
                active_selection(beta)


class ProjectContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=tempfile.gettempdir(), ignore_cleanup_errors=True)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.selections = []
        for name in ("alpha", "beta"):
            root = self.base / name
            control = root / (".anechoic_" + name)
            control.mkdir(parents=True)
            (control / "anechoic_project_settings.toml").write_text(
                f'[project]\nname="{name}"\nkey="{name}"\nrepository_slug="{name}"\n'
                f'[paths]\ncontrol_root=".anechoic_{name}"\n'
                f'[artifacts.identity]\nproject_prefix="{name.upper()}"\n'
                '[artifact_timestamps]\ntimezone="UTC"\n')
            write_scope_unit_declarations(root, control_root=control)
            self.selections.append(resolve_project(root))


    def test_named_readers_use_the_bound_project_without_git(self):
        for selection in self.selections:
            with bind_selection(selection):
                self.assertEqual(selection.control_root, control_root(selection.root))
                self.assertEqual(selection.settings["project"]["name"], project_identity(selection.root)["project"]["name"])
                self.assertEqual("UTC", str(configured_timezone(selection.root)))


    def test_runtime_namespace_properties_are_selected_and_read_only(self):
        for selection in self.selections:
            runtime = selection.root / ".anechoic_runtime/runtime"
            self.assertEqual(runtime / "project_mcp" / selection.instance_id, selection.launcher_state)
            self.assertFalse(runtime.exists())
            self.assertFalse((selection.root / ".anechoic_install").exists())


    def test_foreign_root_and_outside_project_source_refuse(self):
        alpha, beta = self.selections
        with bind_selection(alpha):
            with self.assertRaises(ValueError):
                control_root(beta.root)


