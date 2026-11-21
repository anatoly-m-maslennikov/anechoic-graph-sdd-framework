---
atom_family: TKT
atom_id: AN-T-39
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-20T20:34:46.098904+00:00"
---
## Summary

How should unconstrained Execution Result values be formatted?

## Question

Should the generic Result schema use the broad scalar Format, with producer-specific restrictions stated in its own specification?

## Details

Chosen continuation: define scalar as the direct primitive-value domain, including null, while sequences and mappings remain carrier structures. Use Execution.Result[scalar]{0+}; a structured result may have zero direct values and independently declared children, and a sequence may have several direct values. Its producing Action/Workflow specification still defines the actual result shape. This adds one reusable value Format rather than reference, list, map, a per-case function or a mandatory opaque encoding. The six specific Formats remain available for narrower properties.

Current R2235 defines Result without one universal datatype or serialization. The last 48 hours require a Format and separate direct values from nested children, but leave this generic case open. Continue P2683; track this choice with latest candidate A1302 in A1305.
