---
identity:
  atom_id: AN-S-3090
context:
  container:
    component: C62
  lens: SPEC
  template: PKG
  package_id: pkg2
state:
  status: active
  version: 1
  updated_at: '2026-11-20T10:40:29.349219+00:00'
---

## Summary

Model Host

## Purpose

Provide the loaded Model to implementation and validators.

## Contract

Run as a thin, long-lived process. Consumers import only the compiled types and rules they need. Activate a new Model generation by restarting the host and consumers that imported the previous Model.
