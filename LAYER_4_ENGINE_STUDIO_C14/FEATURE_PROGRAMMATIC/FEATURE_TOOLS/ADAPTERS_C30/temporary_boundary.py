"""Validate Project Temporary State directory boundaries."""

from pathlib import Path


class TemporaryBoundaryError(RuntimeError):
    """A disposable Carrier cannot be placed in the required Project Temporary State."""


def validate_directory_components(root: Path, directory: Path) -> None:
    """Reject existing symlink or non-directory components below a Project root."""

    try:
        relative = directory.relative_to(root)
    except ValueError as error:
        raise TemporaryBoundaryError(
            f"temporary state path is outside Project root: {directory}"
        ) from error
    current = root
    for component in relative.parts:
        current /= component
        if current.is_symlink():
            raise TemporaryBoundaryError(
                f"temporary state path contains symlinked directory: {current}"
            )
        if current.exists() and not current.is_dir():
            raise TemporaryBoundaryError(f"temporary state path is not a directory: {current}")

