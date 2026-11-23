---
atom_family: SPEC
atom_id: AN-S-1076
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Bind admitted Scope Unit Graph sources in canonical order

# Bind admitted Scope Unit Graph sources in canonical order

## Test case

provide a fixed valid Project Structure Artifact with multiple accepted Scope Unit declarations **and** a fixed set of admitted Settings, Atom, directory-observation **and** Journal inputs. discover the input Carriers **in** different filesystem orders **without** changing their identities, content **or** declared structural **and** navigational order.

## Acceptance criteria

- **every** run emits the same Project Scope Unit Graph **and** Sources bindings **in** canonical source-identity order.
- Project Structure remains the sole authority for accepted declarations **and** bindings under CA-R-1070; an Atom-owned contribution map cannot redefine them.
- Project Settings **and** Framework Instance Settings retain their own selected-value authority; observations **and** generated views do **not** select Settings.
- filesystem enumeration order does **not** rewrite declared structural order **or** navigational order. **all** source Carriers remain unchanged.
