---
identity:
  atom_id: AN-S-1076
context:
  container:
    component: C37
  tier: 3
  lens: QA
state:
  status: active
  version: 28
  updated_at: 2026-11-02 19:44:26 +0400
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
