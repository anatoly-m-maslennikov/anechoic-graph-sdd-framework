---
atom_family: SPEC
atom_id: AN-S-1821
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 26
  updated_at: 2026-10-29 07:45:31 +0400
---
## Summary

Serialize the shared Project Journal

## Claim scope

the shared Project-control Work Journal's serialization.

## Claim

the shared Project Work Journal **must** materialize its logical event table by serializing its ordered event Records as append-only NDJSON File Carrier segments **in** `.anechoic_<project_name>/_journal/` **or** its registered subdirectories. these segments **must** remain Carriers of the same Journal, **not** separate Journals for Scope Units, Content Roles, workflows, **or** derived log views. describing the Journal as a table does **not** replace this registered serialization **or** require a database Carrier.

## Details

This serialization governs the Project-control Work Journal, not every runtime technical or business Journal. Runtime Journal Delivery may use configured local or remote databases and logging sinks.
