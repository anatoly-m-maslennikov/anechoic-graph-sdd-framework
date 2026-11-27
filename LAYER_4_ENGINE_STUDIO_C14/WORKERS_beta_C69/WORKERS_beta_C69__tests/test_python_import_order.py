import unittest

from WORKERS_beta_C69.WORKERS_beta_C69__shared import python_import_order


def occurrence(
    source,
    target,
    written,
    line=1,
    column=0,
    status="internal",
    type_only=False,
):
    return (
        f"{source}:{line}",
        "module:" + source,
        "module:" + target if target else None,
        written,
        line,
        column,
        status,
        type_only,
    )


class PythonImportOrderTests(unittest.TestCase):
    def test_later_binding_has_entry_and_relationship_witness(self):
        texts = {
            "a.py": "from b import y\nx = 1\n",
            "b.py": "from a import x\ny = 2\n",
        }
        edges = [
            occurrence("a.py", "b.py", "b"),
            occurrence("b.py", "a.py", "a"),
        ]
        result = python_import_order(texts, edges)
        confirmed = [r for r in result if r[4] == "confirmed"]
        self.assertEqual(len(confirmed), 2)
        witness = next(r for r in confirmed if "entry a.py:" in r[5])
        self.assertEqual(
            witness[:5], ("b.py", 1, 0, "python_import_order", "confirmed")
        )
        self.assertIn("a.py:1 imports b.py", witness[5])
        self.assertIn("b.py:1 imports a.py", witness[5])
        self.assertIn("reads x before a.py:2", witness[5])

    def test_deferred_cycle_is_unresolved(self):
        texts = {
            "a.py": "def f():\n    from b import y\nx = 1\n",
            "b.py": "from a import x\ny = 2\n",
        }
        edges = [
            occurrence("a.py", "b.py", "b", 2, 4),
            occurrence("b.py", "a.py", "a"),
        ]
        result = python_import_order(texts, edges)
        self.assertTrue(result)
        self.assertTrue(all(r[4] == "unresolved" for r in result))

    def test_already_bound_and_unknown_execution_not_confirmed(self):
        edges = [
            occurrence("a.py", "b.py", "b", 2),
            occurrence("b.py", "a.py", "a"),
        ]
        for first in ("x = 1", "if condition:\n    x = 1"):
            texts = {
                "a.py": first + "\nfrom b import y\nx = 2\n",
                "b.py": "from a import x\ny = 2\n",
            }
            edges[0] = occurrence(
                "a.py", "b.py", "b", len(first.splitlines()) + 1
            )
            result = python_import_order(texts, edges)
            self.assertFalse(
                any(
                    r[4] == "confirmed" and "entry a.py:" in r[5]
                    for r in result
                )
            )

    def test_ambiguous_occurrence_and_type_only_never_confirmed(self):
        texts = {
            "a.py": "from b import y\nx = 1\n",
            "b.py": "from a import x\ny = 2\n",
        }
        for edge in (
            occurrence("a.py", None, "b", status="ambiguous"),
            occurrence("a.py", "b.py", "b", type_only=True),
        ):
            self.assertFalse(
                any(
                    r[4] == "confirmed"
                    for r in python_import_order(
                        texts, [edge, occurrence("b.py", "a.py", "a")]
                    )
                )
            )

    def test_deep_cycle_package_and_invalid_syntax_not_confirmed(self):
        texts = {
            f"m{i}.py": f"from m{(i + 1) % 100} import x\nx = 1\n"
            for i in range(100)
        }
        edges = [
            occurrence(f"m{i}.py", f"m{(i + 1) % 100}.py", f"m{(i + 1) % 100}")
            for i in range(100)
        ]
        self.assertFalse(
            any(r[4] == "confirmed" for r in python_import_order(texts, edges))
        )
        package = {
            "pkg/a.py": "from pkg.b import x\nx = 1\n",
            "pkg/b.py": "from pkg.a import x\nx = 1\n",
        }
        edges = [
            occurrence("pkg/a.py", "pkg/b.py", "pkg.b"),
            occurrence("pkg/b.py", "pkg/a.py", "pkg.a"),
        ]
        self.assertFalse(
            any(
                r[4] == "confirmed"
                for r in python_import_order(package, edges)
            )
        )
        invalid = {
            "a.py": "return\nfrom b import x\nx = 1\n",
            "b.py": "from a import x\nx = 1\n",
        }
        edges = [
            occurrence("a.py", "b.py", "b", 2),
            occurrence("b.py", "a.py", "a"),
        ]
        self.assertFalse(
            any(
                r[4] == "confirmed"
                for r in python_import_order(invalid, edges)
            )
        )

    def test_self_import_does_not_crash(self):
        result = python_import_order(
            {"a.py": "from a import x\nx = 1\n"},
            [occurrence("a.py", "a.py", "a")],
        )
        self.assertEqual(result[0][4], "confirmed")


if __name__ == "__main__":
    unittest.main()
