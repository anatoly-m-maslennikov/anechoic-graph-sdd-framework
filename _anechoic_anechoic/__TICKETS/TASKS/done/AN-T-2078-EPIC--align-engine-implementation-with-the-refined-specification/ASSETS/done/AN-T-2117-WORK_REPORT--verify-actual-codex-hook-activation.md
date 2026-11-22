---
atom_family: TKT
atom_id: AN-T-2117
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 06:17:58 +0400
---

## Summary

Verify actual Codex hook activation

## Details

The installed PreToolUse hook ran on actual Codex ANECHOIC query_run calls. It blocked an omitted Project binding and a conflicting caller session with the exact hook diagnostics. A correctly bound read-only call without an explicit caller context returned 42. The installed hook file still matches the P2930 receipt. P2927 separately verified the exact session injection and receiving MCP path. Evidence is in .anechoic_tmp/CA-P-2791/CA-P-2861/actual-codex-activation.json.
