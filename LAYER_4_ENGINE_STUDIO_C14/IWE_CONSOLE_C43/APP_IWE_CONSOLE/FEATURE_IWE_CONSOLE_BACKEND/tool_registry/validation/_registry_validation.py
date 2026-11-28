"""Validate generated Tool registry contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import tool_registry_runtime as runtime


def _registry(
    asset_root: Path, inventory: runtime.ToolInventory
) -> dict[str, Any]:
    value = runtime.read_json(
        asset_root / runtime.REGISTRY_NAME, "generated-tool-registry"
    )
    version = value.get("schema_version")
    if (
        set(value) != runtime._REGISTRY_KEYS
        or type(version) is not int
        or version != runtime.SCHEMA_VERSION
    ):
        raise runtime.ToolRegistryAssetError(
            "generated-tool-registry-schema-invalid"
        )
    if value.get("inventory_sha256") != inventory.digest:
        raise runtime.ToolRegistryAssetError("generated-tool-registry-stale")
    if value.get("mcp_blacklist") != list(inventory.blacklist):
        raise runtime.ToolRegistryAssetError(
            "generated-tool-registry-blacklist-invalid"
        )
    if not isinstance(value.get("providers"), list) or not isinstance(
        value.get("public_tools"), list
    ):
        raise runtime.ToolRegistryAssetError(
            "generated-tool-registry-fields-invalid"
        )
    return value


def _provider_rows(
    value: dict[str, Any], inventory: runtime.ToolInventory
) -> list[dict[str, Any]]:
    rows = value["providers"]
    if len(rows) != len(inventory.providers):
        raise runtime.ToolRegistryAssetError(
            "generated-tool-registry-provider-count-invalid"
        )
    for row, entry in zip(rows, inventory.providers, strict=True):
        if (
            not isinstance(row, dict)
            or set(row) != runtime._GENERATED_PROVIDER_KEYS
        ):
            raise runtime.ToolRegistryAssetError(
                "generated-tool-registry-provider-invalid"
            )
        if {
            key: row[key]
            for key in runtime._GENERATED_PROVIDER_KEYS - {"tools"}
        } != runtime.provider_fields(entry):
            raise runtime.ToolRegistryAssetError(
                "generated-tool-registry-provider-stale"
            )
        if not isinstance(row["tools"], list):
            raise runtime.ToolRegistryAssetError(
                "generated-tool-registry-tools-invalid"
            )
    return rows


def _validator(schema: Any, label: str) -> runtime.Draft202012Validator | None:
    if schema is None and label == "output":
        return None
    if not isinstance(schema, dict):
        raise runtime.ToolRegistryAssetError(f"tool-{label}-schema-invalid")
    try:
        runtime.Draft202012Validator.check_schema(schema)
    except runtime.SchemaError as error:
        raise runtime.ToolRegistryAssetError(
            f"tool-{label}-schema-invalid"
        ) from error
    return runtime.Draft202012Validator(schema)


def _tools(
    entry: runtime.ProviderInventory, row: dict[str, Any], asset_root: Path
) -> tuple[tuple[runtime.types.Tool, ...], list[str]]:
    factory = runtime.provider_symbol(asset_root, entry, "descriptor_factory")
    try:
        current, names = runtime._tool_payloads(factory())
    except Exception as error:
        raise runtime.ToolRegistryAssetError(
            "tool-descriptor-factory-failed"
        ) from error
    if runtime.stable_json(current) != runtime.stable_json(row["tools"]):
        raise runtime.ToolRegistryAssetError(
            "generated-tool-registry-descriptor-stale"
        )
    try:
        tools = tuple(
            runtime.types.Tool.model_validate(tool) for tool in row["tools"]
        )
    except (TypeError, ValueError) as error:
        raise runtime.ToolRegistryAssetError(
            "generated-tool-registry-tools-invalid"
        ) from error
    for tool in tools:
        runtime._validator(tool.input_schema, "input")
        runtime._validator(tool.output_schema, "output")
    return tools, names


def _public_names(
    value: dict[str, Any], known: list[str], blacklist: frozenset[str]
) -> set[str]:
    names = value["public_tools"]
    if not all(isinstance(name, str) for name in names) or len(names) != len(
        set(names)
    ):
        raise runtime.ToolRegistryAssetError(
            "generated-tool-registry-public-tools-invalid"
        )
    expected = {name for name in known if name not in blacklist}
    if set(names) != expected:
        raise runtime.ToolRegistryAssetError(
            "generated-tool-registry-public-tools-stale"
        )
    return expected
