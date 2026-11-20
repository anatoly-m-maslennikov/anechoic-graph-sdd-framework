---
identity:
  atom_id: AN-S-3089
context:
  container:
    component: C62
  lens: SPEC
  template: PKG
  package_id: pkg1
state:
  status: active
  version: 1
  updated_at: '2026-11-20T10:40:29.349219+00:00'
---

## Summary

Manifest Compiler

## Purpose

Compile Active SPEC Manifests and the admitted Model declarations.

## Contract

Run in a short-lived process triggered through the existing source watcher. Emit complete local Model modules and a Structure snapshot validated against that Model. Record the source revisions and Model fingerprint before publication.
