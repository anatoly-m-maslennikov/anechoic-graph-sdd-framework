---
atom_family: TKT
atom_id: AN-T-1574
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 06:04:38 +0400
---
## Summary

bound Unit execution after Release host loss

# Summary

bound Unit execution after Release host loss

## Objective

implement the accepted host-independent Unit deadline and fixed temporary-mount contract, preserving sealed commands and non-passing timeout evidence.

## Details

source-first authority and independent review precede implementation. preserve the installed runtime, historical Release evidence and unrelated changes. root owns source publication and actual runtime dispatch.

## Definition of Done

the 18 bounded regression tests pass; independent code review accepts the guard; an installed-image diagnostic confirms daemon-owned timeout without a live host observer. full Release acceptance remains separately gated.

## Acceptance evidence

18 focused tests passed; independent review accepted the corrected command delimiter and timeout-latching behavior. the exact installed-N image ran a detached, isolated diagnostic with a two-second deadline and a child that exits zero on TERM. with no attached host observer during the deadline, the daemon reported exit 124. retained evidence: `.anechoic_tmp/epic-resume-release/N15/deadline-tests/actual-docker.gTAxcn/terminal-inspect.json`. implementation commit: `8d1867c9e`. this is bounded guard acceptance, not a passing full Release gate.
