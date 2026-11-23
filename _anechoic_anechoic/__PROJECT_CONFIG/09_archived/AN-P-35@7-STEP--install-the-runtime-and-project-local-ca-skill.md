---
atom_family: PROJECT_CONFIG
atom_id: AN-P-35
structure:
  container:
    component: C00
context:
  template: step
state:
  status: archived
  version: 7
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Install the runtime and project-local ca Skill

# Summary

Install the runtime and project-local ca Skill

## Step

This Step invokes CA-O-169 once with phase `install` to copy compiled `101_FRAMEWORK_METHODOLOGY/`, preserve protected configuration and Project state, install Engine `.install` into the Project runtime package, and install the `ca` payload.

## Details

Only this Step clears replaceable installed Framework members, copies the product as-is, installs `ca`, and restarts or reuses Project MCP for Docker/MCP smoke. It preserves settings and Project state, does not alter authoring, push, create a PR, or retry an uncertain effect.

Reuse canonical image preparation only after the Workflow's full suite is green. This occurrence also owns CA-O-169's post-smoke selected-Project retention: keep the exact admitted current-Version candidate, remove only proven owned unused noncandidate images, preserve all container references and other Projects' images, and report pending cleanup. Same fingerprint alone does not preserve an older rebuild. No additional retirement Step is inserted into CA-O-164.
