---
atom_family: SPEC
atom_id: AN-S-364
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DES
state:
  status: active
  version: 34
  updated_at: 2026-11-03 23:17:14 +0400
---
## Summary

Journal Projection Rebuild Events

## Claim

### Prose Claim


Business Projection Rebuilds and their Work Journal Actions and terminal Events. Technical read-only queries and maintenance of rebuildable query indexes are runtime activities outside this Rule.


**every** business Projection Rebuild **must** have **`=1`** Work Journal Action whose terminal Event records the rebuild outcome.

## Details

technical read-only queries and maintenance of rebuildable query indexes report normal output through runtime stdout and failures through runtime stderr. these activities require no Work Journal Action or terminal Event under this Rule.

acceptance of that Event into the Journal does **not**, by itself, make the Projection current. currentness remains subject **to** the Projection's applicable source **and** validation requirements; the accepted Event preserves the observed outcome **without** replacing those requirements.
