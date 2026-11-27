"""Translate selected implementation source files to Lean."""

import argparse
import os
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

_JOERN_LANGUAGES = {
    '.py': 'PYTHONSRC',
    '.js': 'JAVASCRIPT',
    '.jsx': 'JAVASCRIPT',
    '.ts': 'JAVASCRIPT',
    '.tsx': 'JAVASCRIPT',
}


def _configured_directory(variable):
    value = os.environ.get(variable)
    if not value or not Path(value).is_dir():
        raise ValueError(f'{variable} must point to an installed tool directory')
    return Path(value).resolve()


def _run(stage, command, directory, env=None):
    try:
        subprocess.run(command, cwd=directory, env=env, check=True, timeout=600,
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    except subprocess.CalledProcessError as error:
        details = (error.stderr + error.stdout).strip()[-2000:]
        raise ValueError(f'{stage} failed (exit {error.returncode}): {details}') from error
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError(f'{stage} failed: {error}') from error


def _autoform(source_root, language, output, directory):
    joern = _configured_directory('JOERN_HOME')
    cartographer = _configured_directory('AUTOFORM_CHECKOUT') / 'cartographer'
    cpg = directory / 'cpg.bin'
    ast = directory / 'ast.json'
    java_options = os.environ.get('JAVA_TOOL_OPTIONS', '')
    env = os.environ | {'JAVA_TOOL_OPTIONS': f'{java_options} -Dfile.encoding=UTF-8'.strip()}
    env.setdefault('AUTOFORM_PYTHON', sys.executable)
    frontend = ['--language', language] if language else []
    _run('Joern parse', [joern / 'joern-parse', source_root, *frontend, '--output', cpg],
         directory, env)
    _run('Autoform export', [joern / 'joern', '--script', cartographer / 'export_ast.sc',
                            '--param', f'cpgPath={cpg}', '--param', f'out={ast}',
                            '--param', 'dataModel=lp64'], directory, env)
    if not ast.is_file():
        raise ValueError('Autoform export produced no AST')
    _run('Autoform render', [sys.executable, '-B', cartographer / 'render_lean.py',
                            ast, output, 'Implementation'], directory)


def _pastalean(source, output, directory):
    if source.suffix.lower() != '.py':
        raise ValueError('PastaLean accepts Python source files only')
    executable = shutil.which('pastalean')
    if executable is None:
        raise ValueError('PastaLean requires the pastalean executable on PATH')
    _run('PastaLean translation', [executable, 'translate', source, '--strict', '--heap',
                                  '--mode', 'run', '--no-check', '--output', output], directory)


def _stage_sources(sources, inputs, digests):
    if digests and len(digests) != len(sources):
        raise ValueError('supply one SHA-256 per source in source order')
    root = Path(os.path.commonpath([source.parent for source in sources]))
    for index, source in enumerate(sources):
        relative = source.relative_to(root)
        content = source.read_bytes()
        if digests and sha256(content).hexdigest() != digests[index]:
            raise ValueError(f'implementation source digest changed: {relative.as_posix()}')
        target = inputs / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='Autoform needs AUTOFORM_CHECKOUT and JOERN_HOME. '
               'PastaLean needs its executable on PATH.',
    )
    parser.add_argument('source', type=Path, nargs='+',
                        help='implementation files, in one language for Autoform')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--sha256', action='append', help='required source digest, repeated in source order')
    parser.add_argument('--translator', choices=('autoform', 'pastalean'), default='autoform',
                        help='Autoform is the default. PastaLean is opt-in and Python-only.')
    args = parser.parse_args()
    try:
        sources = [path.resolve(strict=True) for path in args.source]
        if any(not source.is_file() or source.suffix == '.lean' for source in sources):
            raise ValueError('source must be an implementation file')
        if args.output.suffix != '.lean' or args.output.resolve() in sources:
            raise ValueError('output must be a separate .lean file')
        languages = {_JOERN_LANGUAGES.get(source.suffix.lower()) for source in sources}
        if len(sources) > 1:
            if args.translator == 'pastalean':
                raise ValueError('PastaLean accepts one source file')
            if len(languages) != 1 or None in languages:
                raise ValueError('Autoform source files must use one supported language')
        with TemporaryDirectory(prefix='anechoic-code-to-lean-') as temp:
            directory = Path(temp)
            inputs = directory / 'source'
            _stage_sources(sources, inputs, args.sha256)
            generated = directory / 'Implementation.lean'
            if args.translator == 'autoform':
                _autoform(inputs, next(iter(languages)), generated, directory)
            else:
                _pastalean(inputs / sources[0].name, generated, directory)
            if not generated.is_file() or generated.stat().st_size == 0:
                raise ValueError(f'{args.translator} produced no Lean source')
            shutil.copyfile(generated, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f'code-to-lean: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
