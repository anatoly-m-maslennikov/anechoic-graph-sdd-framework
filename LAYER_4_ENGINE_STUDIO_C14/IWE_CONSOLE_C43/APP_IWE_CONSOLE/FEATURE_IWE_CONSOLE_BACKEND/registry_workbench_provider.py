"""Registry provider that delegates the retained Workbench frontier."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    ExplicitBlockingRuntimeFailure,
)
from .query_templates import (
    QUERY_TEMPLATE,
    descriptor as template_descriptor,
    run_arguments,
)
from .workbench_links import (
    context_project_root,
    public_saved,
    public_workspace,
    validate_reference,
)
from .workbench_tools import (
    LOAD,
    RUN,
    WORKSPACE_GET,
    WORKSPACE_OPEN,
    native_tools,
)


class WorkbenchProvider:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    async def call(
        self, name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        if name == QUERY_TEMPLATE:
            try:
                arguments = run_arguments(arguments)
            except ValueError as error:
                raise ExplicitBlockingRuntimeFailure(
                    "query_error", str(error)
                ) from error
            name = RUN
        if name == RUN:
            arguments = {"result_delivery": "auto", **arguments}
        return await self.gateway.workbench.call(name, arguments)

    def prepare_arguments(
        self, name: str, arguments: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        if name != LOAD or not isinstance(arguments.get("reference"), str):
            return arguments
        try:
            reference = validate_reference(
                arguments["reference"],
                getattr(context, "request", None),
                self.gateway.selection,
                context_project_root(context),
            )
        except ValueError as error:
            raise ExplicitBlockingRuntimeFailure(
                "query_error", str(error)
            ) from error
        return {**arguments, "reference": reference}

    def present_result(
        self, name: str, value: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        request = getattr(context, "request", None)
        root = context_project_root(context)
        value = public_saved(value, request, self.gateway.selection, root)
        return (
            public_workspace(value, request, self.gateway.selection, root)
            if request is not None
            and name
            in {
                WORKSPACE_OPEN,
                WORKSPACE_GET,
            }
            else value
        )

    async def close(self) -> None:
        return None


def create_provider(_root: Path, gateway: Any) -> WorkbenchProvider:
    return WorkbenchProvider(gateway)


def tool_descriptors():
    return (*native_tools(), template_descriptor())
