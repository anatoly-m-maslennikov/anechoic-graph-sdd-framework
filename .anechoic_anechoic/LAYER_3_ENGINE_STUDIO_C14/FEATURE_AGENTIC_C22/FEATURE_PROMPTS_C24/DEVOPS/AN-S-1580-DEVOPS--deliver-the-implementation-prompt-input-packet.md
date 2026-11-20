---
identity:
  atom_id: AN-S-1580
context:
  container:
    component: C24
  tier: 3
  lens: DevOps
state:
  status: active
  version: 16
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Deliver the implementation prompt input packet

## Claim

### Prose Claim

the packet **must** carry current Workflow/Step/Action pins, P/DoD and owned paths, R/D targets, the verified active-M file, E checks, authority, permissions, confidence, retry accounting, assigned context, retained evidence, and Step-specific input.

## Details

### Scope

the invocation packet passed to one current Implementation Workflow prompt.

Preparation may begin from a bounded request plus admitted authority, but it must produce or verify the M file before delegated work. A missing field produces the Step's blocked result.

### Selected Project and handoff binding

Every invocation packet additionally carries exactly one `selected_project`
binding before a prompt can verify its governed sources or call an Agent:

| Field | Required value | Boundary |
| --- | --- | --- |
| `selected_project.kind` | `selected_project` | identifies the Project frozen by the selected Workflow; it is not an absolute host path, current directory, code-root copy, or mount grant |
| `selected_project.source_root` | `.anechoic_anechoic` | the only authority root for prompt-source resolution |
| `selected_project.source_references` | the exact current `source_bindings` rows, each with Atom ID, Version, project-relative `path`, and SHA-256 | every path is nonempty, relative, has no `..` segment, begins under `source_root`, and resolves only beneath the frozen selected Project |
| `requirements`, `methods`, `evaluations`, `delivery` | complete applicable direct source rows: `atom_id`, `version`, Project-relative `path`, `sha256`, and full `content` | independently verify the authorized initial selection, its declared universe and applicable governing parents against current Project authority; preserve R/D implementation targets separately from governing context |
| `method_projection` | one verified complete active-M projection file with its binding | compile or verify it before delegated work, retain the same file binding downstream, and block if missing, stale, conflicting, unauthorized, or incomplete; it is derived guidance and does not replace direct source rows or establish applicability |
| `workspace` | the existing absolute, non-symlink disposable workspace supplied to the Agent | no source binding infers or substitutes this path |
| `permissions.implementation_workspace` | the existing exact `{kind: disposable_workspace, path: workspace, allow_write: true}` capability | it must match `workspace`; this Delivery adds no write grant |

The selected Workflow runtime resolves `selected_project` only from its frozen
Project context. Absent, stale, duplicate, mismatched, escaping, or
partially-readable source references, incomplete direct RMED inputs, or a
missing/mismatched workspace capability blocks before Agent launch or effects.
This binding exposes neither credentials nor an Agent endpoint and does not
authorize a hidden mount, arbitrary writer, or live-model execution. An
explicit executable mock remains `mock-not-live-llm` evidence only.

An Integrated prompt response carries the current Step's prompt, bound inputs,
output contract, and opaque continuation identity. Publishing it leaves the Step
pending. The controlling session may perform or delegate the admitted work and
submit its actual result through the same Workflow interface. Only the executor
validates that bound submission and chooses the next Step; a prompt alone is not
completion. Retain the persistent Plan, partial effects, candidate-specific
review/check evidence and finite retry state across requests. The implementation
instructions use CA-R-2117 and CA-E-653 for narrowest-branch RMED
ownership comments; citations alone do not prove conformance.
