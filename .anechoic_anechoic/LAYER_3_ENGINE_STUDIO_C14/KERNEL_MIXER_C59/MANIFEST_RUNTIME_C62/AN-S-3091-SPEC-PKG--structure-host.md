---
identity:
  atom_id: AN-S-3091
context:
  container:
    component: C62
  lens: SPEC
  template: PKG
  package_id: pkg3
state:
  status: active
  version: 1
  updated_at: '2026-11-20T10:40:29.349219+00:00'
---

## Summary

Structure Host

## Purpose

Provide the current validated Structure to consumers.

## Contract

Run as a thin, long-lived process. Publish a read-only snapshot API. Each operation holds one snapshot. Atomically replace it on successful compilation and retain the last valid snapshot on failure.
