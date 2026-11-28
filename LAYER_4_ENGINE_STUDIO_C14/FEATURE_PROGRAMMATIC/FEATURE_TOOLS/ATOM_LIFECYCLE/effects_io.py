"""Open and verify lifecycle paths and Workbench reads."""

from __future__ import annotations

from . import effects as owner


@owner.contextmanager
def _project_write_lock(root):
    temporary = owner.owned_temporary_root(
        owner.repository_root(root), "atom_lifecycle"
    )
    directory = owner.open_regular(temporary, directory=True)
    try:
        flags = (
            owner.os.O_RDWR
            | owner.os.O_CREAT
            | owner.os.O_NOFOLLOW
            | owner.os.O_NONBLOCK
        )
        lock = owner.os.open("write.lock", flags, mode=0o600, dir_fd=directory)
        try:
            if not owner.stat.S_ISREG(owner.os.fstat(lock).st_mode):
                raise OSError("Lifecycle write lock is not a regular file.")
            owner.fcntl.flock(lock, owner.fcntl.LOCK_EX | owner.fcntl.LOCK_NB)
            yield
        finally:
            owner.os.close(lock)
    finally:
        owner.os.close(directory)


def _parent(root: owner.Path, path: owner.Path) -> tuple[int, str, str]:
    """Open directories without symlinks and retain the parent fd."""
    root = owner.Path(owner.os.path.abspath(root))
    path = owner.Path(path)
    if not path.is_absolute():
        path = root / path
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError("carrier outside project") from exc
    if not relative.parts or any(
        part in (".", "..") for part in relative.parts
    ):
        raise ValueError("invalid project-relative carrier path")
    flags = owner.os.O_RDONLY | owner.os.O_DIRECTORY | owner.os.O_NOFOLLOW
    fd = owner.os.open(root, flags)
    try:
        for part in relative.parts[:-1]:
            child = owner.os.open(part, flags, dir_fd=fd)
            owner.os.close(fd)
            fd = child
        return fd, relative.name, relative.as_posix()
    except BaseException:
        owner.os.close(fd)
        raise


def _read(parent: int, name: str) -> bytes:
    fd = owner.os.open(
        name,
        owner.os.O_RDONLY | owner.os.O_NOFOLLOW | owner.os.O_NONBLOCK,
        dir_fd=parent,
    )
    with owner.os.fdopen(fd, "rb") as stream:
        if not owner.stat.S_ISREG(owner.os.fstat(stream.fileno()).st_mode):
            raise ValueError("carrier is not a regular file")
        return stream.read()


def _pinned(parent: int, name: str, digest: str) -> bytes:
    data = owner._read(parent, name)
    if owner.hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("stale source")
    return data


def _reader(path: owner.Path):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.settings__shared import (
        bound_selection,
    )
    from .sources import source__shared as source

    get_reader = getattr(source, "query_reader", None)
    reader = get_reader() if get_reader is not None else None
    if reader is None:
        return None
    selection = bound_selection()
    prefix = (
        owner.re.escape(
            selection.settings["artifacts"]["identity"]["project_prefix"]
        )
        if selection
        else ".+"
    )
    return (
        reader
        if owner.re.fullmatch(rf"(?:[0-9]+-)?{prefix}-[A-Z]-.*\.md", path.name)
        else None
    )


def publication_guard():
    """Hide paired lifecycle effects from the watcher until complete."""
    from .sources.source__shared import query_reader

    reader = query_reader()
    publication = getattr(reader, "lifecycle_publication", None)
    if callable(publication):
        return publication()
    lock = getattr(reader, "lifecycle_file_effect", None)
    return lock() if callable(lock) else owner.nullcontext()


def _check_parent(root, path, parent, name, *, check_name):
    checked_parent, checked_name, _ = owner._parent(root, path)
    try:
        actual = owner.os.fstat(checked_parent)
        expected = owner.os.fstat(parent)
        if (check_name and checked_name != name) or (
            actual.st_dev,
            actual.st_ino,
        ) != (expected.st_dev, expected.st_ino):
            raise ValueError("carrier parent changed")
    finally:
        owner.os.close(checked_parent)


def _query_read(
    reader, root: owner.Path, path: owner.Path, parent: int, name: str
) -> bytes:
    """Keep the descriptor-pinned carrier stable across the Workbench read."""
    _check_parent(root, path, parent, name, check_name=True)
    descriptor = owner.os.open(
        name,
        owner.os.O_RDONLY | owner.os.O_NOFOLLOW | owner.os.O_NONBLOCK,
        dir_fd=parent,
    )
    try:
        before = owner.os.fstat(descriptor)
        if not owner.stat.S_ISREG(before.st_mode):
            raise ValueError("carrier is not a regular file")
        try:
            data = reader.lifecycle_read(
                owner.Path(root).absolute() / path, descriptor=descriptor
            )
        except Exception as exc:
            raise RuntimeError("Workbench carrier read failed") from exc
        actual = owner.os.fstat(descriptor)
        after = owner.os.stat(name, dir_fd=parent, follow_symlinks=False)
        if (after.st_dev, after.st_ino) != (actual.st_dev, actual.st_ino) or (
            before.st_size,
            before.st_mtime_ns,
        ) != (actual.st_size, actual.st_mtime_ns):
            raise ValueError("carrier changed during Workbench read")
    finally:
        owner.os.close(descriptor)
    if not isinstance(data, bytes):
        raise RuntimeError("Workbench carrier read returned invalid bytes")
    _check_parent(root, path, parent, None, check_name=False)
    return data


def _read_pinned(
    reader,
    root: owner.Path,
    path: owner.Path,
    parent: int,
    name: str,
    digest: str,
) -> bytes:
    if reader is None:
        return owner._pinned(parent, name, digest)
    data = owner._query_read(reader, root, path, parent, name)
    if owner.hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("stale source")
    return data


def _changed(reader, old: owner.Path | None, new: owner.Path | None) -> None:
    if reader is not None:
        try:
            reader.lifecycle_changed(old, new)
        except Exception as exc:
            raise RuntimeError("Workbench synchronization failed") from exc


def _message(exc: Exception) -> str:
    if isinstance(exc, RuntimeError) and str(exc) in {
        "Workbench carrier read failed",
        "Workbench carrier read returned invalid bytes",
        "Workbench synchronization failed",
    }:
        return str(exc)
    return (
        str(exc)
        if isinstance(exc, ValueError)
        else f"filesystem operation failed ({type(exc).__name__})"
    )


def _cleanup_temp(
    root: owner.Path, temp: str | None, result: owner.Result
) -> None:
    if temp is None:
        return
    try:
        owner.os.unlink(temp)
    except FileNotFoundError:
        pass
    except OSError:
        try:
            retained = (
                owner.Path(temp)
                .relative_to(owner.Path(root).absolute())
                .as_posix()
            )
        except ValueError:
            retained = ".anechoic_tmp (path unavailable)"
        owner._error(
            result,
            "backend_failure",
            f"temporary carrier retained at {retained}",
        )
