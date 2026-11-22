---
atom_family: TKT
atom_id: AN-T-2435
container:
  component: C16
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 01:47:30 +0400
---
# Summary

Record Release compiler evidence identity mismatch

## Concern

The initial P1650 helper executed the installed compiler module but could hash different Project-declared compiler bytes in its success evidence. A disposable fixture stub would therefore be named as if it executed. The saved repair requires declared entrypoint bytes to match the actual executing module before effects; mismatched bytes refuse. The dedicated real-render corpus passes four tests, including this refusal. release_compilation.py SHA-256 is 0c7efbceba973198399a8f5dfcf43ea805868ec463b6588ccced1533be76e148. This resolves the local compiler identity gap, not actual repository Release or image acceptance.

## Evidences

The directly affected Task preserves the exact resulting files, source pins, actual focused test outputs and remaining coverage.

## Blast radius

The narrow implementation slice named above. No broader source audit, runtime promotion or denied-operation workaround is authorized by this record.
