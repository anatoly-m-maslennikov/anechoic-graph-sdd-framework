"""Check resolved Code Access decisions."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure__shared import (
    CodeAccessOwnership,
)
from ......FEATURE_TOOLS.ADAPTERS_C30.structure.code_access_rules__pub import (
    parse_code_access,
)

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.access.code_access_check import (
    check_code_access,
)
from ..FEATURE_MODEL_VALIDATION__tests__shared import CodeAccessOccurrence


def _entries():
    entries = {
        owner: {
            "id": owner,
            "parent": parent,
            "path": path,
            "kind": "component",
            "fields": {},
        }
        for owner, parent, path in (
            ("root", None, "."),
            ("billing", "root", "billing"),
            ("sales", "root", "sales"),
            ("elsewhere", "root", "elsewhere"),
            ("C43", "elsewhere", "elsewhere/consumer"),
        )
    }
    return entries


class CodeAccessTests(unittest.TestCase):
    def allows(
        self,
        caller,
        exports=None,
        *,
        imports=None,
        inherited=None,
        layers=None,
    ):
        entries = _entries()
        if exports is not None:
            entries["billing"]["fields"]["boundaries"] = {
                "code": {"exports": exports}
            }
        if imports is not None:
            entries[caller]["fields"]["boundaries"] = {
                "code": {"imports": imports}
            }
        if inherited is not None:
            entries["root"]["fields"]["boundaries"] = {
                "code": {"imports": inherited}
            }
        if layers is not None:
            (
                entries[caller]["fields"]["layer"],
                entries["billing"]["fields"]["layer"],
            ) = layers
        ownership = CodeAccessOwnership(
            entries, {value["path"]: key for key, value in entries.items()}
        )
        source = f"{entries[caller]['path']}/use.py".removeprefix("./")
        occurrence = CodeAccessOccurrence(
            source,
            "billing/api.py",
            "module",
            "run",
            "billing.api.run",
            1,
            0,
            "internal",
        )
        return not check_code_access(ownership, {}, [occurrence])

    def test_visibility_and_import_rules(self):
        shared = {"billing.api.run": "shared"}
        public = {"billing.api.run": "public"}
        private = {"billing.api.run": {"private": ["C43"]}}
        self.assertFalse(self.allows("sales"))
        self.assertFalse(self.allows("sales", {}))
        self.assertTrue(self.allows("root", shared))
        self.assertTrue(self.allows("sales", shared))
        self.assertFalse(self.allows("C43", shared))
        self.assertTrue(self.allows("C43", public))
        self.assertFalse(self.allows("C43", private))
        self.assertTrue(self.allows("C43", private, imports=["billing"]))
        self.assertTrue(
            self.allows("C43", private, imports={"only": ["billing"]})
        )
        self.assertFalse(self.allows("sales", private, imports=["billing"]))
        self.assertFalse(self.allows("sales", public, imports={"only": []}))
        self.assertTrue(
            self.allows("sales", public, imports={"only": ["billing"]})
        )
        self.assertFalse(
            self.allows("sales", shared, imports=[], inherited={"only": []})
        )
        self.assertFalse(self.allows("sales", public, layers=(1, 1)))
        self.assertTrue(self.allows("sales", public, layers=(2, 1)))
        self.assertTrue(self.allows("billing", {}, layers=(1, 1)))

    def test_markers(self):
        from ......FEATURE_TOOLS.ADAPTERS_C30.structure.code_access_rules__pub import (
            module_visibility,
        )

        for name in ("x__shared", "x__family_pub", "x__internal"):
            self.assertEqual(module_visibility(name), "shared")
        self.assertEqual(module_visibility("x__public"), "public")
        self.assertIsNone(module_visibility("x__pub"))


class ParseCodeAccessTests(unittest.TestCase):
    def test_normalizes_rules_and_preserves_empty_maps(self):
        self.assertEqual(parse_code_access(None), (None, None))
        self.assertEqual(
            parse_code_access({"code": {"imports": [], "exports": {}}}),
            ((False, set()), {}),
        )
        self.assertEqual(
            parse_code_access(
                {
                    "code": {
                        "imports": {"only": []},
                        "exports": {
                            "a": None,
                            "b": "private",
                            "c": {"shared": ["C43"]},
                            "d": "public",
                        },
                    },
                    "process": {"launch": "worker"},
                    "state": {},
                    "io": {"client": {}, "server": {}},
                }
            ),
            (
                (True, set()),
                {
                    "a": ("shared", None),
                    "b": ("private", None),
                    "c": ("shared", {"C43"}),
                    "d": ("public", None),
                },
            ),
        )

    def test_rejects_invalid_authored_values(self):
        for access in (
            {"imports": "x"},
            {"imports": {"only": ["x", "x"]}},
            {"imports": {"other": []}},
            {"exports": []},
            {"exports": {"x": {"shared": "C43"}}},
            {"exports": {"x": "internal"}},
        ):
            with self.subTest(access=access), self.assertRaises(ValueError):
                parse_code_access({"code": access})
        with self.assertRaises(ValueError):
            parse_code_access({"code_access": {}})


if __name__ == "__main__":
    unittest.main()
