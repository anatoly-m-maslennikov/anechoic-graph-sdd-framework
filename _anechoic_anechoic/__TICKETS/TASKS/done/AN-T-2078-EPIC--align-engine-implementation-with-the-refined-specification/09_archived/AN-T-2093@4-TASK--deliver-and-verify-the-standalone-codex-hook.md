---
atom_family: TKT
atom_id: AN-T-2093
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: archived
  version: 4
  updated_at: 2026-11-11 03:08:22 +0400
---

## Summary

Deliver and verify the standalone Codex hook

## Objective

Implement and test the adopted generic hook delivery independently of plugins. Verify actual host activation and end-to-end context only after the receiving backend supports the field. Preserve unrelated host configuration.

## Subtasks

- [ ] Review the next scoped inputs and fix gaps. (ETA: up to 15 min.)
- [ ] Complete one scoped batch; split before 20 minutes.
- [ ] Review the result and write a small Work Report. (ETA: up to 15 min.)

## Definition of Done

The scoped deliverable is reviewed and its actual checks and remaining holds are recorded. Tasks do not replace RMEDO.


## Verified context; host installation pending

P2927 records passing launcher-subprocess and live-MCP context checks. The exact host installation candidate is prepared and reviewed. Automatic approval review rejected the ~/.codex/hooks.json write because persistent host PreToolUse configuration requires explicit approval of the concrete change. The host file and trust state remain unchanged. Installation and actual Codex host activation remain unverified; no Workflow Run/history work is resumed.
