"""Read candidate-only cgroup counters at the startup readiness boundary."""
import json
import os
from pathlib import Path, PurePosixPath
from time import time_ns


_METRICS = ('cpu_seconds', 'peak_memory_bytes', 'block_read_bytes', 'block_write_bytes')


def _member(proc, pid):
    groups = (proc / pid / 'cgroup').read_text().splitlines()
    paths = [line[3:] for line in groups if line.startswith('0::')]
    if len(paths) != 1:
        raise ValueError('unified cgroup v2 unavailable')
    path = PurePosixPath(paths[0])
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('invalid cgroup membership path')
    return path


def _candidate_group(root, proc):
    mountinfo = (proc / 'self/mountinfo').read_text().splitlines()
    mounts = [line.split(' - ', 1) for line in mountinfo]
    if not any(len(parts) == 2 and parts[0].split()[4:5] == [str(root)]
               and parts[1].startswith('cgroup2 ') for parts in mounts):
        raise ValueError('cgroup v2 filesystem unavailable')
    member = _member(proc, 'self')
    if _member(proc, '1') != member:
        raise ValueError('observer is outside the candidate cgroup')
    group = root / member.relative_to('/')
    if not {'1', str(os.getpid())} <= set((group / 'cgroup.procs').read_text().split()):
        raise ValueError('candidate cgroup membership is unverified')
    return group


def _unsigned(text):
    if not text.isascii() or not text.isdecimal():
        raise ValueError('invalid counter')
    return int(text)


def _cpu_usage(text):
    for row in text.splitlines():
        key, space, value = row.partition(' ')
        if key == 'usage_usec' and space:
            return _unsigned(value.strip()) / 1_000_000
    raise ValueError('cpu.stat usage_usec unavailable')


def _block_io(text):
    devices = text.splitlines()
    if not devices:
        raise ValueError('io.stat has no block device counters')
    rows = [dict(item.split('=', 1) for item in device.split()[1:]) for device in devices]
    try:
        return tuple(sum(_unsigned(row[key]) for row in rows) for key in ('rbytes', 'wbytes'))
    except KeyError as error:
        raise ValueError('io.stat read or write bytes unavailable') from error


def _report_counters(group, result):
    for metric, path, parse in (
        ('cpu_seconds', 'cpu.stat', _cpu_usage), ('peak_memory_bytes', 'memory.peak', lambda text: _unsigned(text.strip())),
    ):
        try:
            result[metric] = parse((group / path).read_text())
        except (OSError, ValueError) as error:
            result['unavailable'][metric] = f'{path}: {type(error).__name__}'
    try:
        result['block_read_bytes'], result['block_write_bytes'] = _block_io((group / 'io.stat').read_text())
    except (OSError, ValueError) as error:
        reason = str(error) if isinstance(error, ValueError) else f'io.stat: {type(error).__name__}'
        result['unavailable'].update({key: reason for key in ('block_read_bytes', 'block_write_bytes')})


def cgroup_resources(root=Path('/sys/fs/cgroup'), proc=Path('/proc')):
    result = dict.fromkeys(_METRICS)
    result.update(scope='container cgroup lifetime through sample', timestamp_ns=time_ns(), unavailable={})
    try:
        group = _candidate_group(root, proc)
        identity = group.stat()
    except (OSError, ValueError) as error:
        reason = str(error) if isinstance(error, ValueError) else f'cgroup verification: {type(error).__name__}'
        result['unavailable'] = dict.fromkeys(_METRICS, reason)
        return result
    result.update(source='cgroup v2', device=identity.st_dev, inode=identity.st_ino)
    _report_counters(group, result)
    return result


if __name__ == '__main__':
    print(json.dumps(cgroup_resources()))
