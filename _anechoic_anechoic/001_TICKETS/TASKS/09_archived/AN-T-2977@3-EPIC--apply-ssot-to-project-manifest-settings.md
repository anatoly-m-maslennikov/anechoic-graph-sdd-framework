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
  status: "archived"
  version: 3
  updated_at: "2026-11-22T10:32:28.956140+00:00"
---

## Summary

Apply SSOT to Project Manifest settings

## Objective

Keep Project identity and Project-owned choices in the Project Manifest. Derive Structure from Component and Component Seed Manifests. Read Atom types, properties, and relations from Meta-Ontology and the Project Config Custom Model.

## Done when

The Project Manifest carries Project choices. Runtime consumers derive values from their authoritative sources. Project selection, Workbench, Import Graph, and MCP preserve their behavior.

## Python launch model

AN-S-3310@2 defines the roots and runtime and QA dependency sets for
Engine Studio, Release, and Setup. AN-T-2983 splits the uv Projects.
AN-T-2980 adds the static QA check after the import migration.
