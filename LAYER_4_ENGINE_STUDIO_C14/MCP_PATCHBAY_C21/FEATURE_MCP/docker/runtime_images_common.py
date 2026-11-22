"""Shared image admission data and source selection rules."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys

try:
    from .image_reference import IMMUTABLE_IMAGE
    from .image_tool_registry import TOOL_REGISTRY
except ImportError:
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_reference import IMMUTABLE_IMAGE
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_tool_registry import TOOL_REGISTRY

ENGINE_ROOT = "LAYER_4_ENGINE_STUDIO_C14"
DOCKER_ROOT = ENGINE_ROOT + "/MCP_PATCHBAY_C21/FEATURE_MCP/docker"
DOCKERFILE = DOCKER_ROOT + "/Dockerfile"
DOCKERIGNORE = DOCKER_ROOT + "/Dockerfile.dockerignore"
LICENSE_INPUTS = ("LICENSE", "LICENSE.TLDR.md", DOCKER_ROOT + "/DuckPGQ.LICENSE")
RETIRED_ASSETS = frozenset(
    ENGINE_ROOT + "/" + directory + "/" + name
    for directory, names in (
        ("IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND",
         ("canonical_relation_registry.json", "workbench_schema.json")),
        ("FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE",
         ("status_model.json", "candidate_schema.json")),
    )
    for name in names
)
_GENERATED_ASSETS = frozenset({TOOL_REGISTRY})
SCHEMA_LABEL = "org.anechoic.runtime.schema"
FINGERPRINT_LABEL = "org.anechoic.runtime.fingerprint"
SCHEMA = "1"
_REQUIRED = (
    "LAYER_3_ENVIRONMENTS_C72/engine/pyproject.toml",
    "LAYER_3_ENVIRONMENTS_C72/engine/uv.lock",
    "version.toml", DOCKERFILE, DOCKERIGNORE, *LICENSE_INPUTS,
)
_TRANSIENT_DIRECTORIES = frozenset({
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".nox", ".venv", ".venv-dev", ".venv-prod", ".virtualenv", "venv", "virtualenv",
    "node_modules", "testcache", ".testcache", "tmp",
})
_SECRET_FILES = frozenset({
    "auth.json", "credentials.json", "token.txt", "token.json", "secrets.json", "secrets.txt",
})
_CREDENTIAL_DIRECTORIES = frozenset({
    "vault", ".vault", "secrets", ".secrets", "credentials", ".credentials",
})
_PLATFORM = re.compile(r"linux/(?:amd64|arm64|arm|386|ppc64le|s390x|riscv64)(?:/v[0-9]+)?")


class ImageError(RuntimeError):
    """One safe launcher condition, without captured Docker diagnostics."""

    def __init__(self, code: str, message: str | None = None):
        self.code = code
        defaults = {
            "IMAGE_INPUT_UNAVAILABLE": "Supply a readable --source-root Framework build closure",
            "IMAGE_REFUSED": "A matching immutable runtime image could not be admitted",
            "BUILD_FAILED": "Runtime image build did not produce an admitted immutable image",
        }
        super().__init__(message or defaults.get(code, "Runtime image operation failed"))


@dataclass(frozen=True)
class BuildInput:
    path: str
    sha256: str
    mode: int


@dataclass(frozen=True)
class ImageIdentity:
    fingerprint: str
    tag: str
    version: str
    platform: str
    manifest: tuple[BuildInput, ...]
    uid: int
    gid: int
    tool_registry: bytes
    model_sha256: str | None


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _excluded_directory(name: str) -> bool:
    return (name in _TRANSIENT_DIRECTORIES or name in _CREDENTIAL_DIRECTORIES
            or name.startswith((".anechoic_", "_anechoic_")) or name.endswith("__tests"))


def _excluded_file(name: str) -> bool:
    return (_excluded_directory(name)
            or name == ".env" or name.startswith(".env.") or name.endswith(".env")
            or name in _SECRET_FILES or name == ".DS_Store"
            or Path(name).suffix in {".pyc", ".pyo", ".pem", ".key"})


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate image inspection member")
        value[key] = item
    return value


def _receipt_image(path: Path, selection: object) -> str:
    guard = (Path(__file__).resolve().parents[3] / "FEATURE_PROGRAMMATIC/FEATURE_TOOLS"
             / "ADAPTERS_C30/ADAPTERS_C30__pub.py")
    result = subprocess.run([sys.executable, "-B", str(guard), "--read-bounded", str(path)],
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, timeout=10, check=True)
    payload = json.loads(result.stdout, object_pairs_hook=_unique_object)
    image = payload.get("image_id")
    if (payload.get("project_root") != str(selection.root)
            or payload.get("control_root") != str(selection.control_root)
            or payload.get("project_id") != selection.instance_id
            or payload.get("readiness") is not True
            or not isinstance(image, str) or IMMUTABLE_IMAGE.fullmatch(image) is None):
        raise ValueError("launcher receipt does not match selected Project")
    return image


def ready_predecessor(selection) -> str | None:
    path = selection.launcher_state / "ready.json"
    return _receipt_image(path, selection) if os.path.lexists(path) else None

