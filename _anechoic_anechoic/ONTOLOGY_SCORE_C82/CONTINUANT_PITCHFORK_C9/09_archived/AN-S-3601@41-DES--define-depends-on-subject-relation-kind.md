---
atom_family: SPEC
atom_id: AN-S-3601
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 41
  updated_at: 2026-11-04 03:22:03 +0400
---
## Summary

Define DEPENDS_ON Subject Relation Kind

## Claim

### Prose Claim

#### Applicability
the DEPENDS_ON Subject Relation Kind of an Atom.

DEPENDS_ON **means** the direct Subject Relation Kind from an Atom **to** a canonical Subject entity or instance mentioned **in** its applicable role-specific content or other registered content, other than its GOVERNS target. this reference does **not** make the Atom's content—or every Governing Configuration fact—authoritative about that Subject entity or instance; formal authority depends on the applicable registered content form and role. a formal Claim may be carried in Markdown, structured YAML, or Governing Configuration, but Governing Configuration facts are not automatically Atom Claims.

The Target is a canonical Subject referenced by the Atom, other than its governing target.
Forward `Host ((DEPENDS_ON)) Target` and reverse `Target <((DEPENDS_ON)) Host` are views of the same Relation fact.
DEPENDS_ON relates Atom to referenced Subject entity or instance.

#### Details
mentions **in** Summary, Scope, Claim, Details, other registered body sections, tables, **and** examples count, whether the logical Claim is carried in Markdown, structured YAML, or Governing Configuration. this Relation does **not** establish Workflow control flow **or** execution order; Plan start prerequisites remain separately governed by `BLOCKS` under CA-R-1580-CORE_META_MODEL-DEFINITION--define-plan-blocking.
### Formal Claim

```CFEL
# model
Relation//DEPENDS_ON ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom//$atom ((DEPENDS_ON)) $referenced_subject
```

