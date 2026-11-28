"""Load the generated MCP Tool registry and dispatch Providers."""

from __future__ import annotations

from pydantic import ConfigDict, InstanceOf
from pydantic.dataclasses import dataclass

import inspect
from pathlib import Path
from typing import Annotated, Any

from jsonschema import (
    Draft202012Validator,
    SchemaError as SchemaError,
    ValidationError,
)
from mcp import types

from ._registry_validation import (
    _provider_rows,
    _public_names,
    _registry,
    _tools,
    _validator,
)
from ...generate_tool_registry import _tool_payloads as _tool_payloads
from ...tool_registry_assets import (
    INVENTORY_NAME,
    REGISTRY_NAME,
    SCHEMA_VERSION as SCHEMA_VERSION,
    ProviderInventory as ProviderInventory,
    ToolInventory as ToolInventory,
    ToolRegistryAssetError,
    inventory_digest,
    provider_fields as provider_fields,
    read_inventory,
    read_json as read_json,
    stable_json as stable_json,
)
from ...tool_registry_imports import provider_symbol


_REGISTRY_KEYS = frozenset(
    {
        "schema_version",
        "inventory_sha256",
        "mcp_blacklist",
        "providers",
        "public_tools",
    }
)
_GENERATED_PROVIDER_KEYS = frozenset(
    {"provider_id", "module", "factory", "descriptor_factory", "tools"}
)


class ToolRegistryRuntimeError(RuntimeError):
    """A runtime cannot safely expose an incomplete or stale registry."""


class ToolRegistryStaleError(ToolRegistryRuntimeError):
    """Installed registration changed since this runtime loaded it."""


class ToolInputValidationError(ValueError):
    """The request does not meet the registered generic Tool contract."""


class ToolOutputValidationError(RuntimeError):
    """A Provider returned data outside its registered Tool contract."""


async def _await(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


async def _close(value: Any) -> None:
    close = getattr(value, "close", None)
    if callable(close):
        try:
            await _await(close())
        except Exception:
            return


@dataclass(
    config=ConfigDict(
        strict=True, extra="forbid", arbitrary_types_allowed=True
    )
)
class ProviderBinding:
    factory: Any
    root: Path
    gateway: Any
    provider: Any = None

    async def resolve(self) -> Any:
        if self.provider is not None:
            return self.provider
        try:
            candidate = await _await(self.factory(self.root, self.gateway))
        except Exception as error:
            raise ToolRegistryRuntimeError(
                "tool-provider-factory-failed"
            ) from error
        if not callable(getattr(candidate, "call", None)) or not callable(
            getattr(candidate, "close", None)
        ):
            await _close(candidate)
            raise ToolRegistryRuntimeError("tool-provider-contract-invalid")
        self.provider = candidate
        return candidate

    async def close(self) -> None:
        if self.provider is not None:
            provider, self.provider = self.provider, None
            await _close(provider)


@dataclass(
    config=ConfigDict(
        strict=True, extra="forbid", arbitrary_types_allowed=True
    ),
    frozen=True,
)
class RegisteredTool:
    binding: ProviderBinding
    input_validator: Draft202012Validator
    output_validator: Draft202012Validator | None


@dataclass(
    config=ConfigDict(
        strict=True, extra="forbid", arbitrary_types_allowed=True
    )
)
class ActiveToolRegistry:
    tools: tuple[types.Tool, ...]
    routes: Annotated[dict[str, RegisteredTool], InstanceOf()]
    bindings: tuple[ProviderBinding, ...]
    global_blacklist: frozenset[str]
    asset_root: Path
    registry_revision: str
    inventory_revision: str

    def ensure_current(self) -> None:
        try:
            current_registry = inventory_digest(
                self.asset_root / REGISTRY_NAME
            )
            current_inventory = inventory_digest(
                self.asset_root / INVENTORY_NAME
            )
        except ToolRegistryAssetError as error:
            raise ToolRegistryStaleError("tool-registry-stale") from error
        if (current_registry, current_inventory) != (
            self.registry_revision,
            self.inventory_revision,
        ):
            raise ToolRegistryStaleError("tool-registry-stale")

    def permits(self, name: str) -> bool:
        return name not in self.global_blacklist and name in self.routes

    async def call(
        self, name: str, arguments: dict[str, Any], *, context: Any = None
    ) -> dict[str, Any]:
        self.ensure_current()
        if not self.permits(name):
            raise ToolRegistryRuntimeError("tool-unavailable")
        registered = self.routes[name]
        try:
            registered.input_validator.validate(arguments)
        except ValidationError as error:
            raise ToolInputValidationError("tool-input-invalid") from error
        provider = await registered.binding.resolve()
        arguments = await _provider_hook(
            provider, "prepare_arguments", name, arguments, context
        )
        self.ensure_current()
        value = await _await(provider.call(name, arguments))
        if not isinstance(value, dict):
            raise ToolOutputValidationError("tool-provider-result-invalid")
        if registered.output_validator is not None:
            try:
                registered.output_validator.validate(value)
            except ValidationError as error:
                raise ToolOutputValidationError(
                    "tool-output-invalid"
                ) from error
        return await _provider_hook(
            provider, "present_result", name, value, context
        )

    async def close(self) -> None:
        for binding in self.bindings:
            await binding.close()


async def _provider_hook(
    provider: Any, name: str, tool: str, value: dict[str, Any], context: Any
) -> dict[str, Any]:
    hook = getattr(provider, name, None)
    result = (
        await _await(hook(tool, value, context)) if callable(hook) else value
    )
    if not isinstance(result, dict):
        raise ToolRegistryRuntimeError(f"tool-provider-{name}-invalid")
    return result


def _runtime_error(error: Exception) -> ToolRegistryRuntimeError:
    return ToolRegistryRuntimeError(f"tool-registry-unavailable: {error}")


def _frontier(asset_root, inventory, value, rows):
    tool_results = [
        _tools(entry, row, asset_root)
        for entry, row in zip(inventory.providers, rows, strict=True)
    ]
    tools_by_provider = [tools for tools, _ in tool_results]
    names = [
        name for _, provider_names in tool_results for name in provider_names
    ]
    if len(names) != len(set(names)):
        raise ToolRegistryAssetError("generated-tool-registry-tool-duplicates")
    blacklist = frozenset(inventory.blacklist)
    valid_names = [tool.name for tools in tools_by_provider for tool in tools]
    if not valid_names:
        raise ToolRegistryAssetError("generated-tool-registry-frontier-empty")
    public = _public_names(value, valid_names, blacklist)
    return tools_by_provider, blacklist, public


def _active_registry(
    tools,
    routes,
    bindings,
    blacklist,
    asset_root,
    registry_revision,
    inventory_digest_value,
):
    active = ActiveToolRegistry(
        tools,
        routes,
        bindings,
        blacklist,
        asset_root,
        registry_revision,
        inventory_digest_value,
    )
    active.ensure_current()
    return active


def load_active_registry(
    asset_root: Path, root: Path, gateway: Any
) -> ActiveToolRegistry:
    try:
        registry_revision = inventory_digest(asset_root / REGISTRY_NAME)
        inventory = read_inventory(asset_root)
        value = _registry(asset_root, inventory)
        rows = _provider_rows(value, inventory)
        tools_by_provider, blacklist, public = _frontier(
            asset_root, inventory, value, rows
        )
        bindings = tuple(
            ProviderBinding(
                provider_symbol(asset_root, entry, "factory"), root, gateway
            )
            for entry in inventory.providers
        )
        routes = {
            tool.name: RegisteredTool(
                binding,
                _validator(tool.input_schema, "input"),
                _validator(tool.output_schema, "output"),
            )
            for binding, tools in zip(bindings, tools_by_provider, strict=True)
            for tool in tools
            if tool.name in public
        }
        tools = tuple(
            tool
            for tools in tools_by_provider
            for tool in tools
            if tool.name in public
        )
        return _active_registry(
            tools,
            routes,
            bindings,
            blacklist,
            asset_root,
            registry_revision,
            inventory.digest,
        )
    except ToolRegistryAssetError as error:
        raise _runtime_error(error) from error


__all__ = [
    "ActiveToolRegistry",
    "ToolInputValidationError",
    "ToolOutputValidationError",
    "ToolRegistryRuntimeError",
    "ToolRegistryStaleError",
    "load_active_registry",
]
