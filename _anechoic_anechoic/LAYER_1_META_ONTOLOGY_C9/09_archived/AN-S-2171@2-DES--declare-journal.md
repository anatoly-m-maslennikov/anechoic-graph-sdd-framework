---
atom_family: SPEC
atom_id: AN-S-2171
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Declare Journal

## Claim

### Formal Claim

```CFEL
# model
Journal {::0}((IS_PROPERTY_OF));

Journal >| (Container == yes);

Journal ((NARROWER_THAN)) Continuant;

# instances
Journal//$journal{::1};

Journal//$journal_2 {::0+}((CONTAINS)) Event Record//$event_record;
```

## Semantics

A Journal preserves accepted event history.
