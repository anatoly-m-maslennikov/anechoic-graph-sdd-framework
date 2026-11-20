---
atom_family: TKT
atom_id: AN-T-1958
structure:
  container:
    component: C15
  priority: 2
context:
  template: question
state:
  status: resolved
  version: 2
  updated_at: 2026-11-10 22:04:06 +0400
---

## Summary

Should configurable model composition be adopted?

## Concern

Four unpromoted Drafts propose a generic model-composition mechanism with additions, overrides and runtime refresh. They still leave the carrier, composition mechanism, refresh trigger, override permissions and invalid-refresh behavior open. Current R1375 forbids Core shadowing or reinterpretation; these Drafts do not supply a new permission.

## Details

Keep the four Drafts unadopted while completing the reviewed Engine specification. Do not turn their open alternatives into runtime requirements or broaden the Workbench schema mechanism to implement them.

A future proposal must choose the permitted extension surface, exact source/configuration format and precedence, and whether rejected refresh pauses model-dependent work or retains the prior complete generation. Then review its Method, Evaluations and Delivery against that choice.

Blast radius: four first-version Drafts only. No Current Atom, Core authority, Scope tree or running service changes.

## Draft sources

- CA-R-2968
- CA-M-494
- CA-E-789
- CA-D-699

## Resolution

The Operator deferred configurable model additions and overrides to version 0.6. Project Objective CA-P-2904 tracks the future work. Do not adopt or implement this feature for the current version. The four existing Drafts remain unchanged as proposal inputs; no override permission is introduced.
