"""Build and admit immutable images from a verified Release package."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import subprocess
import tempfile
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
TOOL_REGISTRY = ENGINE + "/MCP_PATCHBAY_C21/FEATURE_MCP/tool_registry.json"
_IMAGE = re.compile(r"sha256:[0-9a-f]{64}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_SCHEMA = "org.anechoic.runtime.schema"
_FINGERPRINT = "org.anechoic.runtime.fingerprint"
_VERSION = "org.opencontainers.image.version"
_EXCLUDED = frozenset({".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox", ".venv", ".virtualenv", "venv", "virtualenv", "node_modules", "testcache", ".testcache", "tmp", "vault", ".vault", "secrets", ".secrets", "credentials", ".credentials"})
_SECRETS = frozenset({"auth.json", "credentials.json", "token.txt", "token.json", "secrets.json", "secrets.txt", ".DS_Store"})
_REQUIRED = ("pyproject.toml", "uv.lock", "version.toml", DOCKERFILE, DOCKERIGNORE, TOOL_REGISTRY)


def _excluded(name: str) -> bool:
    return (name in _EXCLUDED or name in _SECRETS or name.endswith("__tests")
            or name.startswith((".anechoic_", "_anechoic_"))
            or name == ".env" or name.startswith(".env.") or name.endswith(".env")
            or Path(name).suffix in {".pyc", ".pyo", ".pem", ".key"})


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def ready_predecessor(selection) -> str | None:
    root, state = Path(selection.root), Path(selection.launcher_state)
    try:
        parts = state.relative_to(root).parts
        if not root.is_absolute() or root.is_symlink() or root.resolve() != root or ".." in parts:
            raise ValueError("unsafe launcher receipt")
        path = root
        for part in parts:
            path /= part
            if not os.path.lexists(path):
                return None
            if path.is_symlink() or not path.is_dir():
                raise ValueError("unsafe launcher receipt")
        path /= "ready.json"
        if not os.path.lexists(path):
            return None
        if path.is_symlink():
            raise ValueError("unsafe launcher receipt")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
                raise ValueError("invalid launcher receipt")
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError("invalid launcher receipt")
        payload = json.loads(raw, object_pairs_hook=_unique)
        image = payload.get("image_id") if isinstance(payload, dict) else None
        if (not isinstance(payload, dict) or payload.get("project_root") != str(root)
                or payload.get("control_root") != str(selection.control_root)
                or payload.get("project_id") != selection.instance_id
                or payload.get("readiness") is not True
                or not isinstance(image, str) or _IMAGE.fullmatch(image) is None):
            raise ValueError("launcher receipt does not match selected Project")
        return image
    except (OSError, ValueError, UnicodeError, TypeError) as error:
        raise ValueError("invalid launcher receipt") from error


@dataclass(frozen=True)
class ImageIdentity:
    fingerprint: str
    version: str
    manifest: tuple[tuple[str, str, int], ...]


class ImageManager:
    def __init__(self, source_root: Path, *, project_root: Path, build_temp_root: Path | None = None,
                 build_provenance: dict[str, str] | None = None, timeout: float = 600,
                 executor=None):
        self.source_root = Path(source_root)
        self.project_root = Path(project_root)
        self.build_temp_root = Path(build_temp_root) if build_temp_root is not None else None
        self.timeout = timeout
        self.executor = executor
        self.uid, self.gid = os.getuid(), os.getgid()
        machine = {"aarch64": "arm64", "x86_64": "amd64"}.get(platform.machine().lower(), platform.machine().lower())
        if machine not in {"amd64", "arm64", "arm", "386", "ppc64le", "s390x", "riscv64"}:
            raise ValueError("unsupported image platform")
        self.platform = "linux/" + machine
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 900:
            raise ValueError("invalid image timeout")
        self.labels = {}
        if build_provenance is not None:
            if not isinstance(build_provenance, dict) or set(build_provenance) != {"project_id", "project_root", "control_root", "project_name", "head_commit"}:
                raise ValueError("invalid image provenance")
            p = build_provenance
            if (not all(isinstance(v, str) and v and "\x00" not in v for v in p.values())
                    or _SHA.fullmatch(p["project_id"]) is None
                    or re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", p["head_commit"]) is None
                    or not p["project_name"].strip() or Path(p["project_root"]) != self.project_root
                    or not PurePosixPath(p["project_root"]).is_absolute() or ".." in PurePosixPath(p["project_root"]).parts
                    or len(PurePosixPath(p["control_root"]).parts) != 1
                    or not p["control_root"].startswith((".anechoic_", "_anechoic_"))
                    or len(p["control_root"]) <= len(".anechoic_")):
                raise ValueError("invalid image provenance")
            self.labels = {"org.anechoic.project": p["project_id"], "org.anechoic.host_project_root": p["project_root"],
                           "org.anechoic.control_root": p["control_root"], "org.anechoic.project.name": p["project_name"],
                           "org.anechoic.source.head_commit": p["head_commit"]}

    def _files(self):
        root = self.source_root
        if root.is_symlink() or not root.is_dir() or root.resolve() != root:
            raise ValueError("image source unavailable")
        paths = []
        for relative in _REQUIRED:
            path = root / relative
            if any((root / Path(*Path(relative).parts[:i])).is_symlink() for i in range(1, len(Path(relative).parts) + 1)) or not path.is_file():
                raise ValueError("image input unavailable")
        engine = root / ENGINE
        def fail(error):
            raise error
        for current, directories, names in os.walk(engine, followlinks=False, onerror=fail):
            directory = Path(current)
            directories[:] = sorted(name for name in directories if not _excluded(name))
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
        return sorted(set(paths) | {root / relative for relative in _REQUIRED}, key=lambda p: p.relative_to(root).as_posix())

    def identity(self, *, use_packaged_assets: bool = False) -> ImageIdentity:
        if not isinstance(use_packaged_assets, bool):
            raise ValueError("invalid image selection")
        try:
            version = tomllib.loads((self.source_root / "version.toml").read_text(encoding="utf-8"))["framework"]["version"]
            if not isinstance(version, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", version) is None:
                raise ValueError("invalid framework version")
            files = self._files()
            if not (self.source_root / TOOL_REGISTRY).stat().st_size:
                raise ValueError("image tool registry is empty")
            manifest = tuple((path.relative_to(self.source_root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest(),
                              0o644 if path.relative_to(self.source_root).as_posix() == TOOL_REGISTRY else path.stat().st_mode & 0o777)
                             for path in files)
            payload = {"schema": "1", "platform": self.platform,
                       "build_arguments": {"RUNTIME_UID": self.uid, "RUNTIME_GID": self.gid}, "files": manifest}
            fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
            return ImageIdentity(fingerprint, version, manifest)
        except (OSError, UnicodeError, KeyError, TypeError) as error:
            raise ValueError("image source unavailable") from error

    def _run(self, args, *, cwd=None, buildx=None):
        env = {key: value for key, value in os.environ.items() if key in {"HOME", "PATH", "DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_CONFIG", "XDG_RUNTIME_DIR", "TMPDIR", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "all_proxy", "no_proxy"}}
        if buildx:
            env["BUILDX_CONFIG"] = str(buildx)
        try:
            with tempfile.TemporaryFile() as output:
                run = self.executor or subprocess.run
                result = run(list(args), cwd=cwd or self.source_root, stdin=subprocess.DEVNULL, stdout=output,
                             stderr=subprocess.DEVNULL, timeout=self.timeout, check=False, env=env)
                if result.returncode != 0:
                    raise RuntimeError("Docker image operation failed")
                if output.tell() > 4 * 1024 * 1024:
                    raise RuntimeError("Docker image output too large")
                output.seek(0)
                return output.read().decode("utf-8")
        except (OSError, UnicodeError, subprocess.SubprocessError) as error:
            raise RuntimeError("Docker image operation unavailable") from error

    def _inspect(self, image: str, identity: ImageIdentity):
        try:
            values = json.loads(self._run(("docker", "image", "inspect", image)), object_pairs_hook=_unique)
            if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
                raise ValueError("invalid image inspection")
            row = values[0]
            labels = row["Config"]["Labels"]
            expected = {_SCHEMA: "1", _FINGERPRINT: identity.fingerprint, _VERSION: identity.version, **self.labels}
            if (row["Id"] != image or row.get("Os") != "linux" or row.get("Architecture") != self.platform.split("/")[1]
                    or not isinstance(labels, dict) or any(labels.get(k) != v for k, v in expected.items())):
                raise ValueError("image identity differs")
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError("image admission failed") from error

    def _verify_context(self, context: Path, identity: ImageIdentity):
        expected = {relative: (digest, mode) for relative, digest, mode in identity.manifest}
        expected_directories = {parent.as_posix() for relative in expected for parent in Path(relative).parents if parent != Path(".")}
        seen, seen_directories = set(), set()
        def fail(error):
            raise error
        for current, directories, names in os.walk(context, followlinks=False, onerror=fail):
            for name in directories:
                path = Path(current) / name
                relative = path.relative_to(context).as_posix()
                if path.is_symlink() or not path.is_dir() or relative not in expected_directories:
                    raise RuntimeError("unsafe image context")
                seen_directories.add(relative)
            for name in names:
                path = Path(current) / name
                relative = path.relative_to(context).as_posix()
                if (path.is_symlink() or not path.is_file() or relative not in expected
                        or (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode & 0o777) != expected[relative]):
                    raise RuntimeError("image context changed")
                seen.add(relative)
        if seen != set(expected) or seen_directories != expected_directories:
            raise RuntimeError("image context changed")

    def resolve(self, explicit_id: str | None = None, build_if_missing: bool = True, *, use_packaged_assets: bool = False) -> str:
        if type(build_if_missing) is not bool or type(use_packaged_assets) is not bool:
            raise ValueError("invalid image selection")
        identity = self.identity(use_packaged_assets=True)
        if explicit_id is not None:
            if not isinstance(explicit_id, str) or _IMAGE.fullmatch(explicit_id) is None:
                raise ValueError("invalid immutable image")
            self._inspect(explicit_id, identity)
            if self.identity(use_packaged_assets=True) != identity:
                raise RuntimeError("image inputs changed")
            return explicit_id
        if not build_if_missing or not self.labels:
            raise RuntimeError("image build unavailable")
        parent = self.build_temp_root
        temporary = self.project_root / ".anechoic_tmp"
        if (parent is None or not parent.is_absolute() or parent.is_symlink() or temporary.is_symlink()
                or not parent.is_dir() or not temporary.is_dir() or parent.resolve() != parent
                or not parent.is_relative_to(temporary.resolve())):
            raise RuntimeError("unsafe image staging")
        with tempfile.TemporaryDirectory(prefix="release-image-", dir=parent) as staging:
            stage = Path(staging)
            context, buildx = stage / "context", stage / "buildx"
            context.mkdir(mode=0o700)
            buildx.mkdir(mode=0o700)
            for relative, digest, mode in identity.manifest:
                data = (self.source_root / relative).read_bytes()
                if hashlib.sha256(data).hexdigest() != digest:
                    raise RuntimeError("image inputs changed")
                destination = context / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                destination.chmod(mode)
            if self.identity(use_packaged_assets=True) != identity:
                raise RuntimeError("image inputs changed")
            self._verify_context(context, identity)
            labels = {_SCHEMA: "1", _FINGERPRINT: identity.fingerprint, _VERSION: identity.version, **self.labels}
            label_args = tuple(arg for key, value in labels.items() for arg in ("--label", f"{key}={value}"))
            iidfile = stage / "image.id"
            self._run(("docker", "build", "--iidfile", str(iidfile), *label_args, "--platform", self.platform,
                       "--build-arg", f"RUNTIME_UID={self.uid}", "--build-arg", f"RUNTIME_GID={self.gid}",
                       "--file", str(context / DOCKERFILE), str(context)), cwd=context, buildx=buildx)
            if iidfile.is_symlink() or not iidfile.is_file() or iidfile.stat().st_size > 1024:
                raise RuntimeError("builder image identity unavailable")
            image = iidfile.read_text(encoding="ascii").strip()
            if _IMAGE.fullmatch(image) is None:
                raise RuntimeError("invalid builder image identity")
            self._inspect(image, identity)
            self._verify_context(context, identity)
            if self.identity(use_packaged_assets=True) != identity:
                raise RuntimeError("image inputs changed")
            self._tag(image, "test")
            return image

    def _tag_images(self, tag: str) -> set[str]:
        raw = self._run(("docker", "image", "ls", "--all", "--quiet", "--no-trunc", tag))
        return {line.strip() for line in raw.splitlines() if line.strip()}

    def _tag(self, image: str, role: str) -> str:
        tag = f"anechoic-runtime:{role}-{image[7:]}"
        ids = self._tag_images(tag)
        if ids and ids != {image}:
            raise RuntimeError("release image tag collision")
        if not ids:
            self._run(("docker", "image", "tag", image, tag))
        if self._tag_images(tag) != {image}:
            raise RuntimeError("release image tag verification failed")
        return tag

    def mark_production_image(self, image: str) -> str:
        if not isinstance(image, str) or _IMAGE.fullmatch(image) is None:
            raise ValueError("invalid immutable image")
        self._inspect(image, self.identity(use_packaged_assets=True))
        tag = self._tag(image, "prod")
        test_tag = "anechoic-runtime:test-" + image[7:]
        if self._tag_images(test_tag) == {image}:
            self._run(("docker", "image", "rm", test_tag))
        return tag
