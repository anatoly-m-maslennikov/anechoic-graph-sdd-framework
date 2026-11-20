---
atom_family: TKT
atom_id: AN-T-2139
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 2
  updated_at: 2026-11-11 08:08:52 +0400
---

## Summary

Verify lifecycle correction with the MCP SDK

## Details

The installed MCP SDK accepted a corrected input dictionary within one Tool call. Form cancellation and transport cancellation both left the synthetic Action unstarted. The SDK rejected elicitation for a client that did not advertise it.

Evidence is in `.anechoic_tmp/CA-P-2791/CA-P-2934/sdk-correction-probe/`. The installed Codex App Server bindings expose a standard form request and accept, decline and cancel replies. The generated bindings are in `.anechoic_tmp/CA-P-2791/CA-P-2934/codex-app-protocol/`. C730 still needs live client negotiation and proof of the Action cancellation boundary.
