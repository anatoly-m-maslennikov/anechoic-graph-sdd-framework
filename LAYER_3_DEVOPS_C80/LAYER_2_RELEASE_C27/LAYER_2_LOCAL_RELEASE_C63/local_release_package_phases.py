"""Package and installation phases of the direct local Release."""

import json
import re
import shutil
from contextlib import ExitStack
from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    _LAYER_NAMES,
    LocalReleaseError,
    _clear_target,
    _copy_tree,
    _file_identity,
    _image_manager,
    _install_bootstrap,
    _native_release_sources,
    _new_staging_directory,
    _project_path,
    _relative,
    _target,
    _verify_package,
    _walk_regular_files,
    read_release_selection,
    release_image_provenance,
)

from .release_support import (
    _GENERATED_ASSETS,
    _PRESERVED_NAMES,
    _prepare_package,
)


def stage_active_sources(root, selection, staged, *, tracked=None):
    sources = _native_release_sources(selection)
    if tracked is not None and any(
        source.relative_to(root) not in tracked for source in sources.values()
    ):
        raise LocalReleaseError("local-release-untracked-active-source")
    identities = {
        source: _file_identity(source) for source in sources.values()
    }
    for relative, source in sources.items():
        target = staged / _relative(relative.as_posix(), label="source-path")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    if (
        _native_release_sources(selection) != sources
        or any(
            _file_identity(path) != identity
            for path, identity in identities.items()
        )
        or read_release_selection(root) != selection
    ):
        raise LocalReleaseError("local-release-source-changed")
    for name in _LAYER_NAMES:
        (staged / name).mkdir(exist_ok=True)
    expected = {
        relative.as_posix(): identities[source]
        for relative, source in sources.items()
    }
    _verify_package(staged, expected)
    return expected


def copy_sources(root, selection, run_id, product):
    with ExitStack() as source_stage:
        staged = _new_staging_directory(root, f"{run_id}-sources-")
        source_stage.callback(shutil.rmtree, staged)
        stage_active_sources(root, selection, staged)
        for name in _LAYER_NAMES:
            destination = _target(root, Path(name), label="delivery-layer")
            _clear_target(
                destination,
                root=root,
                preserve=frozenset(),
                label="delivery-layer",
            )
            _copy_tree(staged / name, destination, preserve=frozenset())


def copy_product(
    root,
    selection,
    installation_lock,
    package,
    package_identity,
    prepared_product,
    product_identity,
    installed,
):
    _verify_package(package, package_identity)
    _verify_package(prepared_product, product_identity)
    preserve = _PRESERVED_NAMES | {
        "SUPERLAYER_1_METHODOLOGY_SOURCES",
        "applicable_methodology",
    }
    _clear_target(
        installed, root=root, preserve=preserve, label="installed-root"
    )
    _copy_tree(prepared_product, installed, preserve=preserve)
    _verify_package(installed, product_identity, preserve=preserve)


def build_package(
    root, selection, product, staging, *, active_sources=False, tracked=None
):
    prepared_product = staging / "framework"
    prepared_product.mkdir()
    product_identity = (
        stage_active_sources(
            root, selection, prepared_product, tracked=tracked
        )
        if active_sources
        else _stage_delivery_layers(root, prepared_product)
    )
    package = staging / "package"
    package.mkdir()
    package_identity = _prepare_package(
        root,
        prepared_product,
        package,
        control_relative=selection.control_relative,
        manifest_path=selection.manifest_path,
        tracked=tracked,
    )
    return prepared_product, product_identity, package, package_identity


def _stage_delivery_layers(root, prepared_product):
    for name in _LAYER_NAMES:
        destination = prepared_product / name
        destination.mkdir()
        _copy_tree(root / name, destination, preserve=frozenset())
    product_identity = {
        entry.relative_to(prepared_product).as_posix(): _file_identity(entry)
        for entry in _walk_regular_files(prepared_product)
    }
    _verify_package(prepared_product, product_identity)
    return product_identity


def prepare_image(
    root,
    selection,
    staging,
    package,
    package_identity,
    prepared_product,
    product_identity,
    cleanup_runner,
    *,
    provenance=None,
):
    _verify_package(package, package_identity)
    _verify_package(prepared_product, product_identity)
    image_temporary = staging / "image_builds"
    image_temporary.mkdir(mode=0o700, exist_ok=True)
    manager = _image_manager(
        package,
        image_temporary,
        project_root=root,
        build_provenance=provenance
        or release_image_provenance(root, selection, cleanup_runner),
    )
    fingerprint = manager.identity(use_packaged_assets=True).fingerprint
    image = manager.resolve(use_packaged_assets=True)
    if (
        not isinstance(image, str)
        or not re.fullmatch(r"sha256:[0-9a-f]{64}", image)
        or not isinstance(fingerprint, str)
        or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
    ):
        raise LocalReleaseError("local-release-candidate-image-invalid")
    if manager.identity(use_packaged_assets=True).fingerprint != fingerprint:
        raise LocalReleaseError("local-release-packaged-image-mismatch")
    _verify_package(package, package_identity)
    return manager, image, fingerprint


def restore_image(root, staging, package, provenance, image, fingerprint):
    manager = _image_manager(
        package,
        staging / "image_builds",
        project_root=root,
        build_provenance=provenance,
    )
    if (
        manager.resolve(explicit_id=image, build_if_missing=False) != image
        or manager.identity(use_packaged_assets=True).fingerprint
        != fingerprint
    ):
        raise LocalReleaseError("local-release-resume-image-unverified")
    return manager


def install_runtime(
    root,
    package,
    package_identity,
    runtime,
    candidate_image,
    candidate_fingerprint,
):
    _verify_package(package, package_identity)
    _clear_target(
        runtime, root=root, preserve=frozenset(), label="simple-runtime"
    )
    _copy_tree(package, runtime, preserve=frozenset())
    _verify_package(runtime, package_identity)
    manager = _image_manager(runtime, project_root=root)
    if (
        manager.resolve(explicit_id=candidate_image, build_if_missing=False)
        != candidate_image
        or manager.identity(use_packaged_assets=True).fingerprint
        != candidate_fingerprint
    ):
        raise LocalReleaseError("local-release-installed-image-mismatch")
    ane = _target(root, Path(".agents/skills/ane"), label="project-ane")
    _clear_target(ane, root=root, preserve=frozenset(), label="project-ane")
    _copy_tree(runtime / "SKILLS/ane", ane, preserve=frozenset())
    _verify_package(
        ane,
        {
            path.removeprefix("SKILLS/ane/"): identity
            for path, identity in package_identity.items()
            if path.startswith("SKILLS/ane/")
        },
    )
    _install_bootstrap(root, runtime, package_identity)


def validate_package_inputs(root, selection):
    for relative in sorted(_GENERATED_ASSETS):
        asset = _project_path(root, Path(relative), label="image-asset")
        if not asset.is_file() or asset.stat().st_size == 0:
            raise LocalReleaseError(
                f"local-release-image-asset-missing: {relative}"
            )
        if asset.stat().st_size > 1_048_576 or not isinstance(
            json.loads(asset.read_text(encoding="utf-8")), dict
        ):
            raise LocalReleaseError(
                f"local-release-image-asset-invalid: {relative}"
            )
    _native_release_sources(selection)


def validate_inputs(
    root,
    selection,
    product,
    installed,
    runtime,
    *,
    source_root=None,
    source_selection=None,
):
    settings = selection.parameters.get("project_mcp")
    port = settings.get("http_port") if isinstance(settings, dict) else None
    if type(port) is not int or not 1 <= port <= 65535:
        raise LocalReleaseError("local-release-production-port-invalid")
    validate_package_inputs(source_root or root, source_selection or selection)
    ane = _target(root, Path(".agents/skills/ane"), label="project-ane")
    for target in (product, installed, runtime, ane):
        if target is not None and target.exists():
            _walk_regular_files(target)
    return port
