"""Find statically recognizable writes through named web module imports.

Only named value imports and chains of simple const aliases are followed.
The owner must directly export an object or array literal. Computed property
names, destructuring, re-exports and calls are deliberately outside this scan.
"""

import json
import os
from pathlib import Path
import subprocess


def web_export_aliases(texts, occurrences):
    """Return property-write locations and their owner, if uniquely known."""
    imports = {}
    for _, source, target, written, line, _, status, type_only in occurrences:
        if type_only or not source.startswith('module:'):
            continue
        source = source.removeprefix('module:')
        if source not in texts:
            continue
        owner = target.removeprefix('module:') if status == 'internal' and target and target.startswith('module:') else None
        if owner not in texts:
            owner = None
        imports.setdefault(source, {}).setdefault((line, written), set()).add(owner)
    links = {source: [[line, written, next(iter(owners)) if len(owners) == 1 else None]
                      for (line, written), owners in sites.items()]
             for source, sites in imports.items()}
    env = {key: value for key, value in os.environ.items() if key not in {'NODE_OPTIONS', 'NODE_PATH'}}
    timeout = None if env.get('ANECHOIC_TEST_IMAGE_DEADLINES') == '0' else 60
    script = Path(__file__).with_suffix('.mjs')
    try:
        result = subprocess.run(['node', str(script)], input=json.dumps({'sources': texts, 'imports': links}),
                                text=True, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as error:
        raise ValueError('Web export alias scanner exceeded its 60-second timeout') from error
    if result.returncode:
        raise ValueError(f'Web export alias scanner failed: {result.stderr.strip()}')
    return [tuple(row) for row in json.loads(result.stdout)]
