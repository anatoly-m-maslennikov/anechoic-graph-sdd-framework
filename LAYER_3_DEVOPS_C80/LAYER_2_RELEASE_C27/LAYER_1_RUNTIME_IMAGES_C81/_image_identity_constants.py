"""Paths and filters for release image input inventory."""

import re

SOURCE_LAYERS = ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58")

SELECTOR = "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/project.toml"
ENGINE = "LAYER_4_ENGINE_STUDIO_C14"
DOCKER_ROOT = ENGINE + "/MCP_PATCHBAY_C21/FEATURE_MCP/docker"
DOCKERFILE = DOCKER_ROOT + "/Dockerfile"
DOCKERIGNORE = DOCKERFILE + ".dockerignore"
LICENSE_INPUTS = (
    "LICENSE",
    "LICENSE.TLDR.md",
    DOCKER_ROOT + "/DuckPGQ.LICENSE",
)
RETIRED_ASSETS = frozenset(
    ENGINE + "/" + directory + "/" + name
    for directory, names in (
        (
            "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND",
            ("canonical_relation_registry.json", "workbench_schema.json"),
        ),
        (
            "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE",
            ("status_model.json", "candidate_schema.json"),
        ),
    )
    for name in names
)
TOOL_REGISTRY = (
    ENGINE + "/IWE_CONSOLE_C43/APP_IWE_CONSOLE/"
    "FEATURE_IWE_CONSOLE_BACKEND/tool_registry.json"
)
_EXCLUDED = frozenset(
    {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".nox",
        ".venv",
        ".virtualenv",
        "venv",
        "virtualenv",
        "node_modules",
        "testcache",
        ".testcache",
        "tmp",
        "vault",
        ".vault",
        "secrets",
        ".secrets",
        "credentials",
        ".credentials",
    }
)
_SECRETS = frozenset(
    {
        "auth.json",
        "credentials.json",
        "token.txt",
        "token.json",
        "secrets.json",
        "secrets.txt",
        ".DS_Store",
    }
)
_REQUIRED = (
    "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml",
    "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/uv.lock",
    "version.toml",
    DOCKERFILE,
    DOCKERIGNORE,
    *LICENSE_INPUTS,
    TOOL_REGISTRY,
)
_BETA_ROOTS = frozenset(
    {
        "KERNEL_MIXER_beta_C67",
        "ORCHESTRATOR_beta_C68",
        "WORKERS_beta_C69",
        "API_MIXER_beta_C91",
    }
)
_BETA_REQUIRED = tuple(
    f"{ENGINE}/{path}"
    for path in (
        "FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/"
        "FEATURE_MODEL_VALIDATION/project_admission__pub.py",
        "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/"
        "native_snapshot_cli.py",
        "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/"
        "realization_graph_cli.py",
        "KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/"
        "DATABASE_SERVER_beta_C71__shared.py",
        "ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__shared.py",
        "ORCHESTRATOR_beta_C68/warm_worker.py",
        "WORKERS_beta_C69/WORKERS_beta_C69__shared.py",
        "WORKERS_beta_C69/warm_worker.py",
        "ORCHESTRATOR_beta_C68/project_peer_owner.py",
        "ORCHESTRATOR_beta_C68/shared_peer_owner.py",
        "API_MIXER_beta_C91/API_MIXER_beta_C91__shared.py",
        "API_MIXER_beta_C91/shared_runtime.py",
    )
)
_BETA_DIRECTORY = re.compile(r"_beta_C[0-9]+\Z")
_CURRENT_ONLY = frozenset(
    {
        "KERNEL_MIXER_C59",
        "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND",
    }
)
