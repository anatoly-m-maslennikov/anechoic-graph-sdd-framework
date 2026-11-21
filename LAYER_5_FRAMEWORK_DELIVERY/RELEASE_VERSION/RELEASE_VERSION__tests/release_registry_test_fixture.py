"""Small deterministic generator used by package-release fixtures."""

from pathlib import Path


def write_tool_registry_generator(directory: Path) -> Path:
    script = directory / "generate_tool_registry.py"
    script.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        "root = Path(sys.argv[sys.argv.index('--package-root') + 1])\n"
        "(root / 'LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/tool_registry.json').write_text("
        "'{\"schema_version\":1,\"providers\":[]}\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    return script
