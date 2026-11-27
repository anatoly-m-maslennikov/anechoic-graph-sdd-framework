"""Canonical fixed HTTP paths for the local ANECHOIC service."""

URL_PREFIX = "/anechoic"
MCP_PATH = f"{URL_PREFIX}/mcp"
HEALTH_PATH = f"{URL_PREFIX}/health"
IWE_CONSOLE_PATH = f"{URL_PREFIX}/iwe-console"
WORKBENCH_PATH = f"{URL_PREFIX}/workbench"
PROJECT_API_PATH = f"{URL_PREFIX}/{{project_name}}/api"
