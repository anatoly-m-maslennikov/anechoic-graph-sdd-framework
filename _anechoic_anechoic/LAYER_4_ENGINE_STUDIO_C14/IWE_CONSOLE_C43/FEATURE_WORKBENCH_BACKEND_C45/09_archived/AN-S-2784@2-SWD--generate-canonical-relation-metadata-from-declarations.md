---
atom_family: SPEC
atom_id: AN-S-2784
container:
  component: C45
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Generate canonical relation metadata from declarations

## Claim

### Prose Claim

Generate one rebuildable relation registry from Current Requirement relation Declarations. Use that registry for Workbench relation-name resolution and direct/derived materialization.

- Include canonical Relation names, explicit inverse aliases, literal unqualified inverse bindings, and their source Atom IDs and versions.
- Accept the applicable Declaration Forms, including Relation Declaration. An inverse alias introduced by a canonical Declaration needs no separate Relation Declaration.
- Normalize an explicit inverse alias by swapping its endpoints once. For an unambiguous legacy named inverse, preserve the same fact through its declared counterpart. Do not edit the source carrier or invent a binding.
- Derive container facts from the effective Header.Container value, including its Header.Context.Container carrier layout. Resolve the Project root as a Scope Unit using uppercase(Project prefix) followed by -SU-00. Build inverse views from each canonical direct fact once. A changed source refreshes only the affected direct and inverse rows and hashes.
- Preserve exact model names. Existing ambiguity warnings and omission rules still apply; do not choose a winner or repair source declarations silently.
- Keep arbitrary prose and general CFEL evaluation out of this compiler. Do not evaluate qualified Model derivation rules or turn them into runtime facts. Unsupported or ambiguous literal metadata is diagnosed and omitted, not guessed.

Regenerate the registry on every supported image rebuild, including local release. Use the same compiler for the existing refresh of relevant Current Declaration changes, so the runtime does not keep stale relation metadata. The asset is derived data, not another source of truth or a separately maintained list.

## Semantics

Canonicalization changes the query representation of an unambiguous fact, not its meaning or its authored source. The runtime graph still uses its admitted Atom and Scope Unit sources; relation metadata does not add new graph vertex domains.
