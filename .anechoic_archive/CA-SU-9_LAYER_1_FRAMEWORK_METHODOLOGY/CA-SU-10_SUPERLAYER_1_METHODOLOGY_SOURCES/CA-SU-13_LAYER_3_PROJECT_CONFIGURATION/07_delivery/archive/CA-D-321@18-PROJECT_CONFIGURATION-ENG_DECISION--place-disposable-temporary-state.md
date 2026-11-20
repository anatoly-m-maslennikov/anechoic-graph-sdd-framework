---
subjects:
  governs: Subject/ANECHOIC/Carrier/Directory
  depends_on: []
version: 18
updated_at: 2026-10-27 19:59:23 +0400
relations: {}
atom_id: CA-D-321@18
content_role: Delivery
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
status: Archived
author: Anatoly Maslennikov
tier: 3
type: Eng Decision
---
# Summary

Place Disposable Temporary State

## Scope

disposable temporary state in a ANECHOIC Project.

## Claim

the ANECHOIC Project **must** place disposable scratch, staging, test cache, atomic-write intermediate, build intermediate, **and** interrupted-cleanup Carriers under `.anechoic_tmp/`.

## Details

deleting `.anechoic_tmp/` **must not** delete governed authority, Project Journal history, installed Framework Engine releases, runtime logs, sessions, databases, service state, **or** resumable state.
