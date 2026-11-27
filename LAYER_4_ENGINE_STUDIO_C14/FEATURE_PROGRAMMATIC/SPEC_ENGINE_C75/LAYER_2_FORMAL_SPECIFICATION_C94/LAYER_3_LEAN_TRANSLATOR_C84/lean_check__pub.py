import json
import subprocess
import tempfile
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

_capture = ContextVar('lean_evidence', default=None)


@contextmanager
def capture_lean_json():
    programs = []
    token = _capture.set(programs)
    try:
        yield programs
    finally:
        _capture.reset(token)


def _reject_json_constant(token):
    raise ValueError(f'Non-JSON numeric constant: {token}')


def run_lean_json(program, lean, *, parse_float=float):
    try:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'Comparison.lean'
            path.write_text(program, encoding='utf-8')
            result = subprocess.run([str(lean), str(path)], capture_output=True, text=True,
                                    timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError(f'Lean comparison failed: {error}') from error
    if result.returncode:
        raise ValueError('Lean comparison failed: ' + (result.stderr + result.stdout)[:2000])
    try:
        output = json.loads(result.stdout, parse_float=parse_float, parse_constant=_reject_json_constant)
    except ValueError as error:
        raise ValueError('invalid Lean output: ' + result.stdout[:2000]) from error
    if (programs := _capture.get()) is not None:
        programs.append({'program': program, 'stdout': result.stdout})
    return output
