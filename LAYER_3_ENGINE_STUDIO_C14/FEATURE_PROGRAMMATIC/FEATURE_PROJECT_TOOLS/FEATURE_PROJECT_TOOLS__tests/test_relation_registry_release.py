# CA-E-804@5

"""Tool registry generation must succeed before building the release image."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "LAYER_5_FRAMEWORK_DELIVERY/LAYER_5_FRAMEWORK_DELIVERY__tests"))
import test_simple_local_release as release_fixture
import local_release


class RelationRegistryReleaseTests(unittest.TestCase):
    def setUp(self):
        self.fixture = release_fixture.SimpleLocalReleaseTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_missing_tool_registry_generator_stops_before_image_build_or_startup(self):
        fixture = self.fixture
        (fixture.engine_bootstrap.parent.parent / "generate_tool_registry.py").unlink()
        runner, calls = fixture._runner()
        result = local_release.run_local_release(fixture.root, run_id="tool-registry-missing", runner=runner)
        self.assertEqual(("failed", "build_package"), (result["outcome"], result["failed_step"]))
        fixture.image_factory.assert_not_called()
        self.assertFalse(any(fixture._is_mcp_bootstrap(argv) for argv in calls))

    def test_invalid_tool_registry_output_stops_before_image_build_or_startup(self):
        fixture = self.fixture
        script = fixture.engine_bootstrap.parent.parent / "generate_tool_registry.py"
        script.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            "root = Path(sys.argv[sys.argv.index('--package-root') + 1])\n"
            "(root / 'LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/tool_registry.json').write_text('not-json', encoding='utf-8')\n",
            encoding="utf-8",
        )
        runner, calls = fixture._runner()
        result = local_release.run_local_release(fixture.root, run_id="tool-registry-invalid", runner=runner)
        self.assertEqual(("failed", "build_package"), (result["outcome"], result["failed_step"]))
        fixture.image_factory.assert_not_called()
        self.assertFalse(any(fixture._is_mcp_bootstrap(argv) for argv in calls))

if __name__ == "__main__":
    unittest.main()
