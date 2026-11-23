---
atom_family: TKT
atom_id: AN-T-1402
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 08:22:45 +0400
---
## Summary

Preserve TOML text during pure edits

# Summary

Preserve TOML text during pure edits

## Objective

After CA-P-2307 source acceptance and required affected FPF acceptance, implement the private pure TOML materializer with the approved dependency pin. Reuse existing semantic edit validation. Preserve unrelated bytes, types, comments and line endings; retain exact no-op bytes and refuse unsupported layout normalization. No file IO, new public representation or receiving authority.

## Details

Estimated own work: up to 15 minutes; split before exceeding that limit. Inherit CA-P-2256's accepted source and review gates. Root owns Plans and Git; workers own disjoint implementation and independent test files. No live configuration writes, installed activation, Core migration or Markdown/YAML dependency selection is authorized by this Task.

### Definition of Done

The bounded outcome has exact source/implementation pins, actual relevant checks and a different reviewer's acceptance. Preparation is not implementation; a Plan is not an executed FPF review. The parent and CA-P-2297 remain Active until their separate receiving/publication requirements pass.

### Acceptance — 2026-10-13

The private pure materializer and independently authored literal-byte suite passed 20 tests (7 author, 13 independent) with Python 3.14.7 and TOMLKit 0.15.1. Independent review found and verified fixes for duplicate-path binding normalization and retained array whitespace loss. Exact final source/code/test/dependency pins and known refusal boundaries are recorded in `.anechoic_anechoic/_projection/core-entity-review/stage2/tools-first/toml-materializer-acceptance.md`. No receiver, publication, live configuration write or installed runtime acceptance is claimed; P2310 and P2297 remain separate.
