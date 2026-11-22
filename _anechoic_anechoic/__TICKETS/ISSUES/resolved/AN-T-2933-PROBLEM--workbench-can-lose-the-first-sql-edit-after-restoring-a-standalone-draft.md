---
atom_family: TKT
atom_id: AN-T-2933
container:
  component: C46
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-21T00:56:27.380311+00:00'
---
## Summary

Workbench can lose the first SQL edit after restoring a standalone Draft

## Reproduction

1. Open Workbench with a dirty standalone Draft containing `SELECT 41 AS migrated_draft`.
2. Let Workbench migrate the Draft, then reload the page.
3. Replace the SQL with `SELECT 42 AS autosaved_draft`.

In two consecutive isolated Local Release runs, the editor retained the old SQL and sent no matching `view_update` request. This was the only failed module in the latest full run. The failure location is `workbench.e2e.spec.ts`, in “migrates one standalone draft without running it and keeps close protection after sync”.

## Acceptance

- After reload, Workbench accepts the first edit and saves the new SQL.
- Closing the View still warns about unsaved work. The Draft migration and edit never run the query.
- The browser test and full Local Release pass with their existing timeouts.

## References

AN-T-2923, AN-T-2930.
