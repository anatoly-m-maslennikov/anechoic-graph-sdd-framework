"""Conservatively lower JavaScript and TypeScript functions to effect cases."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

_SCANNER = Path(__file__).with_name('web_state_cases.mjs')


def web_state_cases(sources: dict[str, str]) -> dict[str, list[dict]]:
    """Parse a batch without executing source; raise on scanner or protocol failure."""
    if not sources:
        return {}
    env = {k: v for k, v in os.environ.items() if k not in {'NODE_OPTIONS', 'NODE_PATH'}}
    result = subprocess.run(['node', str(_SCANNER)], input=json.dumps(sources), text=True,
                            capture_output=True, timeout=60, env=env)
    if result.returncode:
        raise RuntimeError(f'Web state scanner failed: {result.stderr.strip()}')
    try:
        rows = json.loads(result.stdout)
    except ValueError as error:
        raise RuntimeError(f'Web state scanner returned invalid JSON: {result.stderr.strip()}') from error
    if not isinstance(rows, dict) or set(rows) != set(sources):
        raise RuntimeError('Web state scanner returned an invalid batch')
    return rows
