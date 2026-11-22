"""Package and installation phases of the direct local Release."""

from contextlib import ExitStack
import json
from pathlib import Path
import re
import shutil

from .release_assets import LocalReleaseError
from .release_image_provenance import release_image_provenance
from .release_inputs import read_release_selection
from .local_release_safety import _new_staging_directory, _release_lock
from .release_support import (
    _PRESERVED_NAMES, _GENERATED_ASSETS, _native_release_sources, _file_identity,
    _relative, _verify_package, _clear_target, _copy_tree, _walk_regular_files,
    _prepare_package, _image_manager, _target, _install_bootstrap, _project_path,
)


def copy_sources(root, selection, run_id, product):
    sources = _native_release_sources(selection)
    with ExitStack() as source_stage:
        staged = _new_staging_directory(root, f"{run_id}-sources-")
        source_stage.callback(shutil.rmtree, staged)
        identities = {source: _file_identity(source) for source in sources.values()}
        for relative, source in sources.items():
            target = staged / _relative(relative.as_posix(), label="source-path")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        if (_native_release_sources(selection) != sources
                or any(_file_identity(path) != identity for path, identity in identities.items())
                or read_release_selection(root) != selection):
            raise LocalReleaseError("local-release-source-changed")
        _verify_package(staged, {
            relative.as_posix(): identities[source] for relative, source in sources.items()
        })
        _clear_target(product, root=root, preserve=_PRESERVED_NAMES, label="product-root")
        product_sources = product / "SUPERLAYER_1_METHODOLOGY_SOURCES"
        product_sources.mkdir(parents=True, exist_ok=True)
        _copy_tree(staged, product_sources, preserve=frozenset())


def copy_product(root, selection, installation_lock, package, package_identity,
                 prepared_product, product_identity, installed):
    installation_lock.enter_context(_release_lock(
        root, selection.launcher_state.relative_to(root) / "launch.lock", "launcher",
    ))
    _verify_package(package, package_identity)
    _verify_package(prepared_product, product_identity)
    _clear_target(installed, root=root, preserve=_PRESERVED_NAMES, label="installed-root")
    _copy_tree(prepared_product, installed, preserve=_PRESERVED_NAMES)
    _verify_package(installed, product_identity, preserve=_PRESERVED_NAMES)


def build_package(root, selection, product, staging):
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
    package_identity = _prepare_package(root, prepared_product, package,
                                           control_relative=selection.control_relative)
    return prepared_product, product_identity, package, package_identity


def prepare_image(root, selection, staging, package, package_identity,
                  prepared_product, product_identity, cleanup_runner):
    _verify_package(package, package_identity)
    _verify_package(prepared_product, product_identity)
    image_temporary = staging / "image_builds"
    image_temporary.mkdir(mode=0o700)
    manager = _image_manager(package, image_temporary, project_root=root,
                               build_provenance=release_image_provenance(root, selection, cleanup_runner))
    fingerprint = manager.identity(use_packaged_assets=True).fingerprint
    image = manager.resolve(use_packaged_assets=True)
    if (not isinstance(image, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", image)
            or not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)):
        raise LocalReleaseError("local-release-candidate-image-invalid")
    if manager.identity(use_packaged_assets=True).fingerprint != fingerprint:
        raise LocalReleaseError("local-release-packaged-image-mismatch")
    _verify_package(package, package_identity)
    return manager, image, fingerprint


def install_runtime(root, package, package_identity, runtime, candidate_image, candidate_fingerprint):
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
    _install_bootstrap(root, runtime, package_identity)


def validate_inputs(root, selection, product, installed, runtime):
    settings = selection.parameters.get("project_mcp")
    port = settings.get("http_port") if isinstance(settings, dict) else None
    if type(port) is not int or not 1 <= port <= 65535:
        raise LocalReleaseError("local-release-production-port-invalid")
    for relative in sorted(_GENERATED_ASSETS):
        asset = _project_path(root, Path(relative), label="image-asset")
        if not asset.is_file() or asset.stat().st_size == 0:
            raise LocalReleaseError(f"local-release-image-asset-missing: {relative}")
        if asset.stat().st_size > 1_048_576 or not isinstance(json.loads(asset.read_text(encoding="utf-8")), dict):
            raise LocalReleaseError(f"local-release-image-asset-invalid: {relative}")
    _native_release_sources(selection)
    ane = _target(root, Path(".agents/skills/ane"), label="project-ane")
    for target in (product, installed, runtime, ane):
        if target.exists():
            _walk_regular_files(target)
    return port
