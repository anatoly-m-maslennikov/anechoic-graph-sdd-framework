---
atom_family: SPEC
atom_id: AN-S-379
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 27
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Preserve source scope in derived views

## Claim

### Prose Claim


Derived views of declared source scopes.


a derived view preserves **every** source's declared scope **and** **must not** inflate truth, completeness, evaluation, **or** priority by aggregating sources.
