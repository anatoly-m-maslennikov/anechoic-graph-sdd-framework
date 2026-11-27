---
atom_family: SPEC
atom_id: AN-S-1560
container:
  component: C23
tier: 4
context:
  lens: DevOps
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T10:14:11.104962+00:00"
---
## Summary
Package Skills as bootstrap and response-handler instructions

## Claim

### Prose Claim

a delivered Skill package **must** carry its discovery metadata **and** very thin bootstrap/response-handler body separately from task-specific Action instructions supplied through MCP.

- place canonical Skill packages at the SKILLS Delivery binding. identify the entry purpose **and** **any** registered direct-route reference **in** the host-admitted metadata representation.
- carry the standing instruction body **and** **only** references, templates, **or** assets necessary for bootstrap **and** generic response handling. references identify the canonical shared runtime **and** capabilities rather than copy executable contents.
- do **not** bundle deterministic scripts, executable helpers, copies of the MODEL//ANECHOIC <+ Atom/(.Header.Role in RMED), independent Workflow transitions, **or** a task-prompt library as Skill-owned procedure. Prompt Implementation remains separately owned; the current Step invocation remains delivered through MCP.
- keep discovery metadata, standing body, **and** optional bootstrap resources distinguishable so the host can load the applicable part. portable content is shared; host-specific encoding follows its declared host boundary rather than assuming **every** host has identical fields **or** loading behavior.

this Delivery specifies the package Carrier, **not** a new Workflow, permission policy, response schema, installer, Hook, host-support promise, **or** PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ API implementation.
