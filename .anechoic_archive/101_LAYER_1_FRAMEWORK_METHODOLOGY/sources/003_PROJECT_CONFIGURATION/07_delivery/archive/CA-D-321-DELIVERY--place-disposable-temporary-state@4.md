---
atom_id: CA-D-321
cce_version: cce_1
cce_form: placement
subjects:
  governs:
    continuant:
      - ANECHOIC/Temporary State Carrier Root
version: 4
updated_at: "2026-09-15 03:15:32 +0400"
relations: {}
---
# Place Disposable Temporary State

the ANECHOIC Project **must** place disposable scratch, staging, test cache,
atomic-write intermediate, build intermediate, **and** interrupted-cleanup
Carriers under `.anechoic_tmp/`.

deleting `.anechoic_tmp/` **must not** delete governed authority, Project
Journal history, installed Framework Engine releases, runtime logs, sessions,
databases, service state, **or** resumable state.
