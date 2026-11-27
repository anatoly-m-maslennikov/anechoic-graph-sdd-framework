"""Add the beta Code Unit projection to an existing Realization Graph capture."""

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path, PurePosixPath
import subprocess

from ARCHITECTURE_ANALYSIS_C73.CODE_AND_SPEC_METRICS_C76.metrics__shared import code_rows
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import run_graph_build

from .python_code_units import python_code_units
from .python_context_restoration import python_context_restoration
from .python_import_order import python_import_order
from .web_export_aliases import web_export_aliases
from .web_import_review import web_import_review


def _imports(sources, occurrences):
    matches = defaultdict(lambda: defaultdict(set))
    for _, source, target, written, line, _, status, type_only in occurrences:
        path = source.removeprefix('module:')
        if path in sources and not type_only:
            module = target.removeprefix('module:') if status == 'internal' and target else None
            matches[path][line, written].add(module if module in sources else None)
    return {
        path: {key: next(iter(targets)) for key, targets in sites.items() if len(targets) == 1 and None not in targets}
        for path, sites in matches.items()
    }


def _web_code_units(sources, imports):
    script = Path(__file__).with_name('web_code_units.ts')
    links = {path: [[line, written, target] for (line, written), target in sites.items()]
             for path, sites in imports.items() if path in sources}
    env = {key: value for key, value in os.environ.items() if key not in {'NODE_OPTIONS', 'NODE_PATH'}}
    timeout = None if env.get('ANECHOIC_TEST_IMAGE_DEADLINES') == '0' else 60
    try:
        result = subprocess.run(['node', str(script)], input=json.dumps({'sources': sources, 'imports': links}),
                                text=True, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as error:
        raise ValueError('Code Unit scanner exceeded its 60-second timeout') from error
    if result.returncode:
        raise ValueError(f'Code Unit scanner failed: {result.stderr.strip()}')
    return json.loads(result.stdout)


def _owner(path, ownership):
    if ownership is not None and (owner := ownership.owner(path)) is not None:
        return owner['id']
    return PurePosixPath(path).parent.as_posix()


def _exported_state(web, occurrences, ownership):
    for path, line, column, target, name in web_export_aliases(web, occurrences):
        if target is None:
            yield path, line, column, 'web_exported_state', 'unresolved', f'Owner of {name} is unresolved'
        elif (owner := _owner(target, ownership)) != _owner(path, ownership):
            yield path, line, column, 'web_exported_state', 'confirmed', f'Write to {target}:{name} owned by {owner}'


def _derive_rows(root, sources, occurrences, read_source, ownership):
    python, web = {}, {}
    for path, source in sources.items():
        if source.status == 'parsed' and source.language == 'python':
            python[path] = read_source(path)
        elif source.status == 'parsed' and source.language in {'javascript', 'typescript'}:
            web[path] = read_source(path)
    imports = _imports(python | web, occurrences)
    units, calls = python_code_units(python, imports)
    findings = [*python_import_order(python, occurrences), *python_context_restoration(python)]
    if web:
        web_units, web_calls = _web_code_units(web, imports)
        units.extend(web_units)
        calls.extend(web_calls)
        findings.extend(web_import_review(root, web, occurrences))
        findings.extend(_exported_state(web, occurrences, ownership))
    return {'code_units': units, 'code_unit_calls': calls, 'antipattern_findings': findings}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--watcher-replay', action='store_true', help=argparse.SUPPRESS)
    raise SystemExit(run_graph_build(_derive_rows, code_rows, watcher_replay=parser.parse_args().watcher_replay))
