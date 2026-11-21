"""Check source size limits in the Project test suite."""

import ast
import json
import subprocess
import tokenize
import tomllib
import unittest

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import (
    source_comments as sources,
)

MODULE_LIMIT = 300
FUNCTION_LIMIT = 45
WEB_FUNCTIONS = {".js", ".mjs", ".ts"}


def module_lines(source):
    return source.count("\n") + bool(source and not source.endswith("\n"))


def python_functions(path, source):
    for node in ast.walk(ast.parse(source, filename=str(path))):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = min([node.lineno, *(item.lineno for item in node.decorator_list)])
            yield start, node.name, node.end_lineno - start + 1
        elif isinstance(node, ast.Lambda):
            yield node.lineno, "<lambda>", node.end_lineno - node.lineno + 1


def web_functions(root, files):
    result = subprocess.run(
        ["node", str(root / sources.FRONTEND / "scripts/source-function-sizes.mjs")],
        input=json.dumps(files), encoding="utf-8", stdout=subprocess.PIPE, check=True,
    )
    return json.loads(result.stdout)


def check_functions(path, functions):
    return [f"{path}:{line}: {name} has {size} lines (maximum {FUNCTION_LIMIT})"
            for line, name, size in sorted(functions) if size > FUNCTION_LIMIT]


class SourceSizeTests(unittest.TestCase):
    def test_source_sizes(self):
        root = sources.ROOT
        with (root / "pyproject.toml").open("rb") as file:
            enabled = tomllib.load(file)["tool"]["anechoic"]["test_suite"]["enforce_source_size"]
        self.assertIsInstance(enabled, bool)
        if not enabled:
            self.skipTest("Source size enforcement is disabled in pyproject.toml")
        findings, web = [], []
        for relative in sources.source_paths(root):
            if relative.suffix not in WEB_FUNCTIONS | {".py"}:
                continue
            path = root / relative
            if path.resolve() != path:
                self.fail(f"{relative}: source path traverses a symbolic link")
            if not path.is_file():
                continue
            if path.suffix == ".py":
                with tokenize.open(path) as file:
                    source = file.read()
                findings.extend(check_functions(relative, python_functions(relative, source)))
            else:
                source = path.read_text(encoding="utf-8")
            size = module_lines(source)
            if size > MODULE_LIMIT:
                findings.append(f"{relative}: module has {size} lines (maximum {MODULE_LIMIT})")
            if path.suffix in WEB_FUNCTIONS:
                web.append({"path": relative.as_posix(), "source": source})
        for file, functions in zip(web, web_functions(root, web), strict=True):
            findings.extend(check_functions(file["path"], functions))
        if findings:
            self.fail("\n".join([f"{len(findings)} source size violations", *findings]))

    def test_module_counts_physical_lines(self):
        self.assertEqual(MODULE_LIMIT, module_lines("\n" * MODULE_LIMIT))
        self.assertEqual(MODULE_LIMIT + 1, module_lines("\n" * MODULE_LIMIT + "x"))
        self.assertEqual(1, module_lines('value = "a\fb"'))
        self.assertEqual(0, module_lines(""))

    def test_python_function_limit_includes_decorators(self):
        source = "\n" * 2 + "@decorator\nasync def run():\n" + "\n" * 42 + "    pass\n"
        self.assertEqual([], check_functions("example.py", python_functions("example.py", source)))
        longer = source.replace("    pass", "\n    pass")
        self.assertEqual(
            ["example.py:3: run has 46 lines (maximum 45)"],
            check_functions("example.py", python_functions("example.py", longer)),
        )

    def test_class_can_contain_many_short_methods(self):
        source = "class Example:\n" + "".join(
            f"    def method_{index}(self):\n        pass\n" for index in range(25)
        )
        functions = list(python_functions("example.py", source))
        self.assertEqual(25, len(functions))
        self.assertEqual([], check_functions("example.py", functions))

    def test_javascript_and_typescript_function_limit(self):
        arrow = "const run = () => {\n" + "\n" * 43 + "};"
        files = [{"path": "exact.ts", "source": arrow},
                 {"path": "over.js", "source": arrow.replace("};", "\n};")}]
        exact, over = web_functions(sources.ROOT, files)
        self.assertEqual([], check_functions("exact.ts", exact))
        self.assertEqual(
            ["over.js:1: run has 46 lines (maximum 45)"], check_functions("over.js", over),
        )
