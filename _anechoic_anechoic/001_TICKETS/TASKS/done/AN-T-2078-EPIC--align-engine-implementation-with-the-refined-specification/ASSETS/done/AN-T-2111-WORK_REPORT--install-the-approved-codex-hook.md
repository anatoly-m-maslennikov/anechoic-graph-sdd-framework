---
atom_family: TKT
atom_id: AN-T-2111
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 03:53:43 +0400
---

## Summary

Install the approved Codex hook

## Details

After the Operator approved the exact host change, installed the reviewed ANECHOIC PreToolUse command and status text in ~/.codex/hooks.json. Matcher, five-second timeout, unrelated hooks and trust state are unchanged. Exact old/new hashes, a preimage and installation receipt are in .anechoic_tmp/CA-P-2791/CA-P-2861. The earlier automatic-review rejection is superseded by this explicit approval and successful installation.

The receiver and actual launcher-subprocess/live-MCP context checks passed in P2927. Host installation is now proven; actual Codex host invocation and its normal exact-definition trust review are not inferred from a file write. P2861 stays Active for that remaining activation evidence; Workflow Run/history remains deferred.
