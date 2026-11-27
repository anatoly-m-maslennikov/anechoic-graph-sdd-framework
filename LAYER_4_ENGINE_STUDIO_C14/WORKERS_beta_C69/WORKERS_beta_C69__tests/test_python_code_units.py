import unittest
from textwrap import dedent

from WORKERS_beta_C69.WORKERS_beta_C69__shared import python_code_units


class PythonCodeUnitTests(unittest.TestCase):
    def test_calls_and_shadowing(self):
        texts = {
            "dep.py": "def leaf():\n    pass\ndef middle():\n    leaf()\n",
            "main.py": (
                "from dep import middle as run\ndef start():\n    run()\n"
                "def shadow(run):\n    run()\ndef dynamic(obj):\n    obj.run()\n"
            ),
        }
        units, calls = python_code_units(
            texts, {"main.py": {(1, "dep"): "dep.py"}}
        )
        keys = {(u[1], u[3]): u[0] for u in units}
        assert calls == [
            (
                keys["module:dep.py", "middle"],
                keys["module:dep.py", "leaf"],
                4,
                4,
            ),
            (
                keys["module:main.py", "start"],
                keys["module:dep.py", "middle"],
                3,
                4,
            ),
        ]

    def test_static_methods_and_rebinding(self):
        source = dedent("""\
    class Service:
        @staticmethod
        def safe():
            pass
        def dynamic(self):
            pass

    def call(obj):
        Service.safe()
        obj.dynamic()

    def replaced():
        pass
    replaced = other

    def caller():
        replaced()
    """)
        units, calls = python_code_units({"a.py": source}, {})
        keys = {u[3]: u[0] for u in units}
        assert calls == [(keys["call"], keys["Service.safe"], 9, 4)]

    def test_relative_child_module_alias(self):
        texts = {
            "pkg/dep.py": "def leaf():\n    pass\n",
            "pkg/main.py": "from . import dep as target\ndef call():\n    target.leaf()\n",
        }
        units, calls = python_code_units(
            texts, {"pkg/main.py": {(1, "."): "pkg/dep.py"}}
        )
        keys = {(u[1], u[3]): u[0] for u in units}
        self.assertEqual(
            calls,
            [
                (
                    keys["module:pkg/main.py", "call"],
                    keys["module:pkg/dep.py", "leaf"],
                    3,
                    4,
                )
            ],
        )

    def test_nonlocal_rebinding_suppresses_call(self):
        source = (
            "def outer():\n    def target():\n        pass\n"
            "    def replace():\n        nonlocal target\n        target = other\n"
            "    def caller():\n        target()\n"
        )
        _, calls = python_code_units({"a.py": source}, {})
        self.assertEqual(calls, [])
