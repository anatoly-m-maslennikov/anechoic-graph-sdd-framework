---
atom_family: TKT
atom_id: AN-T-2977
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 4
  updated_at: "2026-11-22T10:32:28.957135+00:00"
---

## Summary

Apply SSOT to Project Manifest settings

## Objective

Keep Project identity and Project-owned choices in the Project Manifest. Derive Structure from Component and Component Seed Manifests. Read Atom types, properties, and relations from Meta-Ontology and the Project Config Custom Model.

## Done when

The Project Manifest carries Project choices. Runtime consumers derive values from their authoritative sources. Project selection, Workbench, Import Graph, and MCP preserve their behavior.

## Python launch model

AN-S-3310@3 defines three Python roots and four environments.
AN-T-2983 splits the uv Projects and sets up `release`, `setup`,
`prod`, and `dev`. AN-T-2980 adds static QA after the import migration.
