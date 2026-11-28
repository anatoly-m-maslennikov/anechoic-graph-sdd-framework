"""Build a release image from a verified input inventory."""

import hashlib
import os
from pathlib import Path
import re
import stat
import tempfile

from ..image_identity.image_identity__shared import DOCKERFILE, ImageIdentity


_IMAGE = re.compile(r"sha256:[0-9a-f]{64}\Z")

_PRUNE_BUILD_CACHE = (
    "docker",
    "buildx",
    "prune",
    "--force",
    "--max-used-space",
    "4GB",
    "--min-free-space",
    "2GB",
)


def _remove_finder_metadata(path: Path) -> bool:
    if path.name == ".DS_Store":
        try:
            if stat.S_ISREG(path.lstat().st_mode):
                path.unlink(missing_ok=True)
                return True
        except FileNotFoundError:
            return True
    return False


class ImageBuild:
    def _verify_context(self, context: Path, identity: ImageIdentity):
        expected = {
            relative: (digest, mode)
            for relative, digest, mode in identity.manifest
        }
        expected_directories = {
            parent.as_posix()
            for relative in expected
            for parent in Path(relative).parents
            if parent != Path(".")
        }
        seen, seen_directories = set(), set()

        def fail(error):
            raise error

        for current, directories, names in os.walk(
            context, topdown=False, followlinks=False, onerror=fail
        ):
            for name in directories:
                path = Path(current) / name
                relative = path.relative_to(context).as_posix()
                if path.is_symlink() or not path.is_dir():
                    raise RuntimeError("unsafe image context")
                if relative not in expected_directories:
                    path.rmdir()
                    continue
                seen_directories.add(relative)
            for name in names:
                path = Path(current) / name
                if _remove_finder_metadata(path):
                    continue
                relative = path.relative_to(context).as_posix()
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or relative not in expected
                    or (
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                        path.stat().st_mode & 0o777,
                    )
                    != expected[relative]
                ):
                    raise RuntimeError("image context changed")
                seen.add(relative)
        if seen != set(expected) or seen_directories != expected_directories:
            raise RuntimeError("image context changed")

    def _populate_context(self, context, identity):
        for relative, digest, mode in identity.manifest:
            data = self._source_map.get(
                Path(relative), self.source_root / relative
            ).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise RuntimeError("image inputs changed")
            destination = context / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            destination.chmod(mode)
        if self.identity(use_packaged_assets=True) != identity:
            raise RuntimeError("image inputs changed")

    def _run_build(self, context, buildx, iidfile, label_args):
        self._run(
            (
                "docker",
                "build",
                "--iidfile",
                str(iidfile),
                *label_args,
                "--platform",
                self.platform,
                "--build-arg",
                f"RUNTIME_UID={self.uid}",
                "--build-arg",
                f"RUNTIME_GID={self.gid}",
                "--file",
                str(context / DOCKERFILE),
                str(context),
            ),
            cwd=context,
            buildx=buildx,
        )

    def _staging_parent(self):
        parent = self.build_temp_root
        temporary = self.project_root / ".anechoic_tmp"
        if (
            parent is None
            or not parent.is_absolute()
            or parent.is_symlink()
            or temporary.is_symlink()
            or not parent.is_dir()
            or not temporary.is_dir()
            or parent.resolve() != parent
            or not parent.is_relative_to(temporary.resolve())
        ):
            raise RuntimeError("unsafe image staging")
        return parent

    def _build(self, identity: ImageIdentity) -> str:
        parent = self._staging_parent()
        with tempfile.TemporaryDirectory(
            prefix="release-image-", dir=parent
        ) as staging:
            stage = Path(staging)
            context, buildx = stage / "context", stage / "buildx"
            context.mkdir(mode=0o700)
            buildx.mkdir(mode=0o700)
            self._populate_context(context, identity)
            labels = self._expected_labels(identity)
            label_args = tuple(
                arg
                for key, value in labels.items()
                for arg in ("--label", f"{key}={value}")
            )
            iidfile = stage / "image.id"
            self._run(_PRUNE_BUILD_CACHE, cwd=context, buildx=buildx)
            self._verify_context(context, identity)
            self._run_build(context, buildx, iidfile, label_args)
            if (
                iidfile.is_symlink()
                or not iidfile.is_file()
                or iidfile.stat().st_size > 1024
            ):
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
