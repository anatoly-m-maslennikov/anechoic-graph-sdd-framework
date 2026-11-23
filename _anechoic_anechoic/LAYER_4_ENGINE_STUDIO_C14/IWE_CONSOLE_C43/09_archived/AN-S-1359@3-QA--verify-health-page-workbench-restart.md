---
atom_family: SPEC
atom_id: AN-S-1359
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Verify health-page Workbench restart

## Claim

### Prose Claim

The health page's Restart Workbench button invokes the same native MCP operation and shows the actual success or failure. The page remains available when Workbench fails. Opening the page is read-only; no restart occurs before the explicit POST action.

## Details

| Scenario | Expected outcome |
| --- | --- |
| GET HTML health page and machine JSON readiness | Restart button is present in HTML; no service operation runs. Existing JSON readiness is unchanged. |
| Submit the fixed restart form for the Project | Health HTML shows the actual ready result; fresh queries work; old result IDs are unknown and saved items remain loadable. |
| Restart with a still-invalid Current Scope Unit Declaration | Health page shows failure; MCP and the health page remain usable. |
| Shared host action | It requires an explicit Project folder and restarts only the selected Project. |
| Missing, repeated or unknown form fields | Rejected before any restart effect. |
| Tool is blacklisted | The health action reports the blocked operation and does not bypass the native MCP blacklist. |
