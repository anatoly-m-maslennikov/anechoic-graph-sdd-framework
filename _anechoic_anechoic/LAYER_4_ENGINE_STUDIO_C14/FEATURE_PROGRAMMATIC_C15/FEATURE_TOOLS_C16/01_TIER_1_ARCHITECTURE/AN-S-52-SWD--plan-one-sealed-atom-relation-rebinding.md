---
atom_family: SPEC
atom_id: AN-S-52
concern:
  subject: "Relations"
  path: "Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header"
  relation: "is_property_of"
container:
  component: C16
tier: 1
context:
  lens: SWD
state:
  status: active
  version: 21
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Plan one sealed Atom relation rebinding

# Plan one sealed Atom relation rebinding

For one sealed request, resolve the exact active source carrier, verify its digest **and** version, validate **only** the explicitly named direct relation rewrites **or** removals, **and** pass the observed bytes **and** sealed request **to** a pure planner. The planner preserves filename, body, **and** undeclared frontmatter, advances version once, sets the supplied timestamp, derives the result digest, **and** returns one `UPDATE` receipt.

Dry run is mutation-free. `--apply` is accepted **only** through authorized project-local MCP delegation with the sealed Initiative action envelope. The authorized effect atomically replaces **only** the source carrier **and** obtains durable `COMMIT_TRIGGER` intake acknowledgement **before** MCP reports success. It never infers a relation meaning, target mapping, backup, Journal event, staging change, **or** Git action.
