"""Image input inventory and identity for local Release."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tomllib

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


SOURCE_LAYERS = ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58")

SELECTOR = "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
ENGINE = "LAYER_4_ENGINE_STUDIO_C14"
DOCKER_ROOT = ENGINE + "/MCP_PATCHBAY_C21/FEATURE_MCP/docker"
DOCKERFILE = DOCKER_ROOT + "/Dockerfile"
DOCKERIGNORE = DOCKERFILE + ".dockerignore"
LICENSE_INPUTS = ("LICENSE", "LICENSE.TLDR.md", DOCKER_ROOT + "/DuckPGQ.LICENSE")
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
_REQUIRED = (
    "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml",
    "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock",
    "version.toml", DOCKERFILE, DOCKERIGNORE, *LICENSE_INPUTS, TOOL_REGISTRY,
)
_BETA_ROOTS = frozenset({"KERNEL_MIXER_beta_C67", "ORCHESTRATOR_beta_C68", "WORKERS_beta_C69", "API_MIXER_beta_C82"})
_BETA_REQUIRED = tuple(f"{ENGINE}/{path}" for path in (
    "FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_MODEL_VALIDATION/project_admission__pub.py",
    "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/native_snapshot_cli.py",
    "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_IMPORT_GRAPH_C61/realization_graph_cli.py",
    "KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__shared.py",
    "ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__shared.py",
    "ORCHESTRATOR_beta_C68/warm_worker.py",
    "WORKERS_beta_C69/WORKERS_beta_C69__shared.py",
    "WORKERS_beta_C69/warm_worker.py",
    "ORCHESTRATOR_beta_C68/project_peer_owner.py", "ORCHESTRATOR_beta_C68/shared_peer_owner.py",
    "API_MIXER_beta_C82/API_MIXER_beta_C82__shared.py", "API_MIXER_beta_C82/shared_runtime.py",
))
_BETA_DIRECTORY = re.compile(r"_beta_C[0-9]+\Z")
_CURRENT_ONLY = frozenset({"KERNEL_MIXER_C59", "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND"})


def _excluded(name: str) -> bool:
    return (name.startswith(".venv-") or name in _EXCLUDED or name in _SECRETS or name.endswith("__tests")
            or name.startswith((".anechoic_", "_anechoic_"))
            or name == ".env" or name.startswith(".env.") or name.endswith(".env")
            or Path(name).suffix in {".pyc", ".pyo", ".pem", ".key"})


def _include_engine_directory(path: Path, engine: Path, stack: str, beta_components: frozenset[str]) -> bool:
    if _excluded(path.name):
        return False
    relative = path.relative_to(engine)
    if stack != "current" and relative.as_posix() in _CURRENT_ONLY:
        return False
    if _BETA_DIRECTORY.search(path.name) is None:
        return True
    return stack != "current" and relative.parts[0] in beta_components


def _stack_selector(root: Path) -> tuple[Path | None, str, str | None]:
    path = root / SELECTOR
    if not os.path.lexists(path):
        return None, "current", None
    try:
        if path.parent.is_symlink() or path.is_symlink():
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
        if set(document) != {"stack"} or document["stack"] not in ("current", "beta_next"):
            raise ValueError
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        raise ValueError('invalid project.toml: expected only stack = "current" or "beta_next"') from error
    return path, document["stack"], hashlib.sha256(data).hexdigest()


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class ImageIdentity:
    fingerprint: str
    version: str
    manifest: tuple[tuple[str, str, int], ...]
    stack: str


class ImageInputIdentity:
    def _files(self):
        root = self.source_root
        if root.is_symlink() or not root.is_dir() or root.resolve() != root:
            raise ValueError("image source unavailable")
        paths = []
        selector, stack, selector_digest = _stack_selector(root)
        beta_components, stack_required = (_BETA_ROOTS, _BETA_REQUIRED) if stack == "beta_next" else (frozenset(), ())
        required = _REQUIRED[:-1] + stack_required if beta_components else _REQUIRED
        for relative in required:
            path = root / relative
            if any((root / Path(*Path(relative).parts[:i])).is_symlink() for i in range(1, len(Path(relative).parts) + 1)) or not path.is_file():
                raise ValueError(f"image input unavailable: {relative}")
        engine = root / ENGINE
        def fail(error):
            raise error
        for current, directories, names in os.walk(engine, followlinks=False, onerror=fail):
            directory = Path(current)
            directories[:] = sorted(name for name in directories
                                    if _include_engine_directory(directory / name, engine, stack, beta_components))
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
        source_map = self._delivery_sources(root, fail)
        self._source_map = source_map
        files = sorted(set(paths) | {root / relative for relative in required} | ({selector} if selector else set()),
                       key=lambda p: p.relative_to(root).as_posix())
        return files, (selector, stack, selector_digest), source_map

    def _delivery_sources(self, root, fail):
        if self.source_provider is None:
            source_map = {}
            for layer in SOURCE_LAYERS:
                directory = root / layer
                if directory.is_symlink() or not directory.is_dir():
                    raise ValueError("image delivery sources unavailable")
                for current, directories, names in os.walk(directory, followlinks=False, onerror=fail):
                    for name in directories:
                        if (Path(current) / name).is_symlink():
                            raise ValueError("unsafe image delivery source")
                    for name in names:
                        if _excluded(name):
                            continue
                        path = Path(current) / name
                        if path.is_symlink() or not path.is_file() or path.suffix != ".md":
                            raise ValueError("unsafe image delivery source")
                        source_map[path.relative_to(root)] = path
        else:
            source_map = self.source_provider()
        if (not isinstance(source_map, dict) or any(not isinstance(k, Path) or not isinstance(v, Path)
                or k.is_absolute() or ".." in k.parts or len(k.parts) < 2
                or k.parts[0] not in SOURCE_LAYERS or k.suffix != ".md"
                or v.is_symlink() or not v.is_file() for k, v in source_map.items())
                or any(not any(k.parts[0] == layer for k in source_map) for layer in SOURCE_LAYERS)):
            raise ValueError("image delivery sources unavailable")
        return source_map

    def identity(self, *, use_packaged_assets: bool = False) -> ImageIdentity:
        if not isinstance(use_packaged_assets, bool):
            raise ValueError("invalid image selection")
        try:
            version = tomllib.loads((self.source_root / "version.toml").read_text(encoding="utf-8"))["framework"]["version"]
            if not isinstance(version, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", version) is None:
                raise ValueError("invalid framework version")
            files, selection, source_map = self._files()
            if self.source_root / TOOL_REGISTRY in files and not (self.source_root / TOOL_REGISTRY).stat().st_size:
                raise ValueError("image tool registry is empty")
            manifest = tuple((path.relative_to(self.source_root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest(),
                              0o644 if path.relative_to(self.source_root).as_posix() == TOOL_REGISTRY else path.stat().st_mode & 0o777)
                             for path in files)
            manifest += tuple((relative.as_posix(), hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode & 0o777)
                              for relative, path in sorted(source_map.items()))
            manifest = tuple(sorted(manifest))
            if self.source_provider is not None and self.source_provider() != source_map:
                raise ValueError("image delivery sources changed")
            if (_stack_selector(self.source_root) != selection or
                    (selection[0] is not None and (SELECTOR, selection[2]) not in
                     {(path, digest) for path, digest, _ in manifest})):
                raise ValueError("image stack selection changed")
            payload = {"schema": "1", "platform": self.platform,
                       "build_arguments": {"RUNTIME_UID": self.uid, "RUNTIME_GID": self.gid},
                       "files": [row for row in manifest if row[0] not in LICENSE_INPUTS]}
            fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
            return ImageIdentity(fingerprint, version, manifest, selection[1])
        except (OSError, UnicodeError, KeyError, TypeError) as error:
            raise ValueError("image source unavailable") from error

