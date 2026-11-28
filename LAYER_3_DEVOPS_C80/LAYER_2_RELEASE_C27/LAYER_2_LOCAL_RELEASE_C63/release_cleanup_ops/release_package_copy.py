"""Copy and verify the inputs of a Local Release package."""


def prepare_package(
    root, product, package, control_relative, manifest_path, tracked, gate
):
    if len(
        control_relative.parts
    ) != 1 or not control_relative.name.startswith(
        (".anechoic_", "_anechoic_")
    ):
        raise gate.LocalReleaseError("local-release-project-selection-invalid")
    control_root = gate._project_path(
        root, control_relative, label="control-root", require_exists=True
    )
    if not control_root.is_dir():
        raise gate.LocalReleaseError("local-release-project-selection-invalid")
    excluded = frozenset(
        {
            control_relative.name.casefold(),
            ".anechoic_runtime",
            ".anechoic_tmp",
            ".runtime",
            ".git",
            ".pytest_cache",
            "__pycache__",
            ".mypy_cache",
            ".ruff_cache",
            ".venv",
            ".vite",
            "node_modules",
        }
    )
    sources, inventories = gate._package_sources(
        root, product, package, excluded, manifest_path, tracked
    )
    expected = _copy_and_check(
        root, product, package, excluded, tracked, sources, inventories, gate
    )
    _check_required(expected, gate)
    gate._verify_package(package, expected)
    return expected


def _copy_and_check(
    root, product, package, excluded, tracked, sources, inventories, gate
):
    expected = {}
    for source, relative in sources:
        expected[relative.as_posix()] = gate._file_identity(source)
        destination = package / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        gate.shutil.copy2(source, destination)
    for source, members in inventories:
        current = gate._walk_package_tree(
            root, source, product, excluded, tracked
        )
        if current != members:
            raise gate.LocalReleaseError(
                "local-release-package-source-changed"
            )
    for source, relative in sources:
        if gate._file_identity(source) != expected[relative.as_posix()]:
            raise gate.LocalReleaseError(
                "local-release-package-source-changed"
            )
    return expected


def _check_required(expected, gate):
    child_inputs = tuple(
        f"{child}/{name}"
        for child in (
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine",
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release",
            "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/setup",
        )
        for name in ("pyproject.toml", "uv.lock")
    )
    for relative in (
        "version.toml",
        *child_inputs,
        "SKILLS/ane/SKILL.md",
        "LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/"
        "FEATURE_SKILLS/ane/SKILL.md",
        gate._BOOTSTRAP.as_posix(),
        *gate._GENERATED_ASSETS,
    ):
        if relative not in expected:
            raise gate.LocalReleaseError(
                "local-release-package-source-unavailable"
            )
