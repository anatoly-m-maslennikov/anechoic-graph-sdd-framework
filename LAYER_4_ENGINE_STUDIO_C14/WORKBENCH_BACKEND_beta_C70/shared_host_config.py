"""Read and pin a shared host's bounded TOML configuration."""
from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import stat
import tomllib


def directory(value):
    if not isinstance(value, str) or not value or '\0' in value:
        raise ValueError('invalid_project_root')
    path = Path(value)
    if not path.is_absolute() or '..' in path.parts or path.resolve(strict=True) != path or not path.is_dir():
        raise ValueError('invalid_project_root')
    return path


@dataclass(frozen=True)
class Config:
    source: Path
    digest: str
    root: Path
    single: bool
    maximum: int
    workbench_storage: str = "disk"
    journal_storage: str = "files"
    log_level: str = "INFO"

    @property
    def runtime_id(self):
        return sha256(f'{self.source}\0{self.root}'.encode()).hexdigest()

    def project(self, value):
        root = directory(value)
        if (root != self.root if self.single else root == self.root or not root.is_relative_to(self.root)):
            raise ValueError('outside_project_root')
        return root


def load(path=None):
    source = Path(path or Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'anechoic/runtime.toml').expanduser().absolute()
    if source.resolve(strict=True) != source:
        raise ValueError('host_configuration_invalid')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(source, flags)
    try:
        before = os.fstat(fd)
        raw = os.read(fd, 4097)
        after = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_mode & 0o022 or len(raw) > 4096
                or (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size)
                != (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size)
                or source.stat().st_ino != after.st_ino):
            raise ValueError('host_configuration_invalid')
    finally:
        os.close(fd)
    doc = tomllib.loads(raw.decode('utf-8'))
    allowed = {'schema_version', 'shared_mcp', 'project_defaults', 'logging'}
    if set(doc) - allowed or type(doc.get('schema_version')) is not int or doc['schema_version'] != 1:
        raise ValueError('host_configuration_invalid')
    shared = doc.get('shared_mcp')
    if not isinstance(shared, dict) or set(shared) - {'project_root', 'projects_root', 'http_port', 'max_loaded_projects'} or len({'project_root', 'projects_root'} & shared.keys()) != 1:
        raise ValueError('host_configuration_invalid')
    single = 'project_root' in shared
    root = directory(shared['project_root' if single else 'projects_root'])
    port, maximum = shared.get('http_port'), shared.get('max_loaded_projects', 2)
    defaults = doc.get('project_defaults', {})
    if (root == root.parent or type(port) is not int or not 1 <= port <= 65535
            or type(maximum) is not int or not 1 <= maximum <= 64 or not isinstance(defaults, dict)
            or set(defaults) - {'workbench_storage', 'journal_storage'}
            or defaults.get('workbench_storage', 'disk') not in ('disk', 'memory')
            or defaults.get('journal_storage', 'files') not in ('files', 'duckdb')):
        raise ValueError('host_configuration_invalid')
    logging = doc.get('logging', {})
    if not isinstance(logging, dict) or logging.keys() - {'level'}:
        raise ValueError('host_configuration_invalid')
    level = logging.get('level', 'INFO')
    if level not in ('DEBUG', 'INFO', 'WARNING', 'ERROR'):
        raise ValueError('host_configuration_invalid')
    return Config(source, sha256(raw).hexdigest(), root, single, maximum,
                  defaults.get('workbench_storage', 'disk'), defaults.get('journal_storage', 'files'), level)
