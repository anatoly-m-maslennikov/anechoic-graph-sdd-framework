---
atom_family: SPEC
atom_id: AN-S-3001
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:02:57.528847+00:00'
---
## Summary

Define Component Manifests and Purposes

## Claim

### Prose Claim

A Component Manifest is the Tier 0 Spec Atom that describes a child Component. Its Header gives the parent Component. In its Markdown body, `## Purpose` states why the child exists and describes its responsibilities and obligations. `## Formal manifest` contains the Anechoic Python eDSL declaration of the child's stable ID, name, and settings, including its layer where applicable. A child can add Purpose prose later. A local extension defining a new Component kind belongs in PMETA.

## Details

Acceptance requires one Component Manifest in the parent Component's Spec root. Its declared Component ID identifies the child. Its Purpose belongs in that same Atom.

Sources: CA-A-1461@1-draft, CA-A-1463@1-draft. Task: CA-P-3079.
