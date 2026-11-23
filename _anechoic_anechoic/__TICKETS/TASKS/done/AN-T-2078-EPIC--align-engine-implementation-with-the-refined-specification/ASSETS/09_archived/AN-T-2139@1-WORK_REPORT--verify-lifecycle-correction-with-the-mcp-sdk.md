---
atom_family: TKT
atom_id: AN-T-2139
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 08:00:22 +0400
---

## Summary

Verify lifecycle correction with the MCP SDK

## Details

The installed MCP SDK accepted a corrected input dictionary within one Tool call. Form cancellation and transport cancellation both left the synthetic Action unstarted. The SDK rejected elicitation for a client that did not advertise it.

Evidence is in `.anechoic_tmp/CA-P-2791/CA-P-2934/sdk-correction-probe/`. C730 still needs the native Codex capability check and the Action cancellation boundary.
