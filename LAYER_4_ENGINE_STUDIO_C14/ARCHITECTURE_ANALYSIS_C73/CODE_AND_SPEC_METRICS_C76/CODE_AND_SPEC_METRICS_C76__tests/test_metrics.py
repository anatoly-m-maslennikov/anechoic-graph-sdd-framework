import unittest

from ..metrics__shared import code_rows, spec_rows


def _attributed_rows():
    nodes = [
        ["p", "package", "python", "a", None, None, None],
        [
            "t",
            "package",
            "python",
            "a/a__tests",
            None,
            None,
            "Test Package",
        ],
        ["c", "package", "python", "a/child", None, None, None],
        ["m", "module", "python", "a/x.py", "parsed", "p", None],
        ["u", "module", "python", "a/test_lonely.py", "parsed", "p", None],
        [
            "s",
            "module",
            "python",
            "a/a__tests/test_x.py",
            "parsed",
            "t",
            None,
        ],
        [
            "c1",
            "module",
            "python",
            "a/child/x.py",
            "read_error",
            "c",
            None,
        ],
    ]
    sizes = {n[3]: (10, 1) for n in nodes if n[1] == "module"}
    return code_rows(
        nodes,
        [("t", "p"), ("t", "C1")],
        {".": "C00", "a": "C1", "a/child": "C2"},
        sizes,
        {"a/a__tests/assets/x": ("t", 4, None)},
    )


def _cross_component_rows():
    test_kind = "Test Package"
    bound_test = "b/b__tests/test_x.py"
    unbound_test = "b/unbound__tests/test_y.py"
    nodes = [
        ["p", "package", "python", "a", None, None, None],
        ["t", "package", "python", "b/b__tests", None, None, test_kind],
        ["u", "package", "python", "b/unbound__tests", None, None, test_kind],
        ["m", "module", "python", bound_test, "parsed", "t", None],
        ["n", "module", "python", unbound_test, "parsed", "u", None],
    ]
    return code_rows(
        nodes,
        [("t", "p")],
        {".": "C00", "a": "C1", "b": "C2"},
        {
            bound_test: (10, 1),
            unbound_test: (5, 1),
        },
        {
            "b/b__tests/assets/x": ("t", 4, None),
            "b/unbound__tests/assets/y": ("u", 2, None),
        },
    )


def _bound_rows():
    test = "b/b__tests/test_x.py"
    asset = "b/b__tests/assets/x"
    return {
        ("Component", "C1", test, "test_code", 10, 1),
        ("Package", "p", test, "test_code", 10, 1),
        ("Component", "C1", asset, "test_assets", 4, None),
        ("Package", "p", asset, "test_assets", 4, None),
    }


class MetricsTests(unittest.TestCase):
    def test_code_attribution_and_unclassified(self):
        rows = _attributed_rows()
        self.assertIn(
            ["Component", "C1", "a/a__tests/test_x.py", "test_code", 10, 1],
            rows,
        )
        self.assertEqual(
            1,
            sum(
                r[:3] == ["Component", "C1", "a/a__tests/test_x.py"]
                for r in rows
            ),
        )
        self.assertIn(
            ["Package", "p", "a/a__tests/assets/x", "test_assets", 4, None],
            rows,
        )
        self.assertIn(
            ["Package", "p", "a/test_lonely.py", "unclassified", 10, 1], rows
        )
        self.assertIn(
            ["Component", "C2", "a/child/x.py", "unclassified", 10, 1], rows
        )
        self.assertFalse(
            any(r[1] == "C1" and r[2] == "a/child/x.py" for r in rows)
        )

    def test_unreadable_source_without_size_fails_explicitly(self):
        nodes = [
            ["p", "package", "python", "a", None, None, None],
            ["m", "module", "python", "a/x.py", "read_error", "p", None],
        ]
        with self.assertRaisesRegex(
            ValueError, "Cannot measure unreadable source: a/x.py"
        ):
            code_rows(nodes, [], {"a": "C1"}, {}, {})

    def test_cross_component_tests_and_unbound_paths(self):
        rows = _cross_component_rows()
        self.assertEqual(
            {tuple(r) for r in rows if r[2].startswith("b/b__tests/")},
            _bound_rows(),
        )
        self.assertIn(
            [
                "Component",
                "C2",
                "b/unbound__tests/test_y.py",
                "unclassified",
                5,
                1,
            ],
            rows,
        )
        self.assertIn(
            [
                "Package",
                "u",
                "b/unbound__tests/assets/y",
                "unclassified",
                2,
                None,
            ],
            rows,
        )

    def test_spec_carrier_measurements(self):
        atoms = [
            {
                "id": "AN-S-1",
                "ref": "AN-S-1",
                "_exact_ref": "AN-S-1@1",
                "status_group": "Current",
                "_source_bytes": 20,
                "_source_lines": 3,
                "_content_bytes": b"a\nb\n",
            },
            {"id": "AN-S-2", "status_group": "Draft"},
            {"id": "AN-T-1", "status_group": "Current"},
        ]
        self.assertEqual([["AN-S-1@1", 20, 3, 4, 2]], spec_rows(atoms))


if __name__ == "__main__":
    unittest.main()
