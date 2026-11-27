"""Exercise translator selection through the command-line entry point."""

import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ENGINE = Path(__file__).resolve().parents[4]
MODULE = 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.code_to_lean'


def _tool(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'#!{sys.executable}\n{body}')
    path.chmod(0o755)


def _tools(tmp_path):
    log = tmp_path / 'calls.jsonl'
    joern = tmp_path / 'joern'
    autoform = tmp_path / 'autoform'
    bin_dir = tmp_path / 'bin'
    record = ("import json, os, sys\n"
              "with open(os.environ['TEST_CALLS'], 'a') as f:\n"
              "    f.write(json.dumps([os.path.basename(sys.argv[0]), *sys.argv[1:]]) + '\\n')\n")
    _tool(joern / 'joern-parse', record)
    _tool(joern / 'joern', record +
          "from pathlib import Path\n"
          "out = next(arg[4:] for arg in sys.argv if arg.startswith('out='))\n"
          "Path(out).write_text('{}')\n")
    _tool(autoform / 'cartographer' / 'render_lean.py',
          record + "from pathlib import Path\n"
          "Path(sys.argv[2]).write_text('-- autoform result\\n')\n")
    (autoform / 'cartographer' / 'export_ast.sc').touch()
    _tool(bin_dir / 'pastalean', record +
          "from pathlib import Path\n"
          "Path(sys.argv[sys.argv.index('--output') + 1]).write_text('-- pastalean result\\n')\n")
    (tmp_path / 'sitecustomize.py').write_text(
        "import os, shutil\n"
        "original = shutil.which\n"
        "def checked(command, *args, **kwargs):\n"
        "    if command == 'pastalean':\n"
        "        open(os.environ['TEST_LOOKUPS'], 'a').write('pastalean\\n')\n"
        "    return original(command, *args, **kwargs)\n"
        "shutil.which = checked\n")
    env = os.environ.copy()
    env.update(AUTOFORM_CHECKOUT=str(autoform), JOERN_HOME=str(joern),
               PATH=str(bin_dir) + os.pathsep + env.get('PATH', ''),
               TEST_CALLS=str(log), TEST_LOOKUPS=str(tmp_path / 'lookups'),
               PYTHONPATH=os.pathsep.join([str(tmp_path), str(ENGINE)]))
    return env, log


def _translate(tmp_path, env, sources, translator=None, digests=()):
    output = tmp_path / 'output.lean'
    args = [sys.executable, '-B', '-m', MODULE, *map(str, sources), '--output', str(output)]
    if translator:
        args += ['--translator', translator]
    for digest in digests:
        args += ['--sha256', digest]
    result = subprocess.run(args, cwd=ENGINE, env=env, capture_output=True,
                            text=True, timeout=45, check=False)
    return result, output


def _run(tmp_path, env, suffix='.py', translator=None):
    source = tmp_path / ('input' + suffix)
    source.write_text('x = 1\n')
    return _translate(tmp_path, env, [source], translator)


def _calls(log):
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


class CodeToLeanTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.folder = Path(directory.name)
        self.env, self.log = _tools(self.folder)

    def test_default_uses_autoform(self):
        for suffix, frontend in [('.py', 'PYTHONSRC'), ('.js', 'JAVASCRIPT'), ('.ts', 'JAVASCRIPT')]:
            with self.subTest(suffix=suffix):
                self.log.unlink(missing_ok=True)
                result, output = _run(self.folder, self.env, suffix)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(output.read_text().strip(), '-- autoform result')
                calls = _calls(self.log)
                self.assertEqual([call[0] for call in calls], ['joern-parse', 'joern', 'render_lean.py'])
                self.assertFalse(Path(self.env['TEST_LOOKUPS']).exists())
                self.assertEqual(calls[0][calls[0].index('--language') + 1], frontend)

    def test_autoform_preserves_the_tree_of_selected_files(self):
        _tool(Path(self.env['JOERN_HOME']) / 'joern-parse',
              "import json, os, sys\nfrom pathlib import Path\n"
              "root = Path(sys.argv[1])\n"
              "with open(os.environ['TEST_CALLS'], 'a') as log:\n"
              "    log.write(json.dumps({p.relative_to(root).as_posix(): p.read_text() "
              "for p in root.rglob('*.py')}) + '\\n')\n")
        sources = {
            'consumer/spec.py': 'from ..provider.source import value\n',
            'provider/source.py': 'value = 1\n',
            'provider/extra.py': 'unused = 2\n',
        }
        for file, content in sources.items():
            path = self.folder / file
            path.parent.mkdir(exist_ok=True)
            path.write_text(content)
        wanted = {key: sources[key] for key in ('consumer/spec.py', 'provider/source.py')}
        result, output = _translate(self.folder, self.env, [self.folder / key for key in wanted])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(_calls(self.log)[0], wanted)
        self.assertEqual(output.read_text().strip(), '-- autoform result')

    def test_autoform_sidecar_uses_the_engine_python_by_default(self):
        _tool(Path(self.env['JOERN_HOME']) / 'joern',
              "import os, shutil, sys\nfrom pathlib import Path\n"
              "out = next(arg[4:] for arg in sys.argv if arg.startswith('out='))\n"
              "python = os.environ.get('AUTOFORM_PYTHON') or shutil.which('python3')\n"
              "Path(os.environ['TEST_CALLS']).with_suffix('.python').write_text(python)\n"
              "Path(out).write_text('{}')\n")
        fallback = self.folder / 'bin' / 'python3'
        _tool(fallback, 'raise SystemExit(42)\n')
        interpreter_log = self.log.with_suffix('.python')
        self.env.pop('AUTOFORM_PYTHON', None)
        result, _ = _run(self.folder, self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(interpreter_log.read_text(), sys.executable)
        result, _ = _run(self.folder, {**self.env, 'AUTOFORM_PYTHON': str(fallback)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(interpreter_log.read_text(), str(fallback))

    def test_incompatible_source_groups_stop_before_translation(self):
        first, second = self.folder / 'first.py', self.folder / 'second.js'
        first.touch()
        second.touch()
        for translator, message in (('autoform', 'one supported language'), ('pastalean', 'one source file')):
            with self.subTest(translator=translator):
                result, output = _translate(self.folder, self.env, [first, second], translator)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertFalse(output.exists())
                self.assertFalse(_calls(self.log))

    def test_translate_only_the_pinned_source_bytes(self):
        sources = [self.folder / name for name in ('first.py', 'second.py')]
        for index, source in enumerate(sources):
            source.write_text(f'value = {index}\n')
        digests = [hashlib.sha256(source.read_bytes()).hexdigest() for source in sources]
        result, output = _translate(self.folder, self.env, sources, digests=digests)
        self.assertEqual(result.returncode, 0, result.stderr)
        before = output.read_bytes()
        self.log.unlink()
        sources[1].write_text('value = 2\n')
        for expected, reason in ((digests[:1], 'one SHA-256 per source'),
                                 (digests, 'source digest changed')):
            with self.subTest(reason=reason):
                result, _ = _translate(self.folder, self.env, sources, digests=expected)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(reason, result.stderr)
                self.assertEqual(output.read_bytes(), before)
                self.assertFalse(_calls(self.log))

    def test_pastalean_requires_explicit_opt_in(self):
        result, output = _run(self.folder, self.env, translator='pastalean')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_text().strip(), '-- pastalean result')
        call, = _calls(self.log)
        self.assertEqual(call[:2], ['pastalean', 'translate'])
        self.assertEqual(Path(call[2]).name, 'input.py')
        self.assertEqual(call[3:9], ['--strict', '--heap', '--mode', 'run', '--no-check', '--output'])
        self.assertNotEqual(call[9], str(output))

    def test_pastalean_rejects_non_python(self):
        for suffix in ('.js', '.ts'):
            with self.subTest(suffix=suffix):
                result, output = _run(self.folder, self.env, suffix, 'pastalean')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Python', result.stderr)
                self.assertFalse(output.exists())
                self.assertFalse(_calls(self.log))

    def test_autoform_failure_has_no_fallback_or_artifact(self):
        _tool(Path(self.env['JOERN_HOME']) / 'joern-parse',
              "import sys\nprint('parse failed', file=sys.stderr)\nsys.exit(3)\n")
        result, output = _run(self.folder, self.env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('parse failed', result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse(_calls(self.log))

    def test_pastalean_failure_leaves_no_output(self):
        _tool(self.folder / 'bin' / 'pastalean',
              "import sys\nfrom pathlib import Path\n"
              "Path(sys.argv[sys.argv.index('--output') + 1]).write_text('partial')\n"
              "print('translation failed', file=sys.stderr)\nsys.exit(2)\n")
        result, output = _run(self.folder, self.env, translator='pastalean')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('translation failed', result.stderr)
        self.assertFalse(output.exists())
