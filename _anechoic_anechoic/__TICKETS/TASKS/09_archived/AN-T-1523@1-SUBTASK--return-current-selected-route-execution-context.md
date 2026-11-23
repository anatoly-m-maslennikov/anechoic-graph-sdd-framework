---
atom_family: TKT
atom_id: AN-T-1523
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 1
  updated_at: 2026-10-06 18:38:40 +0000
---
## Summary

Return current selected route execution context

# Summary

Return current selected route execution context

## Objective

repair the discovery implementation so current admitted selected routes and their exact Operations definitions return truthful bounded context under existing authority.

## Details

- use the validated canonical manifest and actual exposed names; a source definition alone does not establish an executable binding.
- keep route-specific request schemas and disclose all matching bindings for a shared Action without choosing or executing one.
- preserve currentness, ambiguity, context-budget and explicit-gap behavior; do not add a new route, request protocol or permission grant.
- root owns source integration, actual MCP reload and rediscovery before freezing N13.

## Definition of Done

focused service/MCP regressions and independent review accept the bounded implementation; live route-name, Workflow-ID and shared Action-ID context requests return their current exact source bindings and truthful schemas without effects.

## Result

the discovery suite passes 16 cases and the isolated MCP suite passes 4 cases; independent review accepts the manifest-validated exposed-route catalog and schema behavior. after an explicit hot reload, all sixteen route-name contexts, Workflow CA-O-136 and shared Action CA-O-128 return complete current bindings. O128 discloses all four lifecycle routes with no arbitrarily selected input schema. no Action or Workflow was executed by these read-only checks.
