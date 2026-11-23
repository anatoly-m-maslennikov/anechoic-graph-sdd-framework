---
atom_family: TKT
atom_id: AN-T-3010
container:
  component: C14
priority: 2
context:
  template: task
  label: Epic
state:
  status: "done"
  version: 1
  updated_at: "2026-11-23T07:35:12.242738+00:00"
---
## Summary

Measure code and Spec size and review Package boundaries

## Objective

Measure directly owned Component code and Spec. Identify Packages where a separate responsibility could have a clearer boundary.

## Work

1. Draft the Architecture Analysis Manifest (AN-S-3391), its Code and Spec Metrics child (AN-S-3396), and the measurement Contract (AN-S-3397) and decision (AN-S-3393).
2. Review and adopt those Specs. Check ownership, test and asset classification, count definitions, and how proposed splits are justified.
3. Implement the accepted rules using the Realization Graph and existing Component metrics. Expose the read-only results through Workbench. Verify exact counts on fixtures and baseline the Engine Studio Packages.

Implementation and Local Release are tracked in AN-T-3011.

## Definition of Done

Workbench reports implementation, test code, and their sum against full Spec and Spec body in physical lines and decimal kB or MB. Package review candidates show their own size and the evidence for any proposed split. The existing AN-S-3390 report remains available.

Code-to-Lean (AN-S-3394) is a child of Architecture Analysis. AN-T-2973 tracks implementation-derived Lean analysis. Spec Engine (AN-S-3395) owns lean Spec schemas and compiles Python Formal Manifests to Lean and Mermaid in separate work.
