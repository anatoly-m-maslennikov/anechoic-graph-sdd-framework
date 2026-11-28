"""Timeout and build options for Project MCP launch."""

from importlib import import_module


def _launcher():
    return import_module(
        "MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.project_mcp_launcher"
    )


def _launch_options(
    selection, timeout, build_timeout, build_if_missing, settings=None
):
    startup_timeout = _launcher()._positive_timeout(
        timeout,
        ceiling=_launcher()._DEFAULT_STARTUP_TIMEOUT,
        default=_launcher()._DEFAULT_STARTUP_TIMEOUT,
    )
    bounded_build_timeout = _launcher()._positive_timeout(
        build_timeout,
        ceiling=_launcher()._DEFAULT_BUILD_TIMEOUT,
        default=_launcher()._DEFAULT_BUILD_TIMEOUT,
    )
    if type(build_if_missing) is not bool:
        raise _launcher().LaunchError("IMAGE_REFUSED")
    if settings is not None:
        return (
            min(startup_timeout, settings.startup_timeout_seconds),
            min(bounded_build_timeout, settings.build_timeout_seconds),
            build_if_missing and settings.build_if_missing,
        )
    return _runtime_options(
        selection, startup_timeout, bounded_build_timeout, build_if_missing
    )


def _runtime_options(
    selection, startup_timeout, bounded_build_timeout, build_if_missing
):
    runtime = selection.parameters.get("runtime", {})
    mcp_options = (
        runtime.get("project_mcp", {})
        if isinstance(runtime, _launcher().Mapping)
        else None
    )
    if (
        not isinstance(mcp_options, _launcher().Mapping)
        or type(mcp_options.get("build_if_missing", True)) is not bool
    ):
        raise _launcher().LaunchError("PROJECT_SELECTION_REFUSED")
    startup_timeout = min(
        startup_timeout,
        _launcher()._positive_timeout(
            mcp_options.get(
                "startup_timeout_seconds", _launcher()._DEFAULT_STARTUP_TIMEOUT
            ),
            ceiling=_launcher()._DEFAULT_STARTUP_TIMEOUT,
            default=_launcher()._DEFAULT_STARTUP_TIMEOUT,
        ),
    )
    bounded_build_timeout = min(
        bounded_build_timeout,
        _launcher()._positive_timeout(
            mcp_options.get(
                "build_timeout_seconds", _launcher()._DEFAULT_BUILD_TIMEOUT
            ),
            ceiling=_launcher()._DEFAULT_BUILD_TIMEOUT,
            default=_launcher()._DEFAULT_BUILD_TIMEOUT,
        ),
    )
    build_if_missing = build_if_missing and mcp_options.get(
        "build_if_missing", True
    )
    return startup_timeout, bounded_build_timeout, build_if_missing
