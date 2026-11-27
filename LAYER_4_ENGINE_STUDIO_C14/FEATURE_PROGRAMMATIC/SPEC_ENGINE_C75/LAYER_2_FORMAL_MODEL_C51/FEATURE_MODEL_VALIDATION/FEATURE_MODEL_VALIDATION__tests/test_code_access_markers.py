import unittest

from ..FEATURE_MODEL_VALIDATION__shared import (
    check_code_access,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CodeAccessOwnership,
)

from . import _code_access_check_fixtures as fixtures
from .FEATURE_MODEL_VALIDATION__tests__shared import CodeAccessOccurrence


class CheckTests(unittest.TestCase):
    def test_marker_opt_in_and_spec_override(self):
        entries = fixtures._fixture_3_entries()
        ownership = CodeAccessOwnership(
            entries, {v["path"]: k for k, v in entries.items()}
        )

        sites = [
            _marker_occurrence("billing/api.py", "run"),
            _marker_occurrence("billing/open__public.py"),
        ]
        sources = {"billing/api.py": None, "billing/open__public.py": None}
        self.assertEqual(
            [p.written for p in check_code_access(ownership, sources, sites)],
            ["alias"],
        )
        entries["provider"]["fields"] = {
            "boundaries": {"code": {"exports": {"billing.api.run": "public"}}}
        }
        self.assertEqual(
            [p.written for p in check_code_access(ownership, sources, sites)],
            ["alias"],
        )
        entries["provider"]["fields"]["boundaries"]["code"]["exports"] = {}
        self.assertEqual(len(check_code_access(ownership, sources, sites)), 2)
        entries["provider"]["fields"] = {}
        self.assertEqual(
            len(
                check_code_access(
                    ownership, {"billing/api.py": None}, sites[:1]
                )
            ),
            1,
        )
        entries["other"]["parent"] = "root"
        self.assertEqual(
            len(
                check_code_access(
                    ownership, {"billing/api.py": None}, sites[:1]
                )
            ),
            1,
        )

    def test_direct_visibility_is_provider_relative(self):
        entries = fixtures._fixture_4_entries()
        ownership = CodeAccessOwnership(
            entries, {v["path"]: k for k, v in entries.items()}
        )

        def allowed(source, target):
            site = CodeAccessOccurrence(
                source, target, "module", None, target, 1, 0, "internal"
            )
            return not check_code_access(ownership, {target: None}, [site])

        for target in (
            "billing/api__shared.py",
            "billing/api__family_pub.py",
            "billing/api__internal.py",
        ):
            for source in ("billing/a.py", "root.py", "sales/a.py"):
                self.assertTrue(allowed(source, target), (source, target))
            for source in (
                "billing/child/a.py",
                "sales/sub/a.py",
                "billing/child/other/a.py",
            ):
                self.assertFalse(allowed(source, target), (source, target))
        self.assertTrue(allowed("sales/sub/a.py", "billing/api__public.py"))
        self.assertFalse(allowed("sales/sub/a.py", "billing/api__pub.py"))
        self.assertFalse(allowed("sales/a.py", "billing/api.py"))
        self.assertTrue(allowed("billing/a.py", "billing/api.py"))
        self.assertFalse(
            allowed("sales/a.py", "billing/nested/api__family_pub.py")
        )
        entries["provider"]["fields"] = {
            "boundaries": {"code": {"exports": {"billing.api": "public"}}}
        }
        self.assertTrue(allowed("sales/sub/a.py", "billing/api.py"))
        self.assertFalse(allowed("sales/a.py", "billing/api__pub.py"))

    def test_inherited_rules_and_uncertain_imports(self):
        entries = fixtures._fixture_5_entries()
        ownership = CodeAccessOwnership(
            entries, {v["path"]: k for k, v in entries.items()}
        )
        sites = [
            CodeAccessOccurrence(
                "a/x.py",
                "b/open__public.py",
                "module",
                None,
                "b.open__public",
                2,
                0,
                "internal",
            ),
            CodeAccessOccurrence(
                "a/x.py", None, None, None, "missing", 3, 0, "unresolved"
            ),
        ]
        result = check_code_access(
            ownership, {"b/open__public.py": None}, sites
        )
        self.assertEqual(
            [(p.status, p.line) for p in result],
            [("denied", 2), ("uncertain", 3)],
        )


def _marker_occurrence(target, unit=None):
    return CodeAccessOccurrence(
        "caller/other/a.py",
        target,
        "module",
        unit,
        "alias",
        1,
        0,
        "internal",
    )


if __name__ == "__main__":
    unittest.main()
