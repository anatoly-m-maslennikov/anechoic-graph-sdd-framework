---
atom_family: TKT
atom_id: AN-T-968
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

Implement versioned and dated ANECHOIC image names

## Objective

Implement versioned and dated ANECHOIC image names.

## Details

Reuse the canonical image owner to give newly built ANECHOIC images an inspectable repository/name and tag containing the actual framework version and UTC build date; carry matching standard image metadata. Read current runtime/release RMED and reconcile its precise display-tag permission before implementation. Derive version from the exact source/package boundary, never a live checkout fallback. Preserve immutable sha256 selection, fingerprint and Project isolation, no moving an existing tag, no latest alias, and no runtime replacement. Include development and test builders in the affected closure. At most15minutes own work; split before extending. Acceptance is a frozen source change reviewed against caller/build-context closure; tests are P2519.

### Verified checkpoint

P2522 follow-up accepted before parent completion. Canonical version/date/SHA display tags, exact version.toml fingerprint input and OCI version label implemented with immutable admission unchanged.109/109 focused checks and real isolated build/reuse passed. Bounded legacy layout exception: runtime_images.py513 lines and runtime.py332 lines remain canonical owners (ceilings520/340 for this increment); new pure metadata helper56 lines. Reconsider split before scope/bounds grow. Existing3C901 diagnostics unchanged; no global clean-lint claim.
