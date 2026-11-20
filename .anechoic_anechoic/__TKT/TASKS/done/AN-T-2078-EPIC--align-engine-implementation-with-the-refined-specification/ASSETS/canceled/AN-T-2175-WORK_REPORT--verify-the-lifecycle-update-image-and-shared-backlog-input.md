---
atom_family: TKT
atom_id: AN-T-2175
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: 2026-11-11 18:34:07 +0400
---

## Summary

Verify the lifecycle Update image and shared Backlog input

## Details

The Update candidate passed the six-Tool HTTP checks and all nine Workbench Docker checks. Single-file visibility took 0.24–0.34 seconds. The 500-Atom create, update, rename and move cases took 4.3–5.4 seconds. The Scope Unit rename took 24.3 seconds, the cold rebuild 25.4 seconds, and the short resource guard passed without an OOM.

CA-D-475@25 now places Backlog Plans in the owning Scope Unit Role folder or inside their direct Backlog parent’s matching directory. The build selects its Formal Claim by Main Subject and Delivery Role and compiles the shared Backlog directory. The new acceptance cases show that the current Engine omits logical Backlog children when it archives or closes a Plan without a companion directory. The pre-cutover candidate was held before activation.
