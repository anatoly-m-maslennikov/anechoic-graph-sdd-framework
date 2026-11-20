---
identity:
  atom_id: AN-S-1821
context:
  container:
    component: C00
  tier: 3
  lens: DevOps
state:
  status: draft
  version: 29
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Serialize the shared Project Journal

## Claim scope

the shared Project-control Work Journal's serialization.

## Claim

the shared Project Work Journal **must** materialize its logical event table by serializing its ordered event Records as append-only NDJSON File Carrier segments **in** `.anechoic_<project_name>/_journal/` **or** its registered subdirectories. these segments **must** remain Carriers of the same Journal, **not** separate Journals for Scope Units, Content Roles, workflows, **or** derived log views. describing the Journal as a table does **not** replace this registered serialization **or** require a database Carrier.

## Details

This serialization governs the Project-control Work Journal, not every runtime technical or business Journal. Runtime Journal Delivery may use configured local or remote databases and logging sinks.
