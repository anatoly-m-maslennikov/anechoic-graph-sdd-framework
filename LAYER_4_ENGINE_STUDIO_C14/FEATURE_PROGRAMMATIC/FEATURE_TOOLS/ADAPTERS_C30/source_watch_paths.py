"""Resolve and validate the Source Watcher's configured paths."""

from pathlib import Path


def watched_roots(root, control_root, implementation_root):
    roots = (
        (control_root,)
        if implementation_root is None
        else (control_root, implementation_root)
    )
    candidates = tuple(Path(path).absolute() for path in roots)
    resolved_root = root.resolve()
    if any(
        not path.is_relative_to(root)
        or not path.resolve().is_relative_to(resolved_root)
        for path in candidates
    ):
        raise ValueError(
            "Workbench sources must be inside the selected repository"
        )
    roots = tuple(
        path
        for path in dict.fromkeys(candidates)
        if not any(
            path != other and path.is_relative_to(other)
            for other in candidates
        )
    )
    return resolved_root, roots, tuple(path.resolve() for path in roots)


def additional_watch(additional_directory, roots, resolved_roots):
    additional = (
        Path(additional_directory).absolute()
        if additional_directory is not None
        else None
    )
    if additional is not None and (
        not any(additional.is_relative_to(path) for path in roots)
        or not any(
            additional.resolve().is_relative_to(path)
            for path in resolved_roots
        )
    ):
        raise ValueError(
            "Workbench sources must be inside the selected repository"
        )
    return additional
