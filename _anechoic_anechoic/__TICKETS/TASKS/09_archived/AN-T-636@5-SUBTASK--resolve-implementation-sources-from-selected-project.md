---
atom_family: TKT
atom_id: AN-T-636
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 08:22:45 +0400
---
## Summary

Resolve Implementation sources from selected Project

# Summary

Resolve Implementation sources from selected Project

## Objective

Within <=15 minutes, implement independently accepted P1575 bindings in the Implementation prompt package.

## Details

- Own implementation_actions.py, source_bindings.json, narrowly required short prompts and focused prompt package tests. Do not edit selected_execution, backend, providers, fixture, source Atoms, Plans or Journal.
- Resolve selected_project against the separately trusted frozen Project root supplied by the graph owner. Safe relative references and exact source identity/version/digests plus full active-M content must match that Project, not immutable code location or packet-asserted absolute root.
- Implement an explicit trusted selected_project_root handler interface and send the exact wrapper signature to root. Preserve compatible standalone/Base Revise consumers without weakening selected invocation. Refresh derived source bindings only for the independently accepted saved source packet.
- Missing/stale/mismatched Project, source/projection or workspace/capability blocks before Agent launch. Test image code root differing from selected Project and no CLI launch on invalid input. Apply patch, preserve others, inherit 90%; no commits, FPF, harvesting, paid Agent or live Project mutation.

## Saved result

Selected prompt calls now require graph-supplied trusted selected_project_root; packet roots cannot authorize resolution. Exact bounded safe relative source identity/version/hash, full active-M content and workspace/capability validated before Agent invocation. Reviewed source_bindings refreshed after source ACCEPT. Docker prompt/selectedProject suites 16/16 passed; diff checks pass. Graph wrapper must still supply its frozen root (P1586), and startup/fixture/image gates remain separate.

## Definition of Done

The bounded selected Project resolver and current prompt bindings pass focused tests; startup/fixture/image effects remain separate gates.
