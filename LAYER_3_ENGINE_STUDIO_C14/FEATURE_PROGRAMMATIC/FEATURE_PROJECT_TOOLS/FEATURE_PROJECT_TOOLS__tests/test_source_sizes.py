"""Check source size limits in the Project test suite."""

import ast
import json
import subprocess
import tokenize
import tomllib
import unittest

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS \
    import source_comments as sources

MODULE_LIMIT = 300
FUNCTION_LIMIT = 45
LINE_LIMIT = 79
WEB_FUNCTIONS = {".js", ".mjs", ".ts"}


def nonblank_lines(lines):
    return sum(bool(line.strip()) for line in lines)


def check_module(path, source):
    lines = source.split("\n")
    size = nonblank_lines(lines)
    if size > MODULE_LIMIT:
        yield f"{path}: module has {size} lines (maximum {MODULE_LIMIT})"
    for number, line in enumerate(lines, 1):
        width = len(line.expandtabs())
        if width > LINE_LIMIT and line.strip():
            yield (
                f"{path}:{number}: line has {width} columns "
                f"(maximum {LINE_LIMIT})"
            )


def python_functions(path, source):
    lines = source.split("\n")
    for node in ast.walk(ast.parse(source, filename=str(path))):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = [item.lineno for item in node.decorator_list]
            start = min([node.lineno, *decorators])
            size = nonblank_lines(lines[start - 1:node.end_lineno])
            yield start, node.name, size
        elif isinstance(node, ast.Lambda):
            size = nonblank_lines(lines[node.lineno - 1:node.end_lineno])
            yield node.lineno, "<lambda>", size


def web_functions(root, files):
    script = sources.FRONTEND / "scripts/source-function-sizes.mjs"
    result = subprocess.run(
        ["node", str(root / script)],
        input=json.dumps(files), encoding="utf-8",
        stdout=subprocess.PIPE, check=True,
    )
    return json.loads(result.stdout)


def check_functions(path, functions):
    return [
        f"{path}:{line}: {name} has {size} lines (maximum {FUNCTION_LIMIT})"
        for line, name, size in sorted(functions) if size > FUNCTION_LIMIT
    ]


class SourceSizeTests(unittest.TestCase):
    def test_source_sizes(self):
        root = sources.ROOT
        with (root / "pyproject.toml").open("rb") as file:
            settings = tomllib.load(file)["tool"]["anechoic"]["test_suite"]
        self.assertIsInstance(settings["enforce_source_size"], bool)
        if not settings["enforce_source_size"]:
            self.skipTest("Source size lint is disabled in pyproject.toml")
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
                findings.extend(check_functions(
                    relative, python_functions(relative, source)
                ))
            else:
                source = path.read_text(encoding="utf-8")
            findings.extend(check_module(relative, source))
            if path.suffix in WEB_FUNCTIONS:
                web.append({"path": relative.as_posix(), "source": source})
        for file, functions in zip(web, web_functions(root, web), strict=True):
            findings.extend(check_functions(file["path"], functions))
        if findings:
            summary = f"{len(findings)} source size violations"
            self.fail("\n".join([summary, *findings]))

    def test_module_ignores_blank_lines(self):
        source = 'value = "a\fb"\n\n \t\n' * 300
        self.assertEqual([], list(check_module("example.py", source)))
        self.assertEqual(
            ["example.py: module has 301 lines (maximum 300)"],
            list(check_module("example.py", source + "x")),
        )

    def test_line_width_limit(self):
        source = "x" * 79 + "\n\t" + "x" * 72
        self.assertEqual(
            ["example.ts:2: line has 80 columns (maximum 79)"],
            list(check_module("example.ts", source)),
        )

    def test_python_function_limit_includes_decorators(self):
        path = "example.py"
        body = "    pass\n\n    \n" * 43
        source = "\n\n@decorator\nasync def run():\n" + body
        self.assertEqual(
            [], check_functions(path, python_functions(path, source)),
        )
        longer = source + "    pass\n"
        self.assertEqual(
            ["example.py:3: run has 46 lines (maximum 45)"],
            check_functions(path, python_functions(path, longer)),
        )

    def test_class_can_contain_many_short_methods(self):
        source = "class Example:\n" + "".join(
            f"    def method_{index}(self):\n        pass\n"
            for index in range(25)
        )
        functions = list(python_functions("example.py", source))
        self.assertEqual(25, len(functions))
        self.assertEqual([], check_functions("example.py", functions))

    def test_javascript_and_typescript_function_limit(self):
        arrow = "const run = () => {\n" + "  void 0;\n\n  \n" * 43 + "};"
        longer = arrow.replace("};", "  void 0;\n};")
        files = [
            {"path": "exact.ts", "source": arrow},
            {"path": "over.js", "source": longer},
        ]
        exact, over = web_functions(sources.ROOT, files)
        self.assertEqual([], check_functions("exact.ts", exact))
        self.assertEqual(
            ["over.js:1: run has 46 lines (maximum 45)"],
            check_functions("over.js", over),
        )
