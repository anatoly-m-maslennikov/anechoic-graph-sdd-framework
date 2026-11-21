---
atom_family: PROJECT_CONFIG
atom_id: AN-P-29
structure:
  container:
    component: C27
context:
  template: action
state:
  status: active
  version: 25
  updated_at: '2026-11-21T21:51:04.697298+00:00'
---

# Summary

Promote candidate and retire exact prior image

## Action

After C19 unit, end-to-end and canary checks pass for the candidate, install the verified Framework and runtime package and its Skill. Start the exact candidate for Project MCP, verify readiness, and apply the production tag. Preserve protected settings, Project state and authoring sources.

Use inspected Project ownership and immutable identity to select obsolete containers and images for cleanup. Preserve protected, foreign, unowned, uncertain and container-referenced resources. Do not force removal or prune globally. Report failures and pending cleanup; do not replay an uncertain effect. This Action does not invoke Journal.
