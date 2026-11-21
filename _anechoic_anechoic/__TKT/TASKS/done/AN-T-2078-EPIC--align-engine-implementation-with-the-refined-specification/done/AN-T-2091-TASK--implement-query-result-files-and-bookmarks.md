---
atom_family: TKT
atom_id: AN-T-2091
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: task
state:
  status: done
  version: 3
  updated_at: 2026-11-11 07:35:41 +0400
---

## Summary

Implement query result files and Bookmarks

## Objective

Implement the adopted query delivery and Bookmark RMEDO. Use CA-R-2729, CA-R-2776, CA-D-673 and CA-M-516 and their related Methods and Evaluations as the specification. Keep native UI activation and unrelated tools outside this Task.

## Subtasks

- [x] Review the next scoped RMEDO batch and fix any contradiction. (ETA: up to 15 min.)
- [x] Gather applicable Method Policies, then REDO and non-Policy Methods. (ETA: up to 15 min.)
- [x] Implement one Backend batch from the reviewed inputs. Split before exceeding 20 min.
- [x] Implement the scoped Frontend and MCP consumer changes in separate ownership lanes. Split each batch before exceeding 20 min.
- [x] Implement and run the related real-interface Evaluations. Split each batch before exceeding 20 min.
- [x] Review the result and record a small Work Report. (ETA: up to 15 min.)

## Definition of Done

The adopted RMEDO is implemented and its related real-interface Evaluations pass. Unrun checks and unresolved issues are explicit. This Task does not replace the specification.


## Verified batches

P2923 records real MCP JSON-matrix/CSV/TOON exports. P2928 records the Bookmark terminology correction and saved-item/browser checks. P2940 and P2943 cover adapter delivery and browser partial save. P2950 verifies the complete result delivery and Bookmark acceptance against image 87f745f425bc. P2818 tracks local delivery.
