---
atom_family: TKT
atom_id: AN-T-2114
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 05:37:29 +0400
---

## Summary

Verify Workbench formal declaration inputs

## Details

The compiler reads CFEL from Formal Claim. It ignores comments. Bracketed formats and conditions, wildcard constraints and observed headings do not create property names. The 18-test Content schema check passed, including the finite-list and observed-heading regression.

The isolated candidate image exposed 77 columns, including six declared Content columns, and returned three Core Formal Claims. Check returned ordered column metadata without SQL or rows. The Docker suite still had stale delivery and audit-table assertions. The serving image remains unchanged: live query_run returned 4,002 Atoms and zero Core model rows. Generic inheritance and deployed acceptance remain open under P2866.

Evidence: `.anechoic_tmp/CA-P-2791/CA-P-2866/formal-input-20261111/image-build-final/candidate-result.json` and `docker-e2e.log` in the same folder.
