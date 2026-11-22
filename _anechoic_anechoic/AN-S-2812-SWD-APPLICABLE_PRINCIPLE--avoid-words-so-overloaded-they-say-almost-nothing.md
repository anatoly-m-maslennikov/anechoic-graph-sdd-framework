---
atom_family: SPEC
atom_id: AN-S-2812
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: active
  version: 4
  updated_at: '2026-11-22T11:00:54.983176+00:00'
relations:
  ADVANCES:
  - AN-S-1233
---
## Summary

Avoid words so overloaded they say almost nothing

## Claim

### Prose Claim

Do not choose a term that already means too many different things. Choose a name that tells readers what something is or how it relates to other things, without making them look up what the word means here.

## Details

These examples show how to replace overloaded terms. They illustrate the principle; they do not define mandatory ANECHOIC keywords.

| Overloaded term | What it hides | More specific names |
| --- | --- | --- |
| `scope` | Responsibility, public promises, internal design, or what a policy reaches. | `mandate` for why a component exists; `contract` for its public boundary; `affects` for which selections a policy reaches. |
| `depends_on` | Use of another component's data or capabilities, internal wiring, or policy governance. | `consumes` for reliance on data, capabilities, or guarantees; `affects` for policy governance. |
| `parent` / `child` | Folder nesting, execution order, or refinement of a decision. | `refines` when a more specific decision elaborates a broader one. |
| `type` / `kind` | Several independent classifications hidden in one tag. | Separate axes: artifact (INT/TKT/SPC), domain (USR/DOM/TEC/VER/ENB/DOC), and object (policy/decision). |
| `mode` | A flag that can silently change which rules or checks apply. | `modality` for declarative versus imperative; `tier` for authority level (Tier 0, Tier 1+, Tier 2+). |

For example, Mixer could use `consumes` to follow data or guarantees from a producer, derive `producer_for` in the reverse direction, and require a Contract across Component boundaries. It could use `refines` to follow a high-level decision into more specific binding claims and derive `refined_by` in reverse. It could use `affects` to identify which downstream selections a Policy governs.
