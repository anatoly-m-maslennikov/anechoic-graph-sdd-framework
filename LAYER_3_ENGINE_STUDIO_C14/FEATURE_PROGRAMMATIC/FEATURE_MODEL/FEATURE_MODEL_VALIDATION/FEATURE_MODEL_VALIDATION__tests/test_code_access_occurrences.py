"""Check Code Access keeps individual captured import sites."""

from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_occurrences import code_access_occurrences
from LAYER_3_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import capture


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
            facts = code_access_occurrences(root, capture(root, None, fixtures))
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


if __name__ == "__main__":
    unittest.main()
