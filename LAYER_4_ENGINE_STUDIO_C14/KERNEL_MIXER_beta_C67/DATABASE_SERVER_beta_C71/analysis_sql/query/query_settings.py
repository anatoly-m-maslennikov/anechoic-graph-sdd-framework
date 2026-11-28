"""Read the Workbench result lifetime before starting the Project Kernel."""

import os
import stat
import tomllib


_SETTINGS = ".anechoic_runtime/anechoic_runtime_settings.toml"


def result_ttl(project_root, declared):
    value = declared if declared is not None else _configured_ttl(project_root)
    if type(value) is not int or value <= 0:
        raise ValueError(
            "workbench.result_ttl_seconds must be a positive integer"
        )
    return value


def _configured_ttl(root):
    if root is None:
        return 3600
    root = root.resolve(strict=True)
    path = root / _SETTINGS
    if path.resolve() != path:
        raise ValueError(
            (
                "Workbench settings must use the Project runtime directory "
                "directly"
            )
        )
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return 3600
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("Workbench settings must be a regular file")
        data = stream.read(65537)
        if len(data) > 65536:
            raise ValueError(
                "Workbench settings must be a bounded regular TOML file"
            )
    workbench = tomllib.loads(data.decode("utf-8")).get("workbench", {})
    if not isinstance(workbench, dict):
        raise ValueError("Workbench settings must be a TOML table")
    return workbench.get("result_ttl_seconds", 3600)
