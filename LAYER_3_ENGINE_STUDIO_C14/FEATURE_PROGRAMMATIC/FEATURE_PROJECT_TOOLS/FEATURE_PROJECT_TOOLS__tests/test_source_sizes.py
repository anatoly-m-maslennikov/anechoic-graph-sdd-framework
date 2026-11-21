"""Check source size limits in the Project test suite."""

import ast
import json
import subprocess
import tokenize
import unittest

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import (
    source_comments as sources,
)

MODULE_LIMIT = 300
FUNCTION_LIMIT = 25
WEB_FUNCTIONS = {".js", ".mjs", ".ts", ".svelte"}


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
        findings, web = [], []
        for relative in sources.source_paths(root):
            if relative.suffix not in sources.WEB_SUFFIXES | {".py"}:
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
        source = "\n" * 2 + "@decorator\nasync def run():\n" + "\n" * 22 + "    pass\n"
        self.assertEqual([], check_functions("example.py", python_functions("example.py", source)))
        longer = source.replace("    pass", "\n    pass")
        self.assertEqual(
            ["example.py:3: run has 26 lines (maximum 25)"],
            check_functions("example.py", python_functions("example.py", longer)),
        )

    def test_class_can_contain_many_short_methods(self):
        source = "class Example:\n" + "".join(
            f"    def method_{index}(self):\n        pass\n" for index in range(20)
        )
        functions = list(python_functions("example.py", source))
        self.assertEqual(20, len(functions))
        self.assertEqual([], check_functions("example.py", functions))

    def test_web_function_limit_in_svelte_script(self):
        arrow = "const run = () => {\n" + "\n" * 23 + "};"
        files = [{"path": "exact.ts", "source": arrow},
                 {"path": "over.svelte", "source": "<script>\n" + arrow + "\n</script>"}]
        files[1]["source"] = files[1]["source"].replace("};", "\n};")
        exact, over = web_functions(sources.ROOT, files)
        self.assertEqual([], check_functions("exact.ts", exact))
        self.assertEqual(1, len(check_functions("over.svelte", over)))
        self.assertEqual((2, 26), (over[0][0], over[0][2]))
