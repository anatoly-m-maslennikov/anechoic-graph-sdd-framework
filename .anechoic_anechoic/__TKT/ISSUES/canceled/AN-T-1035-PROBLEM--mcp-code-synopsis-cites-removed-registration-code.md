---
atom_family: TKT
atom_id: AN-T-1035
structure:
  container:
    component: C21
  priority: 2
context:
  template: problem
state:
  status: "canceled"
  version: 1
  updated_at: "2026-11-21T08:48:08.692178+00:00"
---

## Summary

MCP Code Synopsis cites removed registration code

## Concern

Current I9 cites selected_route_registration.py, which was removed during a concurrent MCP refactor. direct_gateway.py and hot_reload.py also changed during the bounded review. The fingerprint gate stopped I9 adoption before any Current replacement or archive was written.

## Details

The reviewer located replacement registration evidence in shared_project_catalog.py and shared_gateway.py. The owned I9 Draft now uses that location, but it remains held because the MCP tree changed again during the check. Current I9 remains at Version 1. Capture a consistent MCP source snapshot and verify the revised Claim and code links before promotion. This records stale source evidence; no runtime failure, missing integration or required code rollback is inferred.

The Docker/runtime relocation changed the entrypoint location to `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/docker/entrypoint.py`. I9’s locator was technically rebased to that file. This does not complete the semantic Code Synopsis review in CA-P-2847: selected-route/orchestrator behavior remains retired, and the restored generated registration uses configurable providers and a global MCP blacklist. This Concern remains open.

## Disposition

The Operator uses Spec-Code Mismatch Issues in place of the Code Synopsis.
