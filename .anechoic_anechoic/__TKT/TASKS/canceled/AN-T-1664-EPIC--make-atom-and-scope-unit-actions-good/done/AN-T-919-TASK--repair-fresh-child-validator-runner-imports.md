---
atom_family: TKT
atom_id: AN-T-919
structure:
  container:
    atom: AN-T-1664
  priority: 2
context:
  template: task
state:
  status: done
  version: 5
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Repair fresh-child validator runner imports

## Objective

Repair the bounded fresh-child runner/import setup exposed by the nine failing `VALIDATE_ATOMS` modules in the second local-release attempt, without changing validator or production-guard semantics.

## Details

Use the retained failure evidence from `.anechoic_tmp/simple_local_release/local-20261020-current-target-parser-repair-1438-tests-a71g3vcj.log` and the matching `runtime/reports/runid.md`. Isolate the runner/import repair from the shared frozen-fixture repair in CA-P-2456. Run only the focused affected modules and record actual results; preserve fresh-child isolation, current source provenance and intentional refusals. No production request, image replacement, Git mutation or full-release retry is part of this Task.

At most15minutes ownwork, split before extending. Preserve unrelated concurrent changes and exact predecessor evidence.

### Definition of Done

The nine affected `VALIDATE_ATOMS` fresh-child import paths run with the intended current runner setup and focused checks pass, with the exact source/test boundary recorded. This narrow Task claims neither a production guard fix nor full-suite, deployment or release acceptance.

### Completion checkpoint

The scoped receipt records 13/13 runner checks and 133/133 former fresh-child modules passing with zero skips; independent review is `APPROVE`. This is test-environment evidence only and does not claim installed deployment, production guard repair, full release or Epic completion.
