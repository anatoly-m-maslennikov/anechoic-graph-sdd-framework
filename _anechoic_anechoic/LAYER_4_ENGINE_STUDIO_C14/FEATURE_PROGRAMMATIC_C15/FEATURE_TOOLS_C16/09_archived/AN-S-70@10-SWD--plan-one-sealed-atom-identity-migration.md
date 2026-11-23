---
atom_family: SPEC
atom_id: AN-S-70
container:
  component: C16
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Plan one sealed Atom identity migration

# Plan one sealed Atom identity migration

For one sealed migration request, resolve the exact active source **and** destination carriers, collect filesystem facts **and** canonical-ID collision candidates, **and** pass **only** those facts **to** a pure planner. The planner validates **every** sealed precondition, applies **only** the named frontmatter **and** relation changes **in** memory, derives the exact result digest, **and** returns one `UPDATE` **or** `MOVE+UPDATE` receipt.

Dry run is mutation-free. `--apply` is accepted **only** through authorized project-local MCP delegation with the sealed Initiative action envelope. The authorized effect atomically writes the planned destination, removes the source **only** **when** paths differ, **and** obtains durable `COMMIT_TRIGGER` intake acknowledgement **before** MCP reports success. It never infers identity mappings, relation meanings, timestamps, Journal events, **or** Git actions beyond the sealed request.
