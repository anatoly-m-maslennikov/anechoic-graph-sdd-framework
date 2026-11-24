"""Profile a Beta generation from an explicit native Project binding."""
import argparse
import cProfile
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import owned_temporary_root
from WORKERS_beta_C69 import WORKERS_beta_C69__shared as worker


def child(module, directory, arguments):
    calls = []
    original = subprocess.run

    def run(*args, **kwargs):
        start = time.perf_counter()
        try:
            return original(*args, **kwargs)
        finally:
            calls.append({'executable': Path(str(args[0][0])).name,
                          'script': Path(str(args[0][1])).name if len(args[0]) > 1 else None,
                          'wall_seconds': time.perf_counter() - start})

    profile = cProfile.Profile(time.process_time_ns, 1e-9)
    try:
        with patch.object(subprocess, 'run', run):
            sys.argv = [module, *arguments]
            profile.runcall(runpy.run_module, module, run_name='__main__')
    finally:
        profile.dump_stats(str(directory / (module.rsplit('.', 1)[-1] + '.pstats')))
        (directory / (module.rsplit('.', 1)[-1] + '-children.json')).write_text(json.dumps(calls))


def instrument(directory, stages):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import ADAPTERS_C30__shared as adapter

    original_prepare = adapter.prepare_generation_snapshot
    engine = Path(worker.__file__).resolve().parents[1]

    def measure(name, call, *args, **kwargs):
        wall, cpu = time.perf_counter(), time.process_time()
        try:
            return call(*args, **kwargs)
        finally:
            stages.append({'stage': name, 'wall_seconds': time.perf_counter() - wall,
                           'worker_cpu_seconds': time.process_time() - cpu})

    def prepare(*args, **kwargs):
        config, finish = measure('capture_prepare', original_prepare, *args, **kwargs)
        return config, lambda *a, **kw: measure('capture_finish', finish, *a, **kw)

    def job(module, payload, *arguments):
        name = module.rsplit('.', 1)[-1]
        env = {key: value for key, value in os.environ.items() if key != 'PYTHONHOME'}
        env['PYTHONPATH'] = str(engine)
        command = [sys.executable, '-B', str(Path(__file__).resolve()), '--child', module,
                   '--child-output', str(directory), *arguments]
        result = subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True,
                                cwd=engine, env=env)
        (directory / (name + '-stderr.txt')).write_text(result.stderr)
        if result.returncode:
            raise worker._BuildFailure(name, f'{name} failed: {result.stderr[-2048:]}')
        return json.loads(result.stdout)

    def timed_job(module, payload, *arguments):
        return measure(module.rsplit('.', 1)[-1], job, module, payload, *arguments)

    return adapter, prepare, timed_job


def profile(binding, directory, foreground=False):
    stages = []
    adapter, prepare, timed_job = instrument(directory, stages)
    output = directory / 'generation'
    output.mkdir()
    report = {'binding': binding, 'foreground': foreground, 'stages': stages,
              'worker_source_sha256': sha256(Path(worker.__file__).read_bytes()).hexdigest(),
              'cpu_scope': 'worker process only; child Python CPU is in its pstats',
              'status': 'failed'}
    profiler = cProfile.Profile(time.process_time_ns, 1e-9)
    wall, cpu = time.perf_counter(), time.process_time()
    try:
        with patch.object(adapter, 'prepare_generation_snapshot', prepare), patch.object(worker, '_run_job', timed_job):
            result = profiler.runcall(worker._run, {'binding': binding, 'reuse': None,
                                                   'foreground': foreground}, output)
        report['status'] = 'ok'
        report['snapshot_counts'] = {key: len(value) for key, value in result['snapshot'].items()
                                     if isinstance(value, list)}
    except BaseException:
        (directory / 'failure.txt').write_text(traceback.format_exc())
        raise
    finally:
        report['total_wall_seconds'] = time.perf_counter() - wall
        report['total_worker_cpu_seconds'] = time.process_time() - cpu
        profiler.dump_stats(str(directory / 'worker.pstats'))
        (directory / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def select_project(root, directory):
    module = 'FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.project_admission__pub'
    request = {'project_root': str(root), 'control_root': None, 'instance_id': None, 'host_root': None}
    result = subprocess.run([sys.executable, '-B', '-m', module], input=json.dumps(request) + '\n',
                            text=True, capture_output=True)
    (directory / 'admission-stderr.txt').write_text(result.stderr)
    result.check_returncode()
    response = json.loads(result.stdout)
    if 'error' in response:
        raise ValueError(str(response['error']))
    selected = response['result']
    return {'root': selected['root'], 'control_root': selected['control_relative'],
            'manifest_path': Path(selected['manifest_path']).relative_to(selected['root']).as_posix(),
            'manifest_sha256': selected['manifest_sha256'], 'project_prefix': selected['project_prefix']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, help='Project root to admit and profile')
    parser.add_argument('--binding', type=Path, help='existing native Worker binding JSON')
    parser.add_argument('--foreground', action='store_true', help='capture foreground with deferred Archive')
    parser.add_argument('--child', help=argparse.SUPPRESS)
    parser.add_argument('--child-output', type=Path, help=argparse.SUPPRESS)
    args, rest = parser.parse_known_args()
    if args.child:
        child(args.child, args.child_output, rest)
        return
    if bool(args.binding) == bool(args.project_root) or rest:
        parser.error('supply exactly one of --project-root and --binding')
    binding = json.loads(args.binding.read_text()) if args.binding else None
    root = Path(binding['root'] if binding else args.project_root).resolve(strict=True)
    import tempfile
    directory = Path(tempfile.mkdtemp(prefix='generation-', dir=owned_temporary_root(root, 'beta-profile')))
    print(directory, flush=True)
    try:
        binding = binding or select_project(root, directory)
        profile(binding, directory, args.foreground)
    except Exception:
        if not (directory / 'failure.txt').exists():
            (directory / 'failure.txt').write_text(traceback.format_exc())
        raise


if __name__ == '__main__':
    main()
