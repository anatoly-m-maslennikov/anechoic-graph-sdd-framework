"""Image input inventory and identity for local Release."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tomllib


ENGINE = "LAYER_3_ENGINE_STUDIO_C14"
DOCKERFILE = ENGINE + "/MCP_PATCHBAY_C21/FEATURE_MCP/docker/Dockerfile"
DOCKERIGNORE = DOCKERFILE + ".dockerignore"
RETIRED_ASSETS = frozenset(
    ENGINE + "/" + directory + "/" + name
    for directory, names in (
        ("IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND", ("canonical_relation_registry.json", "workbench_schema.json")),
        ("FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE", ("status_model.json", "candidate_schema.json")),
    ) for name in names
)
TOOL_REGISTRY = ENGINE + "/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/tool_registry.json"
_EXCLUDED = frozenset({".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox", ".venv", ".virtualenv", "venv", "virtualenv", "node_modules", "testcache", ".testcache", "tmp", "vault", ".vault", "secrets", ".secrets", "credentials", ".credentials"})
_SECRETS = frozenset({"auth.json", "credentials.json", "token.txt", "token.json", "secrets.json", "secrets.txt", ".DS_Store"})
_REQUIRED = (ENGINE + "/pyproject.toml", ENGINE + "/uv.lock", "version.toml", DOCKERFILE, DOCKERIGNORE, TOOL_REGISTRY)
_BETA_REQUIRED = tuple(ENGINE + "/" + path for path in (
    "KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__pub.py",
    "ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__pub.py", "WORKERS_beta_C69/WORKERS_beta_C69__pub.py",
    "WORKBENCH_BACKEND_beta_C70/WORKBENCH_BACKEND_beta_C70__pub.py",
    "WORKBENCH_BACKEND_beta_C70/runtime__pub.py", "WORKBENCH_BACKEND_beta_C70/shared_runtime__pub.py",
    "WORKBENCH_BACKEND_beta_C70/project_admission__pub.py", "WORKBENCH_BACKEND_beta_C70/query_run.json",
))
_BETA_COMPONENTS = frozenset(path.split("/")[1] for path in _BETA_REQUIRED)
_CURRENT_ONLY = frozenset({ENGINE + "/KERNEL_MIXER_C59",
                           ENGINE + "/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND"})


def _excluded(name: str) -> bool:
    return (name.startswith(".venv-") or name in _EXCLUDED or name in _SECRETS or name.endswith("__tests")
            or name.startswith((".anechoic_", "_anechoic_"))
            or name == ".env" or name.startswith(".env.") or name.endswith(".env")
            or Path(name).suffix in {".pyc", ".pyo", ".pem", ".key"})


def _stack_selector(root: Path) -> tuple[Path | None, str, str | None]:
    path = root / "project.toml"
    if not os.path.lexists(path):
        return None, "current", None
    try:
        if path.is_symlink():
            raise ValueError
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
                raise ValueError
            data = stream.read(65537)
        if len(data) > 65536:
            raise ValueError
        document = tomllib.loads(data.decode("utf-8"))
        if set(document) != {"stack"} or document["stack"] not in ("current", "beta"):
            raise ValueError
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        raise ValueError('invalid project.toml: expected only stack = "current" or "beta"') from error
    return path, document["stack"], hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class ImageIdentity:
    fingerprint: str
    version: str
    manifest: tuple[tuple[str, str, int], ...]


class ImageInputIdentity:
    def _files(self):
        root = self.source_root
        if root.is_symlink() or not root.is_dir() or root.resolve() != root:
            raise ValueError("image source unavailable")
        paths = []
        selector, stack, selector_digest = _stack_selector(root)
        required = _REQUIRED if stack == "current" else _REQUIRED[:-1] + _BETA_REQUIRED
        for relative in required:
            path = root / relative
            if any((root / Path(*Path(relative).parts[:i])).is_symlink() for i in range(1, len(Path(relative).parts) + 1)) or not path.is_file():
                raise ValueError(f"image input unavailable: {relative}")
        engine = root / ENGINE
        def fail(error):
            raise error
        for current, directories, names in os.walk(engine, followlinks=False, onerror=fail):
            directory = Path(current)
            directories[:] = sorted(name for name in directories if not _excluded(name)
                                    and (stack == "beta" or re.search(r"_beta_C[0-9]+\Z", name) is None)
                                    and (stack != "beta" or (directory / name).relative_to(root).as_posix() not in _CURRENT_ONLY)
                                    and (stack != "beta" or re.search(r"_beta_C[0-9]+\Z", name) is None
                                         or (directory == engine and name in _BETA_COMPONENTS)
                                         or (directory != engine and directory.relative_to(engine).parts[0] in _BETA_COMPONENTS)))
            if any(name == ".runtime" or name.startswith(".env") for name in directories):
                raise ValueError("unsafe image input")
            for name in directories:
                path = directory / name
                if path.is_symlink() or not path.is_dir():
                    raise ValueError("unsafe image input")
            for name in sorted(names):
                if _excluded(name):
                    continue
                if name == ".runtime" or name.startswith(".env"):
                    raise ValueError("unsafe image input")
                path = directory / name
                if path.is_symlink() or not path.is_file():
                    raise ValueError("unsafe image input")
                if path.relative_to(root).as_posix() not in RETIRED_ASSETS:
                    paths.append(path)
        files = sorted(set(paths) | {root / relative for relative in required} | ({selector} if selector else set()),
                       key=lambda p: p.relative_to(root).as_posix())
        return files, (selector, stack, selector_digest)

    def identity(self, *, use_packaged_assets: bool = False) -> ImageIdentity:
        if not isinstance(use_packaged_assets, bool):
            raise ValueError("invalid image selection")
        try:
            version = tomllib.loads((self.source_root / "version.toml").read_text(encoding="utf-8"))["framework"]["version"]
            if not isinstance(version, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", version) is None:
                raise ValueError("invalid framework version")
            files, selection = self._files()
            if self.source_root / TOOL_REGISTRY in files and not (self.source_root / TOOL_REGISTRY).stat().st_size:
                raise ValueError("image tool registry is empty")
            manifest = tuple((path.relative_to(self.source_root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest(),
                              0o644 if path.relative_to(self.source_root).as_posix() == TOOL_REGISTRY else path.stat().st_mode & 0o777)
                             for path in files)
            if (_stack_selector(self.source_root) != selection or
                    (selection[0] is not None and ("project.toml", selection[2]) not in
                     {(path, digest) for path, digest, _ in manifest})):
                raise ValueError("image stack selection changed")
            payload = {"schema": "1", "platform": self.platform,
                       "build_arguments": {"RUNTIME_UID": self.uid, "RUNTIME_GID": self.gid}, "files": manifest}
            fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
            return ImageIdentity(fingerprint, version, manifest)
        except (OSError, UnicodeError, KeyError, TypeError) as error:
            raise ValueError("image source unavailable") from error

