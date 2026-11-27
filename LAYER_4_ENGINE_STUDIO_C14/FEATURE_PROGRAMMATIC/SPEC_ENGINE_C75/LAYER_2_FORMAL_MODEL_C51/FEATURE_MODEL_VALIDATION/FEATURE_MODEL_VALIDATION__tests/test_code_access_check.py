import unittest
from dataclasses import replace

from ..FEATURE_MODEL_VALIDATION__shared import (
    check_code_access,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CodeAccessOwnership,
)

from . import _code_access_check_fixtures as fixtures
from .FEATURE_MODEL_VALIDATION__tests__shared import CodeAccessOccurrence


class CheckTests(unittest.TestCase):
    def test_test_package_imports_require_a_test_source(self):
        entries = fixtures._fixture_0_entries()
        ownership = CodeAccessOwnership(entries, {".": "root"})
        target = "pkg/pkg__tests/nested/helper.py"
        site = CodeAccessOccurrence(
            "pkg/main.py", target, "module", "*", "helper", 1, 0, "internal"
        )
        package = replace(
            site,
            target_path="pkg/pkg__tests",
            target_kind="package",
            unit=None,
        )
        asset = replace(
            site,
            target_path="pkg/pkg__tests/data.json",
            target_kind="asset",
            status="asset",
        )
        for occurrence in (site, package, asset):
            self.assertEqual(
                [
                    (finding.status, finding.reason)
                    for finding in check_code_access(
                        ownership, {}, [occurrence]
                    )
                ],
                [("denied", "non-test import from Test Package")],
            )
        for occurrence in (
            replace(site, source_path="peer/peer__tests/test_main.py"),
            replace(site, target_path="pkg/pkg__tests_support/helper.py"),
            replace(asset, source_path="peer/peer__tests/test_main.ts"),
            replace(asset, target_path="pkg/runtime.json"),
        ):
            self.assertEqual(
                (), check_code_access(ownership, {}, [occurrence])
            )

    def test_entry_bypass_requires_both_exact_declarations(self):
        target = "app/src/lib/parse.ts"
        selector = "src.lib.parse.run"
        code = {
            "imports": [selector],
            "exports": {selector: {"private": ["app/tests"]}},
        }
        entries = fixtures._fixture_1_entries(code)
        ownership = CodeAccessOwnership(
            entries, {value["path"]: key for key, value in entries.items()}
        )
        site = CodeAccessOccurrence(
            "app/tests/run.ts",
            target,
            "module",
            "run",
            target,
            1,
            0,
            "internal",
        )

        self._assert_bypass_outcomes(code, selector, ownership, site)

    def _assert_bypass_outcomes(self, code, selector, ownership, site):
        self.assertEqual(["declared_bypass"], _bypass_status(ownership, site))
        self.assertEqual(
            ["uncertain"], _bypass_status(ownership, replace(site, unit="*"))
        )
        code["imports"] = ["siblings"]
        self.assertEqual(
            ["undeclared_bypass"], _bypass_status(ownership, site)
        )
        code["imports"] = {"only": []}
        self.assertEqual(["denied"], _bypass_status(ownership, site))
        code["imports"] = [selector]
        del code["exports"][selector]
        self.assertEqual(["denied"], _bypass_status(ownership, site))
        del code["exports"]
        code["imports"] = ["siblings"]
        self.assertEqual(
            [],
            _bypass_status(
                ownership,
                replace(site, target_path="app/src/lib/parse__public.ts"),
            ),
        )
        self.assertEqual(
            ["denied"],
            _bypass_status(
                ownership,
                replace(site, target_path="app/src/lib/parse__pub.ts"),
            ),
        )

    def test_component_declares_a_nested_package_export(self):
        code = {
            "imports": {"only": ["src.lib.lib__shared"]},
            "exports": {"src.lib.lib__shared": {"private": ["app/tests"]}},
        }
        ownership = fixtures._fixture_2_ownership(code)
        target = "app/src/lib/lib__shared.ts"
        site = CodeAccessOccurrence(
            "app/tests/run.ts",
            target,
            "module",
            None,
            target,
            1,
            0,
            "internal",
        )
        self.assertEqual((), check_code_access(ownership, {}, [site]))
        self.assertEqual(
            (),
            check_code_access(
                ownership, {}, [site], include_entry_bypasses=True
            ),
        )
        code["exports"]["src.lib.lib__shared"] = {"private": ["unrelated"]}
        self.assertEqual(
            "denied", check_code_access(ownership, {}, [site])[0].status
        )


def _bypass_status(ownership, occurrence):
    return [
        finding.status
        for finding in check_code_access(
            ownership,
            {},
            [occurrence],
            include_entry_bypasses=True,
        )
    ]


if __name__ == "__main__":
    unittest.main()
