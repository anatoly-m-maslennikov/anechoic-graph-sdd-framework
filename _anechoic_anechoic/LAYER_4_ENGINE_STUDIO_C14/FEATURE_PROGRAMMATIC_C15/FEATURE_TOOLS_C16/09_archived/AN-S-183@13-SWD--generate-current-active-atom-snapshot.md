---
atom_family: SPEC
atom_id: AN-S-183
container:
  component: C16
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 13
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Generate current active Atom snapshot

# Generate current active Atom snapshot

generate the current active Atom snapshot through this procedure:

1. resolve the complete current project structural topology **and** canonical Type registry, enumerate Atom carriers through the canonical address resolver, **and** derive active state from **every** Type's registered lifecycle placement rather than from frontmatter, filename text, **or** filesystem timestamps.
2. assign **every** active Atom **=1** canonical Type, one structural level, **and** one structural unit. fail closed on an unknown, ambiguous, malformed, duplicated, **or** topologically unregistered carrier instead of omitting **or** double-counting it.
3. compute one grand total **and** three complete independent rollups: active Atoms by canonical Type, by structural level, **and** by structural unit. emit **every** registered dimension member, including members with a zero count, **and** require **every** rollup **to** sum **to** the grand total.
4. bind the output **to** `<project-control-root>/biz_atoms_current_snapshot.md` **and** emit the declared source frontier **and** as-of timestamp followed by `Total`, `By Type`, `By structural level`, **and** `By structural unit` sections with stably ordered rows **and** integer `active_atom_count` values.
5. bind the exact carrier frontier, lifecycle **and** topology configuration, generator version, source digests, **and** `updated_at`; replace the Projection atomically **and** record the completed rebuild through the Work Journal.
6. regenerate from the same frontier **and** configuration **and** require byte-stable semantic output **before** reporting the snapshot current.
