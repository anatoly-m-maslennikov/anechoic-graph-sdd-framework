---
atom_family: TKT
atom_id: AN-T-2487
container:
  atom: AN-T-2220
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: '2026-11-13T19:43:02.730933+00:00'
---
## Summary

Record spec traces for the Workbench pilot

## Details

Six narrower Claims are Active and verified in the checkout's trace projection. CA-D-723 maps to public row construction, CA-D-724 to result delivery, CA-D-725 to startup retention settings, CA-D-726 to the Archive dialog, CA-M-1027 to batch refresh publication, and CA-E-834 to MCP recovery after invalid SQL.

CA-M-464@19 includes explicitly loaded Archives. CA-M-465@31 records both watcher roots. CA-C-741, CA-C-742 and CA-C-743 track sync failure display, full-inventory work during ordinary refresh, and the frontend test file over its line limit.

CA-D-673@20 and CA-D-674@28 contain route corrections. Their Current predecessors are two versions behind and the intervening Drafts are deferred SQL-write work. CA-D-722 stays Draft alongside the route correction. CA-M-500@14 and CA-M-509@9 stay Draft during the compiler transition. CA-M-501 governs authored queries. CA-E-819 is covered by the MCP test outside the pilot. Shared parent Claims remain as the contracts for their separate owners.

The focused checks passed. The deployed MCP does not list the trace tables. The local watcher E2E could not complete with the macOS native observer. CA-E-830 remains Draft under the pilot's verification task.
