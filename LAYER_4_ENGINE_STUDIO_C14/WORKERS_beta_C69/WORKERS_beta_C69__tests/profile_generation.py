"""Profile a Beta generation from an explicit native Project binding."""
import argparse
import cProfile
from contextlib import contextmanager, redirect_stdout
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time
import traceback
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import owned_temporary_root
WORKER = "WORKERS_beta_C69.WORKERS_beta_C69__shared"
WORKER_SOURCE = Path(__file__).resolve().parents[1] / "WORKERS_beta_C69__shared.py"
PROFILED_CHILDREN = {"WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared", "WORKERS_beta_C69.realization_graph"}
CAPTURE_STAGES = {"prepare_generation_snapshot": "capture_prepare",
                  "prepare_generation_snapshot.<locals>.finish": "capture_finish"}


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


def stage_time(stages, name, started):
    wall, cpu = started
    stages.append({'stage': name, 'wall_seconds': time.perf_counter() - wall,
                   'worker_cpu_seconds': time.process_time() - cpu})


@contextmanager
def capture_timings(stages):
    monitor = sys.monitoring
    tool = 3
    events = monitor.events
    active = {}

    def enter(code, _offset):
        name = CAPTURE_STAGES.get(code.co_qualname)
        if name is None or Path(code.co_filename).name != "native_snapshot_cli.py":
            return monitor.DISABLE
        active.setdefault(code, []).append((time.perf_counter(), time.process_time()))

    def leave(code, _offset, _result):
        if active.get(code):
            stage_time(stages, CAPTURE_STAGES[code.co_qualname], active[code].pop())

    def returned(code, offset, result):
        if code not in active:
            return monitor.DISABLE
        leave(code, offset, result)

    monitor.use_tool_id(tool, "ANECHOIC Worker capture timings")
    callbacks = ((events.PY_START, enter), (events.PY_RETURN, returned), (events.PY_UNWIND, leave))
    try:
        for event, callback in callbacks:
            monitor.register_callback(tool, event, callback)
        monitor.set_events(tool, events.PY_START | events.PY_RETURN | events.PY_UNWIND)
        yield
    finally:
        monitor.set_events(tool, 0)
        for event, _ in callbacks:
            monitor.register_callback(tool, event, None)
        monitor.free_tool_id(tool)


@contextmanager
def profile_children(directory, stages):
    original = subprocess.run

    def run(command, *args, **options):
        if "-m" not in command:
            return original(command, *args, **options)
        index = command.index("-m")
        module = command[index + 1]
        if module not in PROFILED_CHILDREN:
            return original(command, *args, **options)
        profile_command = [*command[:index], str(Path(__file__).resolve()), '--child', module,
                           '--child-output', str(directory), *command[index + 2:]]
        name = module.rsplit('.', 1)[-1]
        started = (time.perf_counter(), time.process_time())
        try:
            result = original(profile_command, *args, **options)
            (directory / (name + '-stderr.txt')).write_text(result.stderr)
            return result
        finally:
            stage_time(stages, name, started)

    with patch.object(subprocess, 'run', run):
        yield


def run_worker(binding, output, foreground):
    argv = [WORKER, "--generation-dir", str(output)]
    request = {"binding": binding, "reuse": None, "foreground": foreground}
    stdout = StringIO()
    with patch.object(sys, 'argv', argv), patch.object(sys, 'stdin', StringIO(json.dumps(request))), redirect_stdout(stdout):
        try:
            runpy.run_module(WORKER, run_name="__main__")
        except SystemExit as requested:
            if requested.code:
                diagnostic = stdout.getvalue().strip()
                raise RuntimeError(f"Worker exited with status {requested.code}: {diagnostic}") from requested
    return json.loads(stdout.getvalue())


def profile(binding, directory, foreground=False):
    stages = []
    output = directory / 'generation'
    output.mkdir()
    report = {'binding': binding, 'foreground': foreground, 'stages': stages,
              'worker_source_sha256': sha256(WORKER_SOURCE.read_bytes()).hexdigest(),
              'cpu_scope': 'worker process only; child Python CPU is in its pstats',
              'status': 'failed'}
    profiler = cProfile.Profile(time.process_time_ns, 1e-9)
    wall, cpu = time.perf_counter(), time.process_time()
    try:
        with capture_timings(stages), profile_children(directory, stages):
            result = profiler.runcall(run_worker, binding, output, foreground)
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
    module = 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.project_admission__pub'
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
