---
atom_family: SPEC
atom_id: AN-S-1478
concern:
  subject: Durable information preservation
  path: Project Practice/Project information and context
  relation: is_contained_by
container:
  component: C00
tier: 2
context:
  lens: DES
  template: applicable_principle
state:
  status: "active"
  version: 13
  updated_at: "2026-11-27T13:06:14.882171+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-1486
---
**P20**

## Summary

Preserve valuable information

## Claim

### Prose Claim

Keep valuable Project information in durable, reliable storage so it remains recoverable across sessions, handoffs, context loss, and implementation changes.

## Details

The Spec, Tickets, and Project Config form the Project’s durable memory. For people, it acts as a second brain. For AI Agents, it is persisted memory.

The Spec records decisions and their reasons. Tickets record work and outcomes. Project Config records how the Project is set up.

### Examples

After a handoff, an AI Agent reads the Spec to recover a storage decision, the Ticket to see what remains open, and Project Config to check the active settings.
