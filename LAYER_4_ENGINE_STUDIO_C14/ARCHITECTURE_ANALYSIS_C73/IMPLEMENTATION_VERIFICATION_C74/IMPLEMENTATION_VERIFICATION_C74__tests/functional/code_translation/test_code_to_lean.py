"""Exercise translator selection through the command-line entry point."""

import hashlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.\
    IMPLEMENTATION_VERIFICATION_C74__tests.functional.code_translation.\
    _code_to_lean_helpers import _calls, _run, _tool, _tools, _translate


class CodeToLeanTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)
        self.env, self.log = _tools(self.folder)

    def _source(self, name, content="def f():\n    return 1\n"):
        source = self.folder / name
        source.parent.mkdir(exist_ok=True, parents=True)
        source.write_text(content)
        return source

    def test_default_uses_autoform(self):
        for suffix, frontend in [
            (".py", "PYTHONSRC"),
            (".js", "JAVASCRIPT"),
            (".ts", "JAVASCRIPT"),
        ]:
            with self.subTest(suffix=suffix):
                self.log.unlink(missing_ok=True)
                result, output = _run(self.folder, self.env, suffix)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    output.read_text().strip(), "-- autoform result"
                )
                calls = _calls(self.log)
                self.assertEqual(
                    [call[0] for call in calls],
                    ["joern-parse", "joern", "render_lean.py"],
                )
                self.assertFalse(Path(self.env["TEST_LOOKUPS"]).exists())
                self.assertEqual(
                    calls[0][calls[0].index("--language") + 1], frontend
                )

    def test_autoform_preserves_the_tree_of_selected_files(self):
        _tool(
            Path(self.env["JOERN_HOME"]) / "joern-parse",
            "import json, os, sys\nfrom pathlib import Path\n"
            "root = Path(sys.argv[1])\n"
            "with open(os.environ['TEST_CALLS'], 'a') as log:\n"
            "    log.write(json.dumps({p.rela"
            "tive_to(root).as_posix(): p.read"
            "_text() "
            "for p in root.rglob('*.py')}) + '\\n')\n",
        )
        sources = {
            "consumer/spec.py": "from ..provider.source import value\n",
            "provider/source.py": "value = 1\n",
            "provider/extra.py": "unused = 2\n",
        }
        for file, content in sources.items():
            self._source(file, content)
        wanted = {
            key: sources[key]
            for key in ("consumer/spec.py", "provider/source.py")
        }
        result, output = _translate(
            self.folder, self.env, [self.folder / key for key in wanted]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(_calls(self.log)[0], wanted)
        self.assertEqual(output.read_text().strip(), "-- autoform result")

    def test_autoform_rejects_relative_import_aliases_before_translation(self):
        cases = (
            (
                "spec.py",
                ".child._package__shared",
                "child/_package__shared",
                "_package__shared.py",
            ),
            (
                "pkg/spec.py",
                ".child.shared",
                "pkg/child/shared",
                "child/shared/__init__.py",
            ),
            ("pkg/sub/spec.py", ".", "pkg/sub", "sub/__init__.py"),
            ("pkg/spec.py", "...shared", "../shared", "shared.py"),
        )
        for importer, written, requested, candidate in cases:
            with self.subTest(importer=importer, written=written):
                sources = [
                    self._source(importer, f"from {written} import f as g\n"),
                    self._source(candidate),
                ]
                result, output = _translate(self.folder, self.env, sources)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(f"{importer}:1:", result.stderr)
                self.assertIn(f"relative import {written!r}", result.stderr)
                self.assertIn(
                    f"requests {requested!r} but would bind to {candidate!r}",
                    result.stderr,
                )
                self.assertFalse(output.exists())
                self.assertFalse(_calls(self.log))

    def test_autoform_allows_exact_and_unresolved_relative_imports(self):
        importer = self._source(
            "spec.py",
            "from .child.shared import f\n"
            "from .child.package import f\n"
            "from .missing.unknown import f\n"
            "from ..missing.unknown import f\n"
            "from . import unknown\n"
            "from missing.shared import f\n",
        )
        candidates = (
            "child/shared.py",
            "child/package/__init__.py",
            "shared.py",
            "package/__init__.py",
            "__init__.py",
        )
        sources = [importer, *(self._source(path) for path in candidates)]
        result, output = _translate(self.folder, self.env, sources)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_text(), "-- autoform result\n")

    def test_autoform_sidecar_uses_the_engine_python_by_default(self):
        _tool(
            Path(self.env["JOERN_HOME"]) / "joern",
            "import os, shutil, sys\nfrom pathlib import Path\n"
            "out = next(arg[4:] for arg in sy"
            "s.argv if arg.startswith('out=')"
            ")\n"
            "python = os.environ.get('AUTOFOR"
            "M_PYTHON') or shutil.which('pyth"
            "on3')\n"
            "Path(os.environ['TEST_CALLS']).w"
            "ith_suffix('.python').write_text"
            "(python)\n"
            "Path(out).write_text('{}')\n",
        )
        fallback = self.folder / "bin" / "python3"
        _tool(fallback, "raise SystemExit(42)\n")
        interpreter_log = self.log.with_suffix(".python")
        self.env.pop("AUTOFORM_PYTHON", None)
        result, _ = _run(self.folder, self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(interpreter_log.read_text(), sys.executable)
        result, _ = _run(
            self.folder, {**self.env, "AUTOFORM_PYTHON": str(fallback)}
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(interpreter_log.read_text(), str(fallback))

    def test_incompatible_source_groups_stop_before_translation(self):
        first, second = self.folder / "first.py", self.folder / "second.js"
        first.touch()
        second.touch()
        for translator, message in (
            ("autoform", "one supported language"),
            ("pastalean", "one source file"),
        ):
            with self.subTest(translator=translator):
                result, output = _translate(
                    self.folder, self.env, [first, second], translator
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertFalse(output.exists())
                self.assertFalse(_calls(self.log))

    def test_translate_only_the_pinned_source_bytes(self):
        sources = [self.folder / name for name in ("first.py", "second.py")]
        for index, source in enumerate(sources):
            source.write_text(f"value = {index}\n")
        digests = [
            hashlib.sha256(source.read_bytes()).hexdigest()
            for source in sources
        ]
        result, output = _translate(
            self.folder, self.env, sources, digests=digests
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        before = output.read_bytes()
        self.log.unlink()
        sources[1].write_text("value = 2\n")
        for expected, reason in (
            (digests[:1], "one SHA-256 per source"),
            (digests, "source digest changed"),
        ):
            with self.subTest(reason=reason):
                result, _ = _translate(
                    self.folder, self.env, sources, digests=expected
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(reason, result.stderr)
                self.assertEqual(output.read_bytes(), before)
                self.assertFalse(_calls(self.log))

    def test_pastalean_requires_explicit_opt_in(self):
        result, output = _run(self.folder, self.env, translator="pastalean")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_text().strip(), "-- pastalean result")
        (call,) = _calls(self.log)
        self.assertEqual(call[:2], ["pastalean", "translate"])
        self.assertEqual(Path(call[2]).name, "input.py")
        self.assertEqual(
            call[3:9],
            ["--strict", "--heap", "--mode", "run", "--no-check", "--output"],
        )
        self.assertNotEqual(call[9], str(output))

    def test_pastalean_rejects_non_python(self):
        for suffix in (".js", ".ts"):
            with self.subTest(suffix=suffix):
                result, output = _run(
                    self.folder, self.env, suffix, "pastalean"
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Python", result.stderr)
                self.assertFalse(output.exists())
                self.assertFalse(_calls(self.log))

    def test_autoform_failure_has_no_fallback_or_artifact(self):
        _tool(
            Path(self.env["JOERN_HOME"]) / "joern-parse",
            (
                "import sys\nprint('parse failed', "
                "file=sys.stderr)\nsys.exit(3)\n"
            ),
        )
        result, output = _run(self.folder, self.env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("parse failed", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(_calls(self.log))

    def test_pastalean_failure_leaves_no_output(self):
        _tool(
            self.folder / "bin" / "pastalean",
            "import sys\nfrom pathlib import Path\n"
            "Path(sys.argv[sys.argv.index('--"
            "output') + 1]).write_text('parti"
            "al')\n"
            "print('translation failed', file=sys.stderr)\nsys.exit(2)\n",
        )
        result, output = _run(self.folder, self.env, translator="pastalean")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("translation failed", result.stderr)
        self.assertFalse(output.exists())
