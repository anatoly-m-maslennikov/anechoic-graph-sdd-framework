---
atom_family: SPEC
atom_id: AN-S-2607
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-04 11:00:07 +0400
---
## Summary

Declare Atom

## Claim

### Formal Claim

```CFEL
# model
Atom;

Atom.*[string,in(Header,Content)]{::2};

Atom ((NARROWER_THAN)) Continuant;

# instances
Atom//$atom {::0..1}((HAS_ACTIVE_SUBJECT));

Atom//$atom {::0..1}((GOVERNS));

UNIQUE(Atom//$atom, (.Header.ID, .Header.Version));
```

### Prose Claim

For each Atom instance, the outgoing HAS_ACTIVE_SUBJECT Relation has cardinality 0..1 and targets only the declared entity or instance resolved from its active Subject field. When the applicable Current-status rule requires that field, its resolved target supplies the one link; an unresolved field remains a diagnostic.

For each Atom instance, the outgoing GOVERNS Relation has cardinality 0..1 and targets only the canonical Subject the Atom governs through its applicable content. These are separate named outgoing permissions and do not grant an inverse or another Relation. The target-omitted bounds count each Atom’s outgoing links within each Relation Declaration’s admissible endpoint domain; they do not create links.

An Atom instance records its immediate container once in Header.Container. It does not represent that same fact again as an instance-level IS_CONTAINED_BY Relation or under Header.Relations. Formal MODEL Relation declarations remain governed by their own declarations.

## Semantics

An Atom is the smallest independently governed Object.
