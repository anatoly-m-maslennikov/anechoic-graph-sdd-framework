"""Read a canonical host configuration carrier."""

from __future__ import annotations

from pathlib import Path

from . import host_runtime_config as runtime


def _canonical_config_path(value: Path | str) -> Path:
    path = runtime._path(value)
    try:
        if path.resolve(strict=True) != path:
            raise runtime._error(
                "Host runtime configuration file must be canonical"
            )
        info = path.lstat()
        if (
            path.is_symlink()
            or not runtime.stat.S_ISREG(info.st_mode)
            or runtime.stat.S_IMODE(info.st_mode) & 0o022
        ):
            raise runtime._error("Host runtime configuration file is unsafe")
        return path
    except runtime.HostRuntimeConfigError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise runtime._error(
            "Host runtime configuration file is unavailable or unsafe"
        ) from error


def _read_config(path: Path) -> bytes:
    try:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            ADAPTERS_C30__shared import ReadContext  # fmt: skip

        reader = ReadContext(
            roots=[str(path.parent)], limits=dict(runtime._READ_LIMITS)
        )
        raw = reader.read(path)
        if reader.currentness()["state"] != "unchanged":
            raise runtime._error(
                "Host runtime configuration changed during read"
            )
        return raw
    except runtime.HostRuntimeConfigError:
        raise
    except (
        OSError,
        RuntimeError,
        UnicodeError,
        ValueError,
        KeyError,
    ) as error:
        raise runtime._error(
            "Host runtime configuration is unavailable or unsafe"
        ) from error
