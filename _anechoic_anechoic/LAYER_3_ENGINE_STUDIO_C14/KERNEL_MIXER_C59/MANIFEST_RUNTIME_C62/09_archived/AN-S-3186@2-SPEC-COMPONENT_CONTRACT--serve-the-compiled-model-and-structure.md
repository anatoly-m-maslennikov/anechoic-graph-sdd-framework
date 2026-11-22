---
atom_family: SPEC
atom_id: AN-S-3186
container:
  component: C62
tier: 1
context:
  template: component_contract
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-22T07:51:44.972692+00:00"
---

## Summary

Serve the compiled Model and Structure

## Guarantee

Given a selected native Project, provide the compiled Model directory,
the current Structure snapshot path, and the bound Model for the lifetime
of the Manifest Runtime. Provide them after both hosts accept the initial
generation. The Model and Structure share one Model source fingerprint.

Publish a replacement Structure snapshot at the same path when a relevant
Manifest change compiles successfully and the Structure host accepts it.
Keep the last accepted snapshot available if a rebuild fails.

## References

AN-S-3088, AN-S-3089, AN-S-3090, AN-S-3091, and AN-T-2947.
