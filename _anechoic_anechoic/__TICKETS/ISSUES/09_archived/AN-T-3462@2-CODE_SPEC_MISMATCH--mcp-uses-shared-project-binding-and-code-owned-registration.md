---
atom_family: TKT
atom_id: AN-T-3462
container:
  component: C21
priority: 2
context:
  template: code_spec_mismatch
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 22:40:16 +0400
---

## Summary

MCP uses shared Project binding and code-owned registration

## Claim

### Prose Claim

The inspected MCP code validates an explicit Project binding, registers code-owned native Tools and shares Workbench handlers. Hot reload is opt-in. Existing release and entrypoint code already wires catalog generation and the shared HTTP server.

**Code locations and review notes**

[shared_gateway.py](../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/shared_gateway.py) validates the outer Project selection before dispatch.

[shared_project_catalog.py](../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/shared_project_catalog.py) discovers each selected Project’s initialized native Tool frontier and combines it with Workbench tools.

[direct_gateway.py](../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/direct_gateway.py) serves tools in process while reload is disabled.

[hot_reload.py](../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/hot_reload.py) requires ANECHOIC_HOT_RELOAD=1 to enable reload.

[generate_tools_catalog.py](../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/generate_tools_catalog.py) pages tools/list without invoking a Tool.

[entrypoint.py](../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKFLOW_ORCHESTRATOR/docker/entrypoint.py) already constructs the shared HTTP command. [local_release.py](../../../../../../LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/RELEASE_VERSION/local_release.py) already calls catalog generation after delivery/readiness checks. Absence of a caller inside the MCP package is not missing integration.

Inspection on 9 November 2026, current working tree. This review inspected code only; it did not execute MCP, release or readiness checks.
