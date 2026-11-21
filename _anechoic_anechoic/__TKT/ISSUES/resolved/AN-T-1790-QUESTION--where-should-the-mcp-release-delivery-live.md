---
atom_family: TKT
atom_id: AN-T-1790
structure:
  container:
    component: C14
  priority: 2
context:
  template: question
state:
  status: resolved
  version: 2
  updated_at: 2026-11-09 15:56:54 +0400
---

## Summary

Where should the MCP release delivery live?

## Question

Where should the MCP release delivery live?

## Details

D577 concerns project-specific release delivery. Its ownership needs coordination with Project Configuration and release Workflow authority outside this bounded MED correction. Keep the Current source and proposed Draft unchanged pending that handoff. Do not move it merely to satisfy ancestry.

## Resolution

The Operator chose whole-project release ownership in FRAMEWORK_DELIVERY, reusing RELEASES / CA-SU-27 as a direct child of Project. This supersedes the earlier Project Configuration destination. The complete local/public Workflow and release-specific RMED families, including D577 and its recovery authorities, are now Current there. The external Goal remains Project-owned. Query readback verified all 80 moves, the stable Scope Unit ID and unchanged Scope Unit census. Implementation and test relocation is deferred to CA-P-2839 in CA-P-2791; no release execution or code change is claimed.
