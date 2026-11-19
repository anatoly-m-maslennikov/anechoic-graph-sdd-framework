---
subjects:
  governs: ANECHOIC/Temporary State Carrier Root
  depends_on: []
version: 11
updated_at: 2026-10-02 19:05:39 +0400
relations: {}
atom_id: CA-D-321@11
content_role: Delivery
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
local_tier: Standard
status: Archived
author: Anatoly Maslennikov
global_tier: 11
---
# Summary

Place Disposable Temporary State

## Scope

disposable temporary state in a ANECHOIC Project.

## Claim

the ANECHOIC Project **must** place disposable scratch, staging, test cache, atomic-write intermediate, build intermediate, **and** interrupted-cleanup Carriers under `.anechoic_tmp/`.

## Details

deleting `.anechoic_tmp/` **must not** delete governed authority, Project Journal history, installed Framework Engine releases, runtime logs, sessions, databases, service state, **or** resumable state.
