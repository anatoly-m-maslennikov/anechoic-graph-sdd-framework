"""Workbench MCP App resource and tool interface."""

from .mcp_app_probe import call, list_resources, read_resource, tools

__all__ = ["call", "list_resources", "read_resource", "tools"]
