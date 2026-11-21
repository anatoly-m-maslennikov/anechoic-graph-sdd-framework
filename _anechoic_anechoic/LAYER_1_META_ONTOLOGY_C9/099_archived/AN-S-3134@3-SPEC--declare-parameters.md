---
atom_family: SPEC
atom_id: AN-S-3134
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-21T09:54:37.122704+00:00'
---

## Summary

Declare Parameters

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest.Parameters

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Parameters',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest',
    value_format=dict[str, object],
    field_options={'default_factory': 'dict'},
)
```

### Parameters

Paths below are relative to `ProjectManifest.parameters`. A group holds the settings in its rows. Retained settings describe the migrated configuration and its provenance. They have an effect only where a consumer implements that setting.

| Parameter | Meaning |
| --- | --- |
| `schema_version` | Version of the settings representation. |
| `project.key` | Stable key used to identify the Project in configuration. |
| `project.obsolete_names` | Former Project names retained for legacy lookup. |
| `project.repository_slug` | Repository identifier associated with the Project. |
| `paths.control_root` | Project-relative directory for the native control tree. The selected Manifest must belong to that tree. |
| `paths.framework_root` | Project-relative directory for the installed Framework. |
| `paths.journal_root` | Project-relative directory for the Project Journal. |
| `paths.legacy_migration_roots` | Project-relative legacy roots retained for migration. |
| `paths.projection_root` | Project-relative directory for generated Project views. |
| `paths.runtime_root` | Project-relative directory for runtime state. |
| `paths.temporary_root` | Project-relative directory for temporary operation data. |
| `artifact_timestamps.timezone` | Time zone used when an Artifact timestamp needs local interpretation. |
| `artifacts.creation_strictness` | Admission policy for creating Artifacts. |
| `artifacts.enabled_types` | Artifact types enabled for Project authoring. |
| `artifacts.default_types.analysis` | Default type for analysis Artifacts. |
| `artifacts.default_types.evaluation` | Default type for evaluation Artifacts. |
| `artifacts.default_types.requirement` | Default type for requirement Artifacts. |
| `artifacts.identity.automatic_number_ceiling` | Highest number that automatic Artifact ID allocation can assign. |
| `artifacts.routing.enabled_governance_loci` | Governance loci eligible for Artifact routing. |
| `authority.tiers.ordered` | Declared order of the authority tiers. |
| `authority.tiers.default` | Tier used when no tier is selected. |
| `authority_modes.default` | Authority mode for areas without a specific mode. |
| `authority_modes.governance` | Authority mode for governance. |
| `authority_modes.metamodel` | Authority mode for the metamodel. |
| `authority_modes.project` | Authority mode for Project declarations. |
| `authority_modes.semantics` | Authority mode for semantic declarations. |
| `git.required` | Whether a Git repository is required. |
| `git.initialize_if_missing` | Whether tooling may initialize a missing Git repository. |
| `git.commit_each_atom_edit` | Whether tooling commits each Atom edit. |
| `governance_surfaces.architecture_view` | Enable the architecture view. |
| `governance_surfaces.project_overview` | Enable the Project overview. |
| `governance_surfaces.relation_map` | Enable the relation map. |
| `governance_surfaces.requirement_catalog` | Enable the requirement catalog. |
| `governance_surfaces.scope_hub` | Enable the scope hub. |
| `project_mcp.http_port` | Loopback TCP port for Project MCP. An integer from 1 to 65535. |
| `project_mcp.tool_blacklist` | Exact Tool names to hide and reject for this Project. It can further restrict release workflows. |
| `project_mcp.release_workflows_enabled` | Boolean. `True` exposes MCP Tools that return host uv commands for Local Release and Public Release. `False` or omission hides both Tools and rejects direct calls. |
| `runtime.journal.storage` | Journal storage. `files` (default) uses append-only NDJSON; `duckdb` uses a durable standalone Journal table in the Project DuckDB file. |
| `runtime.project_mcp.build_if_missing` | Permit the launcher to build an absent compatible runtime image. |
| `runtime.project_mcp.build_timeout_seconds` | Maximum seconds the launcher allows for an image build. |
| `runtime.project_mcp.startup_timeout_seconds` | Maximum seconds the launcher allows for startup and readiness. |
| `runtime.workbench.import_graph` | Import Graph options. A mapping or omission enables it. `False` disables it. |
| `runtime.workbench.import_graph.include` | Named Project-relative authored files to include despite Git ignore rules. |
| `runtime.workbench.import_graph.python_roots` | Ordered Project-relative roots for resolving Python imports. |
| `runtime.workbench.public_url` | Workbench page URL used for saved query links when no request URL is available. |
| `runtime.workbench.result_ttl_seconds` | Retention time in seconds for query results that an open View does not pin. |
| `runtime.workbench.schema_mode` | Header column selection. `1` uses declared paths. `2` uses observed paths. |
| `runtime.workbench.storage` | Workbench table storage. `disk` (default) uses the Project DuckDB file; `memory` makes other Workbench tables ephemeral. Independent of Journal storage. |
| `projection.bindings.<parameter path>` | Source bindings for the named parameter in the generated configuration. |
| `projection.configuration` | Configuration identity used to generate the projection. |
| `projection.configuration_artifact` | Reference to the configuration Artifact. |
| `projection.configuration_sha256` | SHA-256 digest of the projected configuration. |
| `projection.generator` | Identifier of the generator that produced the projection. |
| `projection.generator_sha256` | SHA-256 digest of that generator. |
| `projection.generator_version` | Version of the generator used. |
| `projection.source_frontier` | Source revisions used by the generator. |
| `projection.source_frontier_sha256` | SHA-256 digest of the source frontier. |
| `projection.source_map` | Identifier or path of the generated source map. |
| `projection.source_map_sha256` | SHA-256 digest of the source map. |
| `projection.updated_at` | Time when the projection was generated. |
