import json
import subprocess
import tempfile
from pathlib import Path


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
        return json.loads(result.stdout, parse_float=parse_float)
    except json.JSONDecodeError as error:
        raise ValueError('invalid Lean output: ' + result.stdout[:2000]) from error
