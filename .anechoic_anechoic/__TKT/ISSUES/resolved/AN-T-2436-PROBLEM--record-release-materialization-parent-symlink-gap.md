---
identity:
  atom_id: AN-T-2436
context:
  container:
    component: C16
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 01:47:30 +0400
---
# Summary

Record Release materialization parent symlink gap

## Concern

The initial P1650 staging path created the materialization parent without refusing symlinked existing parent components. The saved helper checks every existing component for symlinks and non-directories before writes. Its disposable-project corpus includes a symlink-parent zero-effect refusal and passes four tests in total. test_release_compilation.py SHA-256 is f334a175c3d97abb3f283acda45c654b2be839145c7da45a370e33efb5f3aea3. C447's denied Projection relocation is untouched; this is a code-path safety repair, not permission to retry or bypass it.

## Evidences

The directly affected Task preserves the exact resulting files, source pins, actual focused test outputs and remaining coverage.

## Blast radius

The narrow implementation slice named above. No broader source audit, runtime promotion or denied-operation workaround is authorized by this record.
