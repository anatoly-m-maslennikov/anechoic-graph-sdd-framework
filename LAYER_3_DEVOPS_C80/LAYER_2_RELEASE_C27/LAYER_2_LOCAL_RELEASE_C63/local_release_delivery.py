"""Verify Local Release targets before retrying an interrupted change."""
from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    _LAYER_NAMES,
    LocalReleaseError,
    _file_identity,
    _native_release_sources,
    _project_path,
    _release_lock,
    _walk_regular_files,
)

from .release_support import _BOOTSTRAP, _PRESERVED_NAMES

INSTALL_PHASES = ("copy product to installed framework", "install project runtime")
COPY_PHASES = ("copy active sources", *INSTALL_PHASES)
PRESERVE_FRAMEWORK = _PRESERVED_NAMES | {"SUPERLAYER_1_METHODOLOGY_SOURCES", "applicable_methodology"}


def launcher_lock(run):
    relative = run.selection.launcher_state.relative_to(run.root) / "launch.lock"
    run.installation_lock.enter_context(_release_lock(run.root, relative, "launcher"))


def abort_lock(root, journal_path):
    return _release_lock(root, journal_path.parent.relative_to(root) / "abort.lock", "abort")


def _prefixed(identities, path):
    return {name.removeprefix(path): value for name, value in identities.items() if name.startswith(path)}


def desired_targets(run, phase):
    if phase == "copy active sources":
        return _source_targets(run)
    if phase == INSTALL_PHASES[0]:
        return {run.installed: (run.product_identity, PRESERVE_FRAMEWORK)}
    skill = _project_path(run.root, Path(".agents/skills/ane"), label="project-ane")
    setup = _project_path(run.root, Path(".anechoic_runtime/start_mcp.py"), label="bootstrap-target")
    return {run.runtime: (run.package_identity, frozenset()),
            skill: (_prefixed(run.package_identity, "SKILLS/ane/"), frozenset()),
            setup: ({".": run.package_identity[_BOOTSTRAP.as_posix()]}, None)}


def _source_targets(run):
    identities = {path.as_posix(): _file_identity(source)
                  for path, source in _native_release_sources(run.selection).items()}
    return {_project_path(run.root, Path(name), label="delivery-layer"):
            (_prefixed(identities, name + "/"), frozenset()) for name in _LAYER_NAMES}


def _observed(path, preserve):
    if not path.exists():
        return None
    if preserve is None:
        if not path.is_file() or path.is_symlink():
            raise LocalReleaseError("local-release-resume-target-unsafe")
        return {".": list(_file_identity(path))}
    files = _walk_regular_files(path, excluded_root_directories=frozenset(name.casefold() for name in preserve),
                                excluded_root_files=preserve)
    return {file.relative_to(path).as_posix(): list(_file_identity(file)) for file in files}


def check_targets(run, phase, *, intent=False):
    """Return true for exact outputs, or check that any partial output is owned."""
    desired = desired_targets(run, phase)
    known = run.journal.data.setdefault("targets", {})
    observed = {path.relative_to(run.root).as_posix(): _observed(path, preserve)
                for path, (_, preserve) in desired.items()}
    expected = {path.relative_to(run.root).as_posix(): {name: list(value) for name, value in entries.items()}
                for path, (entries, _) in desired.items()}
    if not intent:
        if observed != expected:
            raise LocalReleaseError("local-release-resume-installed-target-changed")
        return True
    previous = known.get(phase)
    if previous is None:
        known[phase] = {"before": observed, "after": expected}
        run.journal.save()
        return False
    if previous["after"] != expected:
        raise LocalReleaseError("local-release-resume-target-intent-changed")
    for target, actual in observed.items():
        before = previous["before"][target] or {}
        after = expected[target]
        if any(value not in (before.get(name), after.get(name)) for name, value in (actual or {}).items()):
            raise LocalReleaseError("local-release-resume-target-unverified")
    return observed == expected


def verify_recorded_targets(run, phase):
    """Check an old candidate's committed delivery outputs before replacing them."""
    previous = run.journal.data.get("targets", {}).get(phase)
    if previous is None:
        raise LocalReleaseError("local-release-resume-target-intent-missing")
    for path, (_, preserve) in desired_targets(run, phase).items():
        if _observed(path, preserve) != previous["after"][path.relative_to(run.root).as_posix()]:
            raise LocalReleaseError("local-release-resume-target-unverified")
