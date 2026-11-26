---
atom_family: SPEC
atom_id: AN-S-3134
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 12
  updated_at: "2026-11-25T23:19:13.568186+00:00"
---

## Summary

Declare Parameters

## Claim

### Parameters

Validate Project Manifest settings against their declared schema. Reject missing required keys, duplicate keys, unknown keys in closed mappings, invalid types, and invalid values.

Paths below are relative to `ProjectManifest.parameters`. The Project Manifest owns Project identity and all Operator-selected Project settings. Governing Specs declare applicable parameters and constraints. Runtime paths are derived from the selected Project and its control root; they are not separately configured here.

Component and Component Seed Manifests own Structure. The Meta-Ontology owns the base Model. Project Config Custom Model is the sole source of Project-specific Model declarations. Project Config owns release Workflows; the Project Manifest gate controls their MCP exposure. See AN-T-2978.

| Parameter | Meaning |
| --- | --- |
| `project.root.prefix` | `dot` selects `.anechoic_<project_name>`; `underscore` selects `_anechoic_<project_name>`. Both use the case-folded Manifest name. |
| `project.folder_layout.active_spec_by_tier` | Active SPEC placement relative to the owner. Tier 0 uses `.`, Tier 1 uses the declared `01_` folder, and Tier 2 and above use `_{lens}/{sublenses}`. The default Tier 1 folder is `01_TIER_1_ARCHITECTURE`. |
| `project_mcp.http_port` | Required for MCP launch: loopback TCP port as an integer from 1 to 65535. No default. |
| `project_mcp.tool_blacklist` | Exact Tool names to hide and reject for this Project. |
| `project_mcp.release_workflows_enabled` | Boolean exposure gate for the Local and Public Release MCP Tools. Default `False`; direct calls are rejected when disabled. |
| `runtime.journal.storage` | `files` (default) uses append-only NDJSON; `duckdb` uses a durable Journal table in the Project DuckDB file. |
| `runtime.project_mcp.build_if_missing` | Permit a missing compatible runtime image to be built. Default `True`. |
| `runtime.project_mcp.build_timeout_seconds` | Maximum image build time. Default 600 seconds. |
| `runtime.project_mcp.startup_timeout_seconds` | Maximum startup and readiness time. Default 420 seconds. |
| `runtime.workbench.import_graph` | Import Graph options. A mapping or omission enables it; `False` disables it. |
| `runtime.workbench.import_graph.include` | Named Project-relative authored files included despite Git ignore rules. Default empty list. |
| `runtime.workbench.import_graph.python_roots` | Optional ordered Project-relative roots for Python import resolution. If omitted, infer one root from each direct child directory with a uv Project and lock. Resolve each child against its own root. Use `.` when there are no such children. |
| `runtime.workbench.import_graph.python_image_imports` | Map of Project-relative Python source files to lists of dotted Python module names. Default empty mapping. |
| `runtime.workbench.inline_result_limit_kib` | Inline query result size limit in KiB. Default 4. |
| `runtime.workbench.public_url` | Workbench page URL for saved query links when no request URL is available. |
| `runtime.workbench.result_ttl_seconds` | Retention in seconds for query results not pinned by an open View. Default 3600. |
| `runtime.workbench.schema_mode` | Header selection: `1` uses declared paths; `2` (default) uses observed paths. |
| `runtime.workbench.storage` | `disk` (default) uses the Project DuckDB file; `memory` makes other Workbench tables ephemeral. Independent of Journal storage. |

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ProjectManifest, Property

class Property3134(Property):
    name = 'Parameters'
    bearer = ProjectManifest
    field_options = {'default_factory': 'dict'}
    property.value.format = dict[str, object]
```
