---
artifact_subtype: qa_case
subject_scopes:
  - evaluation
priority: high
version: 1
updated_at: 2026-08-17 19:36:01
llm_session_ids:
  - codex:019f591f-04f6-70f2-8de7-828b7cccc69d
relations:
  - type: replacement_of
    targets:
      - ANECHOIC-GOV-EVAL-037--numbered-layer-directories-test-case
      - ANECHOIC-GOV-EVAL-038--forward-only-layer-authority-test-case
  - type: check_of
    targets:
      - ANECHOIC-GOV-METH-044--numbered-control-plane-layout
      - ANECHOIC-META-REQU-201--canonical-layer-definitions
      - ANECHOIC-META-REQU-203--acyclic-layer-dependencies
---

# Test Case — Validate the complete numbered hierarchy

## Controlled checks

1. Assert the installed methodology has `00_project` then `01_meta` through
   `06_ops`.
2. Assert applied authority has `100_project`, `100_LAYER_1_META` through
   `600_LAYER_6_OPS`, and `150_versions`.
3. Assert reusable source has `10_project`, `11_layer_meta` through
   `16_layer_ops`, and `50_versions`.
4. Assert every methodology descendant has one sibling-unique zero-padded
   numeric prefix.
5. Reject any declared layer dependency from a later layer to an earlier layer.

## Expected disposition

The exact three hierarchies pass, missing or misordered layers fail, and every
backward dependency is reported with both endpoints.
