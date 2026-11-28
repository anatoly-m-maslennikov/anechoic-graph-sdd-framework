import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.access.code_access_check import (
    check_code_access,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure__shared import (
    CodeAccessOwnership,
)

from . import _code_access_check_fixtures as fixtures
from ..FEATURE_MODEL_VALIDATION__tests__shared import CodeAccessOccurrence


class CheckTests(unittest.TestCase):
    def test_layers_apply_to_packages_in_sibling_components(self):
        entries = fixtures._fixture_6_entries()
        ownership = CodeAccessOwnership(
            entries, {v["path"]: k for k, v in entries.items()}
        )
        target = "b/p/open__public.py"
        site = CodeAccessOccurrence(
            "a/x.py",
            target,
            "module",
            None,
            "b.p.open__public",
            1,
            0,
            "internal",
        )
        self.assertEqual(
            [
                p.reason
                for p in check_code_access(ownership, {target: None}, [site])
            ],
            ["sibling layer order"],
        )
        entries["b"]["fields"] = {}
        self.assertEqual(
            check_code_access(ownership, {target: None}, [site]), ()
        )

    def test_nested_divergent_component_lineage(self):
        entries = fixtures._fixture_7_entries()
        ownership = CodeAccessOwnership(
            entries, {v["path"]: k for k, v in entries.items()}
        )
        target = "b/sub/p/open__public.py"
        site = CodeAccessOccurrence(
            "a/sub/x.py", target, "module", None, target, 1, 0, "internal"
        )
        self.assertEqual(check_code_access(ownership, {}, [site]), ())
        entries["b"]["fields"]["layer"] = 2
        self.assertEqual(
            check_code_access(ownership, {}, [site])[0].reason,
            "sibling layer order",
        )


if __name__ == "__main__":
    unittest.main()
