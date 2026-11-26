---
atom_family: SPEC
atom_id: AN-S-2607
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 11
  updated_at: 2026-11-08 15:22:04 +0400
---

## Summary

Declare Atom

## Claim

### Prose Claim

Each Atom instance has exactly one outgoing HAS_ACTIVE_SUBJECT link. Its target is the declared entity or instance resolved from Header.Topics.Main Subject. An unresolved Subject is a diagnostic.

For each Atom instance, the outgoing GOVERNS Relation has cardinality 0..1 and targets only the canonical Subject the Atom governs through its applicable content. These are separate named outgoing permissions and do not grant an inverse or another Relation. The target-omitted bounds count each Atom’s outgoing links within each Relation Declaration’s admissible endpoint domain; they do not create links.

Each Atom instance's outgoing IS_CONTAINED_BY Relation targets the Atom instance or Scope Unit instance selected by its Header.Container.

### Formal Claim

```CFEL
# model
Atom;

Atom.*[string,in(Header,Content)]{::2};

Atom ((NARROWER_THAN)) Continuant;

# instances
Atom//$atom {::1}((IS_CONTAINED_BY));

Atom//$atom {::1}((HAS_ACTIVE_SUBJECT));

Atom//$atom {::0..1}((GOVERNS));

Atom//$atom {::0+}((CONTRIBUTES_TO));

Atom//$atom {::0+}((REPLACEMENT_FOR));

UNIQUE(Atom//$atom, (.Header.ID, .Header.Version));
```

## Semantics

An Atom is the smallest independently governed Object.
