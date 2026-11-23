"""Shared filesystem and command fixture for local Release tests."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from RELEASE_VERSION import local_release_runner
from RELEASE_VERSION.RELEASE_VERSION__shared import run_local_release
from RELEASE_VERSION.RELEASE_VERSION__shared import _GENERATED_ASSETS


class SimpleReleaseFixture:
    def setUp(self) -> None:
        self._setup_filesystem()
        self._setup_engine()
        self._setup_mocks()

    def _setup_filesystem(self):
        self.temporary = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.control = self.root / ".anechoic_anechoic"
        self.control.mkdir()
        ontology = self.control / "LAYER_1_META_ONTOLOGY_C9"
        ontology.mkdir()
        self.native_sources = (
            ontology / "AN-S-10-SPEC--model.md",
            ontology / "AN-S-11-SPEC--related-spec.md",
        )
        for path in self.native_sources:
            atom_id = path.name.split("-SPEC--")[0]
            path.write_text(f"---\natom_family: SPEC\natom_id: {atom_id}\nstate:\n  status: active\n  version: 1\n---\n## Claim\nNative source\n", encoding="utf-8")
        (self.root / ".gitignore").write_text(".anechoic_tmp/\n/.anechoic_runtime/\n", encoding="utf-8")
        self.product = self.root / "LAYER_1_FRAMEWORK_METHODOLOGY"
        self.installed = self.control / "000_ANECHOIC_framework"
        self.runtime = self.root / ".anechoic_runtime"
        delivery = self.root / "LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE"
        delivery.mkdir(parents=True)
        (delivery / "public_release.py").write_text("# release source\n", encoding="utf-8")
        (delivery / "PUBLIC_RELEASE__tests").mkdir()
        (delivery / "PUBLIC_RELEASE__tests/test_private.py").write_text("# excluded test\n", encoding="utf-8")
        for destination in (self.product, self.installed, self.runtime):
            destination.mkdir(parents=True)
            (destination / "old.txt").write_text("obsolete", encoding="utf-8")
            (destination / "config.toml").write_text("keep = true\n", encoding="utf-8")

    def _setup_engine(self):
        skill = self.root / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("ane skill", encoding="utf-8")
        (skill / "references").mkdir()
        (skill / "references/details.md").write_text("skill reference", encoding="utf-8")
        (self.root / "pyproject.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
        (self.root / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        for child in ("LAYER_3_ENVIRONMENTS_C72/engine", "LAYER_3_ENVIRONMENTS_C72/release", "LAYER_3_ENVIRONMENTS_C72/setup"):
            directory = self.root / child
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "pyproject.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
            (directory / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        (self.root / "version.toml").write_text('[framework]\nversion = "0.4.1"\n', encoding="utf-8")
        tools = self.root / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"
        tools.mkdir(parents=True)
        (tools / "tests").mkdir()
        (tools / "tests/test_retired.py").write_text("# package-excluded test\n", encoding="utf-8")
        (tools / "fixtures").mkdir()
        (tools / "fixtures/input.json").write_text("{}\n", encoding="utf-8")
        (tools / "README.md").write_text("package-excluded prose\n", encoding="utf-8")
        (tools / "scope_declaration_test_support.py").write_text("# package-excluded test helper\n", encoding="utf-8")
        (tools / "scope_declaration_render.py").write_text("# package-excluded test renderer\n", encoding="utf-8")
        skill = tools / "retained/SKILL.md"
        skill.parent.mkdir()
        skill.write_text("retained implementation skill\n", encoding="utf-8")
        subject_builder = tools / "GENERATE_ENTITY_GRAPH/render_entity_tree.py"
        subject_builder.parent.mkdir()
        subject_builder.write_text("# retained subject builder\n", encoding="utf-8")
        prompt = self.root / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/retired.py"
        prompt.parent.mkdir(parents=True)
        prompt.write_text("# source-only prompt\n", encoding="utf-8")
        self.engine_bootstrap = (
            self.root / "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/"
            "docker/start_mcp.py"
        )
        self.engine_bootstrap.parent.mkdir(parents=True)
        self.engine_bootstrap.write_bytes(b"#!/usr/bin/env python3\n# package bootstrap fixture\n")
        self.engine_bootstrap.chmod(0o755)
        (self.engine_bootstrap.parent / "runtime.py").write_text("# runtime entrypoint fixture\n", encoding="utf-8")
        backend = self.root / "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND"
        backend.mkdir(parents=True)
        (backend / "tool_providers.json").write_text(
            '{"mcp_blacklist":[],"providers":[]}\n', encoding="utf-8")

    def _setup_mocks(self):
        self.image_id = "sha256:" + "a" * 64
        self.image = SimpleNamespace(resolve=Mock(return_value=self.image_id),
                                     identity=Mock(return_value=SimpleNamespace(fingerprint="b" * 64)),
                                     mark_production_image=Mock(), prune_build_cache=Mock())
        original_launcher_image = local_release_runner._launcher_image

        def scoped_launcher_image(selection):
            observed = original_launcher_image(selection)
            if observed is not None:
                return observed
            package = self.runtime / "simple_local_release/package"
            return self.image_id if package.is_dir() else None

        launcher = patch("RELEASE_VERSION.local_release_runner._launcher_image", side_effect=scoped_launcher_image)
        launcher.start()
        self.addCleanup(launcher.stop)
        image_factory = patch("RELEASE_VERSION.local_release_package_phases._image_manager", return_value=self.image)
        self.image_factory = image_factory.start()
        self.addCleanup(image_factory.stop)
        self.start_container = self.enterContext(patch(
            "RELEASE_VERSION.local_release_runner.start_container", return_value="http://localhost:12345/mcp"
        ))
        provenance = patch("RELEASE_VERSION.local_release_package_phases.release_image_provenance", return_value={
            "project_id": "c" * 64, "project_root": str(self.root),
            "control_root": ".anechoic_anechoic", "project_name": "Fixture",
            "head_commit": "d" * 40,
        })
        self.provenance = provenance.start()
        self.addCleanup(provenance.stop)

        self._native_project()


    def _runner(self):
        calls = []
        staged = False

        def run(argv, cwd):
            nonlocal staged
            self.assertEqual(self.root, cwd)
            calls.append(argv)
            if argv[:2] == ("git", "add"):
                staged = True
            elif argv[:2] == ("git", "commit"):
                staged = False
            if argv[:2] == ("git", "rev-parse"):
                return subprocess.CompletedProcess(argv, 0, "d" * 40 + "\n", "")
            if argv == ("git", "diff", "--cached", "--quiet"):
                return subprocess.CompletedProcess(argv, int(staged), "", "")
            if "--phase" in argv and argv[argv.index("--phase") + 1] == "image":
                return subprocess.CompletedProcess(argv, 0, "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n", "")
            return subprocess.CompletedProcess(argv, 0, "", "")

        return run, calls


    def _is_mcp_bootstrap(self, argv: tuple[str, ...]) -> bool:
        return (
            len(argv) > 1
            and argv[0] == sys.executable
            and argv[1] == str(self.runtime / "start_mcp.py")
        )


    def _mcp_bootstrap_success(self, argv: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        launcher_python = self.runtime / "launcher-venv/bin/python"
        launcher_python.parent.mkdir(parents=True, exist_ok=True)
        launcher_python.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        launcher_python.chmod(0o755)
        return subprocess.CompletedProcess(argv, 0, "http://localhost:12345/mcp\n", "")


    def _native_project(self):
        manifest = self.control / "AN-S-001-PROJECT_MANIFEST--declare.md"
        manifest.parent.mkdir(exist_ok=True)
        manifest.write_text(
            "---\nidentity:\n  atom_id: AN-S-001\ncontext:\n  container:\n    component: C00\n"
            "  tier: -1\n  template: project_manifest\nstate:\n  status: active\n  version: 1\n---\n"
            "## Claim\n\n### Formal Claim\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest\n"
            "declare_entity(entity_name='Project Manifest', "
            "instance=ProjectManifest(name='Anechoic', prefix='AN', "
            "parameters={'project_mcp': {'http_port': 12345}}))\n```\n", encoding="utf-8",
        )

        for relative in _GENERATED_ASSETS:
            (self.root / relative).write_text('{"sealed": true}\n', encoding="utf-8")


    def _native_sources(self):
        return {source.relative_to(self.control): source for source in self.native_sources if source.is_file()}


    def _assert_input_refused(self, run_id, failed_step="validate_inputs"):
        runner, calls = self._runner()
        result = run_local_release(self.root, run_id=run_id, runner=runner)
        self.assertEqual("failed", result["outcome"])
        self.assertEqual(failed_step, result["failed_step"])
        for target in (self.product, self.installed):
            self.assertEqual("obsolete", (target / "old.txt").read_text())
        self.assertFalse(any(any(item.endswith("test_suite__pub.py") for item in argv) for argv in calls))
        self.start_container.assert_not_called()
        self.image_factory.assert_not_called()


