"""Fake engine files for local release fixtures."""


class SimpleReleaseEngineFixture:
    def _setup_engine(self):
        skill = (
            self.root
            / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane"
        )
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("ane skill", encoding="utf-8")
        (skill / "references").mkdir()
        (skill / "references/details.md").write_text(
            "skill reference", encoding="utf-8"
        )
        (self.root / "pyproject.toml").write_text(
            "[project]\nname = 'fixture'\n", encoding="utf-8"
        )
        (self.root / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        for child in (
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine",
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release",
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/setup",
        ):
            directory = self.root / child
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "pyproject.toml").write_text(
                "[project]\nname = 'fixture'\n", encoding="utf-8"
            )
            (directory / "uv.lock").write_text(
                "version = 1\n", encoding="utf-8"
            )
        (self.root / "version.toml").write_text(
            '[framework]\nversion = "0.4.1"\n', encoding="utf-8"
        )
        self._setup_tools()
        self._setup_bootstrap()

    def _setup_tools(self):
        tools = (
            self.root
            / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"
        )
        tools.mkdir(parents=True)
        (tools / "tests").mkdir()
        (tools / "tests/test_retired.py").write_text(
            "# package-excluded test\n", encoding="utf-8"
        )
        (tools / "fixtures").mkdir()
        (tools / "fixtures/input.json").write_text("{}\n", encoding="utf-8")
        (tools / "README.md").write_text(
            "package-excluded prose\n", encoding="utf-8"
        )
        (tools / "scope_declaration_test_support.py").write_text(
            "# package-excluded test helper\n", encoding="utf-8"
        )
        (tools / "scope_declaration_render.py").write_text(
            "# package-excluded test renderer\n", encoding="utf-8"
        )
        skill = tools / "retained/SKILL.md"
        skill.parent.mkdir()
        skill.write_text("retained implementation skill\n", encoding="utf-8")
        subject_builder = tools / "GENERATE_ENTITY_GRAPH/render_entity_tree.py"
        subject_builder.parent.mkdir()
        subject_builder.write_text(
            "# retained subject builder\n", encoding="utf-8"
        )
        prompt = self.root / (
            "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/"
            "retired.py"
        )
        prompt.parent.mkdir(parents=True)
        prompt.write_text("# source-only prompt\n", encoding="utf-8")

    def _setup_bootstrap(self):
        self.engine_bootstrap = (
            self.root
            / "LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/"
            "docker/start_mcp.py"
        )
        self.engine_bootstrap.parent.mkdir(parents=True)
        self.engine_bootstrap.write_bytes(
            b"#!/usr/bin/env python3\n# package bootstrap fixture\n"
        )
        self.engine_bootstrap.chmod(0o755)
        (self.engine_bootstrap.parent / "runtime.py").write_text(
            "# runtime entrypoint fixture\n", encoding="utf-8"
        )
        backend = self.root / (
            "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/"
            "FEATURE_IWE_CONSOLE_BACKEND"
        )
        backend.mkdir(parents=True)
        (backend / "tool_providers.json").write_text(
            '{"mcp_blacklist":[],"providers":[]}\n', encoding="utf-8"
        )
