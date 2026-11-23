---
atom_family: TKT
atom_id: AN-T-2778
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: '2026-11-19T00:45:31.529847+00:00'
---
## Summary

Resolve exact revision collisions from withdrawn Drafts

## Concern

How should migration preserve a withdrawn Draft when an ordinary
revision of the same Atom already has its Version?

## Details

The inventory finds eight conflicts after normalizing withdrawn Drafts
to Archived. Seven pairs have different Markdown bodies. Two pairs
include a Current revision. CA-I-9@2 is one example.

Keep the ordinary revision in its lineage. One option is to assign the
withdrawn carrier its own Archived ID and keep its original exact pin
and path in the migration map. This preserves both Versions and bodies.
CA-P-3092 holds these collisions pending a decision.