---
subjects:
  governs: "relation-model"
  depends_on:
    - "atom-boundary"
version: 14
updated_at: "2026-09-10 05:08:55 +0400"
relations:
  child_of:
    - ANECHOIC-META-REQU-706
---
# Derive inverse structural ownership

ANECHOIC **must** derive the inverse `structural_children` view from stored `structural_parent` relations **and** **must not** persist that inverse separately.
