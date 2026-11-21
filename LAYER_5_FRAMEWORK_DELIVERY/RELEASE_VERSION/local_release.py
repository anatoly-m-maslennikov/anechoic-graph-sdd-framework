
"""Direct local replacement workflow for the Project-owned framework release."""

from __future__ import annotations

import json
import fcntl
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable
from contextlib import ExitStack, contextmanager, nullcontext
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43"))
from release_canary import verify_candidate_image  # noqa: E402
from release_cleanup import cleanup_obsolete_images, cleanup_stopped_containers  # noqa: E402
from release_cleanup_identity import image_labels  # noqa: E402
from release_cleanup_images import record_ready_images  # noqa: E402
from release_image_provenance import release_image_provenance  # noqa: E402
from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images import ImageError  # noqa: E402
from LAYER_5_FRAMEWORK_DELIVERY.local_release_test_process import run_logged_test_process  # noqa: E402
from release_support import (  # noqa: E402
    LocalReleaseError,
    _DEFAULT_PRODUCT,
    _GENERATED_ASSETS,
    _PRESERVED_NAMES,
    _RUN_ID,
    _build_predecessor,
    _cleanup_staging,
    _clear_target,
    _copy_tree,
    _deploy_bootstrap,
    _file_identity,
    _image_manager,
    _launcher_image,
    _prepare_package,
    _project_path,
    _read_version,
    _relative,
    _root,
    _target,
    _verify_package,
    _walk_regular_files,
    _failed_test_output as _support_failed_test_output,
)


def _failed_test_output(root: Path, run_id: str, result: Any, *, log_path: str | None = None) -> str:
    return _support_failed_test_output(
        root, run_id, result, log_path=log_path, named_temporary_file=tempfile.NamedTemporaryFile,
    )


@contextmanager
def _installation_lock(root: Path, selection=None):
    from project_runtime import bind_native_runtime, owned_temporary_root
    from VALIDATE_ATOMS.validate_atoms_workers.read_io import open_regular

    with bind_native_runtime(selection) if selection is not None else nullcontext():
        directory = open_regular(owned_temporary_root(root, "local_release_installation"), directory=True)
    try:
        descriptor = os.open("installation.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,
                             mode=0o600, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise LocalReleaseError("local-release-installation-lock-invalid")
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise LocalReleaseError("local-release-installation-lock-busy") from error
            yield
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)


def run_local_release(
    project_root: Path | str,
    *,
    run_id: str,
    runner: Callable[[tuple[str, ...], Path], Any] | None = None,
    test_modules: tuple[str, ...] | None = None,
    image_mode: str = "refresh",
) -> dict[str, object]:
    """Run the direct local release without candidate selection or recovery state."""

    if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
        raise LocalReleaseError("local-release-run-id-invalid")
    if image_mode not in ("refresh", "existing"):
        raise LocalReleaseError("local-release-image-mode-invalid")
    if test_modules is not None and not isinstance(test_modules, tuple):
        raise LocalReleaseError("local-release-test-modules-invalid")
    if test_modules == ():
        raise LocalReleaseError("local-release-test-modules-empty")
    if test_modules is not None and any(not isinstance(module, str) for module in test_modules):
        raise LocalReleaseError("local-release-test-modules-invalid")
    root = _root(project_root)
    from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project
    installation_lock = ExitStack()
    try:
        selection = select_runtime_project(root)
    except ValueError as error:
        raise LocalReleaseError("local-release-project-selection-invalid") from error
    cleanup_runner = runner
    default_runner = runner is None
    if runner is None:
        runner = lambda argv, cwd: subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)

    product = _target(root, Path(_DEFAULT_PRODUCT), label="product-root")
    installed = _target(root, selection.control_relative / "000_ANECHOIC_framework", label="installed-root")
    package: Path | None = None
    prepared_product: Path | None = None
    staging: Path | None = None
    package_identity: dict[str, tuple[str, int]] = {}
    product_identity: dict[str, tuple[str, int]] = {}
    candidate_image: str | None = None
    candidate_fingerprint: str | None = None
    runtime = _target(root, Path(".anechoic_runtime/simple_local_release/package"), label="simple-runtime")
    if product == installed:
        raise LocalReleaseError("local-release-target-invalid")

    failed_step = "validate_inputs"
    mcp: Any = None
    endpoint: str | None = None
    canary_endpoint: str | None = None
    receipt_path: str | None = None
    test_log_path: str | None = None
    cleanup_note = "No proven superseded Project-owned image identity was available; none was removed."
    cleanup_pending = False
    cleanup = None
    test_scope = "full"
    selected_test_modules = None
    test_selection = "all discovered modules"
    phases = (
        "validate inputs", "tests", "copy active sources", "build package", "prepare candidate image",
        "copy product to installed framework", "install project runtime", "start mcp", "final",
    )
    try:
        failed_step = "installation_lock"
        installation_lock.enter_context(_installation_lock(root, selection))
        failed_step = "validate_inputs"
        try:
            previous_image = _build_predecessor(selection)
        except LocalReleaseError:
            if image_mode != "existing":
                raise
            previous_image = None
        prior_image = previous_image or _launcher_image(selection)
        prior_project = selection.instance_id if prior_image is not None else None
        for phase in phases:
            print(f"Local release phase START: {phase}", file=sys.stderr, flush=True)
            failed_step = "validate_project_selection"
            if select_runtime_project(root) != selection:
                raise LocalReleaseError("local-release-project-selection-changed")
            failed_step = f"git_before_{phase.replace(' ', '_')}"
            sensitive = runner((
                "git", "diff", "--cached", "--name-only", "--", ":(glob)**/.env*", ":(glob)**/*.env",
            ), root)
            if (getattr(sensitive, "returncode", 1) != 0 or not isinstance(getattr(sensitive, "stdout", None), str)
                    or sensitive.stdout.strip()):
                raise LocalReleaseError("local-release-staged-environment-file-or-check-unavailable")
            try:
                result = runner((
                    "git", "add", "-A", "--", ".", ":(exclude,glob)**/.env*", ":(exclude,glob)**/*.env",
                ), root)
            except OSError as error:
                raise LocalReleaseError("local-release-git-failed") from error
            if getattr(result, "returncode", 0) != 0:
                raise LocalReleaseError("local-release-git-failed")
            try:
                result = runner(("git", "diff", "--cached", "--quiet"), root)
            except OSError as error:
                raise LocalReleaseError("local-release-git-failed") from error
            if getattr(result, "returncode", 0) == 1:
                try:
                    result = runner(("git", "commit", "-m", f"chore(release): simple local {phase}"), root)
                except OSError as error:
                    raise LocalReleaseError("local-release-git-failed") from error
                if getattr(result, "returncode", 0) != 0:
                    raise LocalReleaseError("local-release-git-failed")
            elif getattr(result, "returncode", 0) != 0:
                raise LocalReleaseError("local-release-git-failed")
            result = runner(("git", "status", "--porcelain", "--untracked-files=all"), root)
            if (getattr(result, "returncode", 1) != 0 or not isinstance(getattr(result, "stdout", None), str)
                    or result.stdout.strip()):
                raise LocalReleaseError("local-release-worktree-not-clean")

            if phase == "final":
                continue
            if phase == "validate inputs":
                failed_step = "validate_inputs"
                if image_mode == "existing":
                    for relative in sorted(_GENERATED_ASSETS):
                        asset = _project_path(root, Path(relative), label="image-asset")
                        if not asset.is_file() or asset.stat().st_size == 0:
                            raise LocalReleaseError(f"local-release-image-asset-missing: {relative}")
                from release_support import _native_release_sources
                _native_release_sources(selection)
                ane = _target(root, Path(".agents/skills/ane"), label="project-ane")
                for target in (product, installed, runtime, ane):
                    if target.exists():
                        _walk_regular_files(target)
                _read_version(root)
            elif phase == "tests":
                failed_step = "tests"
                argv = (
                    "uv", "run", "--project", str(root), "--locked", "--no-sync", "--python", "3.14",
                    "--managed-python", "--no-env-file", "--all-groups", "python", "-B", "-u",
                    str(Path(__file__).resolve().parents[2] / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/run_full_test_suite.py"), "--project-root", str(root),
                )
                argv += ("--image-mode", "existing")
                if default_runner:
                    temporary = _target(root, Path(".anechoic_tmp/simple_local_release"), label="test-log")
                    temporary.mkdir(parents=True, exist_ok=True)
                    with tempfile.NamedTemporaryFile(
                        mode="w+b", prefix=f"{run_id}-tests-", suffix=".log", dir=temporary, delete=False,
                    ) as log:
                        test_log_path = Path(log.name).relative_to(root).as_posix()
                        print(f"Local release tests; output log: {test_log_path}", file=sys.stderr, flush=True)
                        result = run_logged_test_process(argv, root, log)
                else:
                    try:
                        result = runner(argv, root)
                    except OSError as error:
                        raise LocalReleaseError("local-release-command-unavailable") from error
                if getattr(result, "returncode", 0) != 0:
                    detail = _failed_test_output(root, run_id, result, log_path=test_log_path)
                    raise LocalReleaseError(f"local-release-command-failed: {detail}")
            elif phase == "copy active sources":
                failed_step = "copy_active_sources"
                from project_runtime import bind_native_runtime, owned_temporary_root
                from release_support import _native_release_sources
                sources = _native_release_sources(selection)
                with bind_native_runtime(selection):
                    temporary = owned_temporary_root(root, "simple_local_release")
                with tempfile.TemporaryDirectory(prefix=f"{run_id}-sources-", dir=temporary) as directory:
                    staged = Path(directory)
                    identities = {source: _file_identity(source) for source in sources.values()}
                    for relative, source in sources.items():
                        target = staged / _relative(relative.as_posix(), label="source-path")
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, target)
                    if (_native_release_sources(selection) != sources
                            or any(_file_identity(path) != identity for path, identity in identities.items())
                            or select_runtime_project(root) != selection):
                        raise LocalReleaseError("local-release-source-changed")
                    _verify_package(staged, {
                        relative.as_posix(): identities[source] for relative, source in sources.items()
                    })
                    version_path, next_version_text = _read_version(root)
                    version_path.write_text(next_version_text, encoding="utf-8")
                    _clear_target(product, root=root, preserve=_PRESERVED_NAMES, label="product-root")
                    product_sources = product / "SUPERLAYER_1_METHODOLOGY_SOURCES"
                    product_sources.mkdir(parents=True, exist_ok=True)
                    _copy_tree(staged, product_sources, preserve=frozenset())
            elif phase == "copy product to installed framework":
                failed_step = "copy_product_to_installed_framework"
                _verify_package(package, package_identity)
                _verify_package(prepared_product, product_identity)
                _clear_target(installed, root=root, preserve=_PRESERVED_NAMES, label="installed-root")
                _copy_tree(prepared_product, installed, preserve=_PRESERVED_NAMES)
                _verify_package(installed, product_identity, preserve=_PRESERVED_NAMES)
            elif phase == "build package":
                failed_step = "build_package"
                from project_runtime import bind_native_runtime, owned_temporary_root, repository_root
                temporary = _target(root, Path(".anechoic_tmp/simple_local_release"), label="temporary-package")
                with bind_native_runtime(selection):
                    if repository_root(root) != root:
                        raise LocalReleaseError("local-release-temporary-project-mismatch")
                    owned_temporary_root(root, "simple_local_release")
                staging = Path(tempfile.mkdtemp(prefix=f"{run_id}-", dir=temporary))
                prepared_product = staging / "framework"
                prepared_product.mkdir()
                product_identity = {
                    entry.relative_to(product).as_posix(): _file_identity(entry)
                    for entry in _walk_regular_files(product)
                    if entry.relative_to(product).parts[0] not in _PRESERVED_NAMES
                }
                _copy_tree(product, prepared_product, preserve=_PRESERVED_NAMES)
                _verify_package(prepared_product, product_identity)
                package = staging / "package"
                package.mkdir()
                package_identity = _prepare_package(
                    root, prepared_product, package, refresh_assets=image_mode == "refresh",
                    control_relative=selection.control_relative,
                )
            elif phase == "prepare candidate image":
                failed_step = "prepare_candidate_image"
                _verify_package(package, package_identity)
                _verify_package(prepared_product, product_identity)
                image_temporary = staging / "image_builds"
                image_temporary.mkdir(mode=0o700)
                manager = _image_manager(
                    package, image_temporary,
                    project_root=root,
                    build_provenance=release_image_provenance(root, selection, cleanup_runner),
                )
                candidate_fingerprint = manager.identity(use_packaged_assets=True).fingerprint
                candidate_image = manager.resolve(use_packaged_assets=True)
                if (not isinstance(candidate_image, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", candidate_image)
                        or not isinstance(candidate_fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", candidate_fingerprint)):
                    raise LocalReleaseError("local-release-candidate-image-invalid")
                if manager.identity(use_packaged_assets=True).fingerprint != candidate_fingerprint:
                    raise LocalReleaseError("local-release-packaged-image-mismatch")
                _verify_package(package, package_identity)
                failed_step = "verify_candidate_image"
                canary_endpoint = verify_candidate_image(root, selection, package, staging, candidate_image, run_id=run_id)
            elif phase == "install project runtime":
                failed_step = "install_project_runtime"
                _verify_package(package, package_identity)
                _clear_target(runtime, root=root, preserve=frozenset(), label="simple-runtime")
                _copy_tree(package, runtime, preserve=frozenset())
                _verify_package(runtime, package_identity)
                manager = _image_manager(runtime, project_root=root)
                if (manager.resolve(explicit_id=candidate_image, build_if_missing=False) != candidate_image
                        or manager.identity(use_packaged_assets=True).fingerprint != candidate_fingerprint):
                    raise LocalReleaseError("local-release-installed-image-mismatch")
                ane = _target(root, Path(".agents/skills/ane"), label="project-ane")
                _clear_target(ane, root=root, preserve=frozenset(), label="project-ane")
                _copy_tree(runtime / "SKILLS/ane", ane, preserve=frozenset())
                _verify_package(ane, {path.removeprefix("SKILLS/ane/"): identity
                                      for path, identity in package_identity.items()
                                      if path.startswith("SKILLS/ane/")})
                with bind_native_runtime(selection):
                    _deploy_bootstrap(root, runtime)
            else:
                failed_step = "start_mcp"
                bootstrap = root / ".anechoic_runtime/start_mcp.py"
                if not bootstrap.is_file() or bootstrap.is_symlink():
                    raise LocalReleaseError("local-release-bootstrap-unavailable")
                cleanup = cleanup_stopped_containers(
                    root, selection.instance_id, selection.control_relative.as_posix(),
                    candidate_image, candidate_fingerprint, cleanup_runner,
                )
                if prior_image is not None:
                    cleanup.images.add(prior_image)
                if prior_project is not None:
                    try:
                        result = runner((
                            "docker", "ps", "--all", "--filter", f"label=org.anechoic.project={prior_project}",
                            "--format", "{{.ID}}",
                        ), root)
                    except OSError:
                        result = None
                    identifiers = (
                        [value for value in getattr(result, "stdout", "").splitlines() if re.fullmatch(r"[0-9a-f]{12,64}", value)]
                        if getattr(result, "returncode", 1) == 0 and isinstance(getattr(result, "stdout", ""), str) else []
                    )
                    if getattr(result, "returncode", 1) != 0:
                        cleanup_note = "A prior Project MCP container was retained because discovery was unavailable."
                        cleanup_pending = True
                    elif len(identifiers) > 1:
                        cleanup_note = "Prior Project MCP containers were retained because ownership was ambiguous."
                        cleanup_pending = True
                    elif identifiers and identifiers[0] in cleanup.attempted:
                        cleanup_note = f"Prior container {identifiers[0]} retained after its earlier removal attempt; no retry."
                        cleanup_pending = True
                    elif len(identifiers) == 1:
                        try:
                            inspected = runner((
                                "docker", "container", "inspect", "--format",
                                '{"Image":{{json .Image}},"State":{"Running":{{json .State.Running}}},'
                                '"Config":{"Labels":{{json .Config.Labels}}}}', identifiers[0],
                            ), root)
                            row = json.loads(getattr(inspected, "stdout", ""))
                            labels = row.get("Config", {}).get("Labels") if isinstance(row, dict) else None
                            if (
                                getattr(inspected, "returncode", 1) == 0
                                and isinstance(labels, dict)
                                and labels.get("org.anechoic.project") == prior_project
                                and labels.get("org.anechoic.service") == "mcp-http"
                                and labels.get("org.anechoic.control_root") == selection.control_relative.as_posix()
                                and labels.get("org.anechoic.host_project_root") == str(root)
                                and isinstance(row.get("State"), dict)
                                and isinstance(row["State"].get("Running"), bool)
                            ):
                                prior_id = row.get("Image", "")
                                protected = prior_id == candidate_image
                                if protected:
                                    cleanup_note = "Retained the exact candidate Project MCP container for canonical reuse."
                                else:
                                    image_labels(root, cleanup_runner, prior_id)
                                    cleanup.attempted.add(identifiers[0])
                                if row["State"]["Running"] and not protected:
                                    stopped = runner(("docker", "container", "stop", identifiers[0]), root)
                                    if getattr(stopped, "returncode", 1) != 0:
                                        cleanup_note = "The proven prior Project MCP container was retained because stop failed."
                                        cleanup_pending = True
                                if not cleanup_pending and not protected:
                                    removed = runner(("docker", "container", "rm", identifiers[0]), root)
                                    if getattr(removed, "returncode", 1) == 0:
                                        cleanup_note = f"Stopped and removed prior Project MCP container {identifiers[0]} with exact Project labels."
                                    else:
                                        cleanup_note = "A proven prior Project MCP container was retained because removal failed."
                                        cleanup_pending = True
                            else:
                                cleanup_note = "A prior Project MCP container was retained because its exact stopped ownership was not proven."
                                cleanup_pending = True
                        except (OSError, TypeError, ValueError, json.JSONDecodeError):
                            cleanup_note = "A prior Project MCP container was retained because inspection was unavailable."
                            cleanup_pending = True
                try:
                    mcp = runner((
                        sys.executable, str(bootstrap), "--project-root", str(root),
                        "--source-root", str(runtime), "--no-build",
                    ), root)
                except OSError as error:
                    raise LocalReleaseError("local-release-command-unavailable") from error
                if getattr(mcp, "returncode", 0) != 0:
                    raise LocalReleaseError("local-release-command-failed")
                output = getattr(mcp, "stdout", None)
                endpoint = output.strip() if isinstance(output, str) and output.strip() else None
                current_image = _launcher_image(selection)
                if current_image != candidate_image:
                    raise LocalReleaseError("local-release-installed-image-mismatch")
                try:
                    manager.mark_production_image(candidate_image)
                except ImageError as error:
                    cleanup.pending = True
                    cleanup.notes.append(f"Production image display tag failed: {error}")
                cleanup_stopped_containers(
                    root, selection.instance_id, selection.control_relative.as_posix(),
                    candidate_image, candidate_fingerprint, cleanup_runner, cleanup=cleanup,
                )
                try:
                    history = _project_path(
                        root, Path(".anechoic_runtime/simple_local_release/ready-images.json"),
                        label="simple-image-history",
                    )
                    previous_images = record_ready_images(history, selection.instance_id, candidate_image, prior_image)
                except (OSError, ValueError, LocalReleaseError):
                    cleanup.pending = True
                    cleanup.notes.append("Image history unavailable. Retained existing images.")
                else:
                    if prior_image == candidate_image:
                        cleanup.notes.append("Image reused. Retained existing rollback images.")
                    else:
                        cleanup_obsolete_images(root, candidate_image, candidate_fingerprint, cleanup, cleanup_runner,
                                                previous_images=previous_images)
                if prior_image is not None and previous_image is None and prior_image != candidate_image:
                    cleanup.pending = True
                    cleanup.notes.append("Prior image retained: readiness evidence unavailable.")
                cleanup_pending |= cleanup.pending
                cleanup_note = "\n".join([cleanup_note, *cleanup.notes])
                receipt = _project_path(
                    root, Path(".anechoic_runtime/simple_local_release/reports") / f"{run_id}.md",
                    label="simple-receipt",
                )
                receipt.parent.mkdir(parents=True, exist_ok=True)
                staging_note = _cleanup_staging(root, staging)
                staging = None
                receipt.write_text(
                    "# Simple local release receipt\n\n"
                    f"Run: `{run_id}`\n\n"
                    f"Image mode: `{image_mode}`\n\n"
                    f"Test scope: `{test_scope}`\n\n"
                    f"Selected test modules: {test_selection}\n\n"
                    f"Canary endpoint: `{canary_endpoint}`\n\n"
                    f"Endpoint: `{endpoint or 'not reported'}`\n\n"
                    + (f"Complete test output: `{test_log_path}`\n\n" if test_log_path is not None else "")
                    +
                    f"Image cleanup: {cleanup_note}\n\n{staging_note}",
                    encoding="utf-8",
                )
                receipt_path = receipt.relative_to(root).as_posix()
    except (Exception, KeyboardInterrupt) as error:
        if failed_step == "installation_lock":
            print(f"Local release installation lock failed: {error}", file=sys.stderr, flush=True)
        staging_note = _cleanup_staging(root, staging)
        relative = Path(".anechoic_runtime/simple_local_release/reports") / f"{run_id}.md"
        report_path: str | None = None
        try:
            report = _project_path(root, relative, label="simple-report")
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(
                "# Simple local release failed\n\n"
                f"Run: `{run_id}`\n\nStopped at: `{failed_step}`\n\n"
                f"Image mode: `{image_mode}`\n\n"
                f"Test scope: `{test_scope}`\n\n"
                f"Selected test modules: {test_selection}\n\n"
                f"Error class: `{type(error).__name__}`\n\n"
                + (f"{str(error)[:8500]}\n\n" if failed_step in {"tests", "verify_candidate_image"} else "")
                + (f"Complete test output: `{test_log_path}`\n\n" if test_log_path is not None else "")
                + (f"MCP started at: `{endpoint}`\n\n" if endpoint is not None else "")
                + ("\n".join(getattr(error, "__notes__", ())) + "\n\n" if getattr(error, "__notes__", ()) else "")
                +
                "Manual action required: inspect the current project state before any retry.\n\n"
                + ("Docker cleanup:\n" + "\n".join([cleanup_note, *cleanup.notes]) + "\n\n" if cleanup is not None else "")
                +
                f"{staging_note}",
                encoding="utf-8",
            )
            report_path = relative.as_posix()
        except (LocalReleaseError, OSError):
            pass
        return {
            "outcome": "failed",
            "failed_step": failed_step,
            "report_path": report_path,
            "error_type": type(error).__name__,
            "test_log_path": test_log_path,
            "endpoint": endpoint,
            "canary_endpoint": canary_endpoint,
            "test_scope": test_scope,
            "test_modules": selected_test_modules,
            "image_mode": image_mode,
        }
    finally:
        installation_lock.close()

    return {
        "outcome": "completed_with_cleanup_pending" if cleanup_pending else "completed",
        "failed_step": None, "report_path": None, "receipt_path": receipt_path,
        "test_log_path": test_log_path,
        "endpoint": endpoint,
        "canary_endpoint": canary_endpoint,
        "test_scope": test_scope,
        "test_modules": selected_test_modules,
        "image_mode": image_mode,
    }
