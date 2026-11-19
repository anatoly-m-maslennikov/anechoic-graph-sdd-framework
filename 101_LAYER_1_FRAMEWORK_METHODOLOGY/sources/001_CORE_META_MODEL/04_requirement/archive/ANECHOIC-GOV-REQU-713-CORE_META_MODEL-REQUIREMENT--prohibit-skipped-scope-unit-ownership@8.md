---
atom_id: ANECHOIC-GOV-REQU-713
subjects:
  governs:
    continuant:
      - scope-topology
  depends_on:
    continuant:
      - authority
cce_version: cce_1
cce_form: prohibition
version: 8
updated_at: 2026-09-06 01:45:12 +0400
relations:
  child_of:
    - ANECHOIC-META-REQU-706
---
# Prohibit skipped Scope Unit ownership

A Scope Unit **must not** own a descendant Scope Unit through a stored structural-parent relation **when** another active Scope Unit lies between them.
