---
atom_family: TKT
atom_id: AN-T-3921
container:
  component: C43
priority: 2
context:
  template: code_spec_mismatch
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-24T22:20:19.691356+00:00'
---
## Summary

Resolve the Workbench Atom audit contract mismatch

## Claim

### Prose Claim

AN-S-1948@3 requires five SQL audit tables and audit status through Workbench HTTP and MCP. [AN-S-1948@3](../../LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/_DEVOPS/AN-S-1948-DEVOPS--deliver-query-visible-audit-tables.md)

Current C59 defines the tables in `audit_tables.py`. `native_query_projection.py` does not call the audit publisher. `native_query_runtime.py` omits `audits_pending` and `last_audit_ms` from status.

Beta and Beta Next use C71 `ingestion_issues.py` to publish `ops_ingestion_issues`. The review found no equivalent for declared or physical carrier checks, or audit completion status. AN-S-1948@3 remains active. [AN-S-3401@1](../../LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/01_TIER_1_ARCHITECTURE/AN-S-3401-DES-STANDARD--name-and-retain-database-layers-by-their-role.md)

## Work

Decide whether to restore AN-S-1948@3 or supersede it explicitly.

- To restore it, verify source commit before audit publication, exact SQL shape, non-blocking audit status, repair clearing, and unchanged carriers. Check the public interface through HTTP and MCP.
- To supersede it, check consumers of the current tables and status fields, and specify which interface takes over each audit effect.

[AN-T-3919](../TASKS/AN-T-3917-EPIC--total-refactoring/AN-T-3919-TASK--apply-the-refactoring-decisions.md)
