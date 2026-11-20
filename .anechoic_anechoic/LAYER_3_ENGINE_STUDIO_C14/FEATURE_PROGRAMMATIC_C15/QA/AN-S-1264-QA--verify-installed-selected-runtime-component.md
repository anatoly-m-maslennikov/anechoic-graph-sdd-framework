---
identity:
  atom_id: AN-S-1264
context:
  container:
    component: C15
  tier: 4
  lens: QA
state:
  status: active
  version: 27
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify installed selected-runtime component

## Claim



### Prose Claim
#### Claim checked

one delivered installable PROGRAMMATIC component runs under the runtime **and**
dependency selections owned by accepted Methods from the carrier placed **and**
encoded by its Delivery.

#### Applicable conditions

apply **only** **when** a lower-Scope Delivery declares the component installable.
this case does **not** establish a platform-support claim.

#### Test case

install one delivered component from its Delivery-owned carrier, invoke its
declared entry boundary, **and** compare the observed runtime **and** dependencies with
their Method-owned selections **and** materializations.

#### Acceptance criteria

pass **only** **when** the installed carrier reaches its declared entry boundary,
the observed runtime **and** dependencies match their applicable Method-owned
selections **and** materializations, **and** no undeclared runtime **or** dependency is
required. the carrier **must not** claim selection authority.

#### Failure disposition

reject the installation claim **and** return the component **to** its Delivery owner.

#### Sources

- [CA-M-415 — Implement PROGRAMMATIC components in Python](../05_method/CA-M-415-PROGRAMMATIC-ENG_POLICY--implement-programmatic-components-in-python.md)
