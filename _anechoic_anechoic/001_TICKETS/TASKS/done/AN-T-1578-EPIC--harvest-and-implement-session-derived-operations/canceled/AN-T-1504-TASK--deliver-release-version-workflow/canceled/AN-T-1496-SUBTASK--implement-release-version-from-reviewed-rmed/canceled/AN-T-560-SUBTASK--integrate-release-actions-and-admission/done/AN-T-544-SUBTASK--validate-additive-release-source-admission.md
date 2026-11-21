---
atom_family: TKT
atom_id: AN-T-544
container:
  atom: AN-T-560
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Validate additive Release source admission

## Objective

Within <=15 minutes, implement the strict Release source-admission validator.

## Details

Own only new MCP/release_source_admission.py and its focused tests. Read accepted CA-D-572@3 and derive its exact closed pin record without creating a second authority. Validate current source bytes and identity, the accepted frontier, ten ordered Step/Action occurrences and complete RMED frontier. Preserve the current fifteen-route manifest when Release is absent. Reject absent, duplicate, stale, incomplete, malformed, reordered or caller-forged Release admission before shared support; D527 request definition_manifest remains its existing two fields.

Golden tests first. No actual manifest changes, route registration, native release dispatch, runtime installation, image work, source/Plan/Git edits or denied-operation workaround. Use disposable fixtures in the existing development worker only. Preserve every other Agent's work. Choose the best authorized option and record uncertainty rather than wait for Operator input.

## Definition of Done

The focused compatibility and refusal cases pass, and exact code/test hashes are retained. This is parser/validator proof only, not registration or release execution.

## Result

release_source_admission.py `e2bc6ba7c63c139d8d7b3b8c9eca85e8d3120cce3d93ea20c8ea55637e4946a8` and tests `05106a2c9a6e8029d1aa4c8e91634694d5eaeadde54fb9ebe079d35383444ffa`: eight focused tests pass, including thirty-seven separate live-pin revocations. The read-only helper derives the exact six-field record from D572@3, preserving ordered occurrences and current fifteen-route compatibility without reading Release authority when absent. Raw duplicate-key rejection and whole-manifest integration remain P1692; no actual manifest registration, dispatch or image completion occurred.
