"""Saved query links across HTTP and stdio transports."""
from dataclasses import replace
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from urllib.parse import urlencode

MCP = Path(__file__).resolve().parents[1]
programmatic = MCP.parents[1] / "FEATURE_PROGRAMMATIC"
from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import ProjectBinding  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.registry_workbench_provider import WorkbenchProvider  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workbench_links import public_saved  # noqa: E402


class SavedPublicLinksTests(unittest.TestCase):
    def test_stdio_config_and_unknown_for_save_and_list(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            selection = SimpleNamespace(root=root, project_name="alpha", parameters={})
            provider = WorkbenchProvider(SimpleNamespace(selection=selection))
            context = SimpleNamespace(request=None, params={"arguments": {"project_root": str(root)}})
            saved = {"saved_query_id": "q_1"}
            unknown = provider.present_result("query_run", saved, context)
            self.assertEqual({**saved, "saved_query_url": None, "saved_query_url_reason": "workbench_url_unknown"}, unknown)
            selection.parameters = {"runtime": {"workbench": {"public_url": "https://example.test/custom/page"}}}
            linked = provider.present_result("query_saved_list", {"items": [saved]}, context)["items"][0]
            self.assertEqual("https://example.test/custom/page?" + urlencode({"query": "q_1", "project_root": str(root)}), linked["saved_query_url"])
            request = SimpleNamespace(base_url="http://localhost/")
            self.assertEqual("http://localhost/anechoic/workbench/alpha?query=q_1", public_saved(saved, request, selection)["saved_query_url"])

    def test_native_stdio_uses_only_manifest_public_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            control = Path(".anechoic_anechoic")
            selection = ProjectBinding(root, root / control, control, "test", "Anechoic", "AN",
                                               root / control / "manifest.md", "AN-S-1@1", "test")
            legacy = root / ".anechoic_runtime" / "anechoic_runtime_settings.toml"
            legacy.parent.mkdir()
            legacy.write_text('[workbench]\npublic_url = "https://legacy.test/workbench"\n')
            saved = {"saved_query_id": "q_1"}
            self.assertIsNone(public_saved(saved, None, selection)["saved_query_url"])
            for url in ("https://native.test/workbench", "javascript:alert(1)"):
                native = replace(selection, parameters={"runtime": {"workbench": {"public_url": url}}})
                expected = f"{url}?query=q_1" if url.startswith("https://") else None
                with self.subTest(url=url):
                    self.assertEqual(expected, public_saved(saved, None, native)["saved_query_url"])


if __name__ == "__main__":
    unittest.main()
