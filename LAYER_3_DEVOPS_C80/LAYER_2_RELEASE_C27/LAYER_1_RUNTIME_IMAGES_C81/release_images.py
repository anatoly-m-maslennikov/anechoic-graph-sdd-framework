"""Build and admit immutable images from a verified Release package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import subprocess
import tempfile

from .release_image_identity import (
    ENGINE as ENGINE, DOCKERFILE, DOCKERIGNORE as DOCKERIGNORE, RETIRED_ASSETS as RETIRED_ASSETS, TOOL_REGISTRY as TOOL_REGISTRY,
    _EXCLUDED as _EXCLUDED, _SECRETS as _SECRETS, _REQUIRED as _REQUIRED, _excluded as _excluded, ImageIdentity, ImageInputIdentity,
)



_IMAGE = re.compile(r"sha256:[0-9a-f]{64}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_SCHEMA = "org.anechoic.runtime.schema"
_FINGERPRINT = "org.anechoic.runtime.fingerprint"
_VERSION = "org.opencontainers.image.version"
_PRUNE_BUILD_CACHE = ("docker", "buildx", "prune", "--force", "--max-used-space", "4GB", "--min-free-space", "2GB")


def _candidate_role(identity: ImageIdentity) -> str:
    beta_entrypoint = ENGINE + "/WORKBENCH_BACKEND_beta_C70/WORKBENCH_BACKEND_beta_C70__shared.py"
    return "beta" if any(path == beta_entrypoint for path, _, _ in identity.manifest) else "test"


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


class ImageManager(ImageInputIdentity):
    def __init__(self, source_root: Path, *, project_root: Path, build_temp_root: Path | None = None,
                 build_provenance: dict[str, str] | None = None, timeout: float = 600,
                 executor=None, source_provider=None):
        self.source_provider = source_provider
        self._source_map = {}
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
        return self._build(identity)

    def _build(self, identity: ImageIdentity) -> str:
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
                data = self._source_map.get(Path(relative), self.source_root / relative).read_bytes()
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
            role = _candidate_role(identity)
            iidfile = stage / "image.id"
            self._run(_PRUNE_BUILD_CACHE, cwd=context, buildx=buildx)
            self._run(("docker", "build", "--iidfile", str(iidfile), *label_args, "--platform", self.platform,
                       *(("--target", "beta") if role == "beta" else ()),
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
            self._tag(image, role)
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

    def prune_build_cache(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.build_temp_root) as buildx:
            self._run(_PRUNE_BUILD_CACHE, buildx=buildx)

    def mark_production_image(self, image: str) -> str:
        if not isinstance(image, str) or _IMAGE.fullmatch(image) is None:
            raise ValueError("invalid immutable image")
        identity = self.identity(use_packaged_assets=True)
        self._inspect(image, identity)
        if self.identity(use_packaged_assets=True) != identity:
            raise RuntimeError("image inputs changed")
        tag = self._tag(image, "prod")
        candidate_tag = f"anechoic-runtime:{_candidate_role(identity)}-{image[7:]}"
        if self._tag_images(candidate_tag) == {image}:
            self._run(("docker", "image", "rm", candidate_tag))
        return tag
