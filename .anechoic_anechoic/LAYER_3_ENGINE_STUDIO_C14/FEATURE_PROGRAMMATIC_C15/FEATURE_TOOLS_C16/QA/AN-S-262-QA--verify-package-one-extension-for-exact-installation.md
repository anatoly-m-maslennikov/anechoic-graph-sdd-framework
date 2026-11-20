---
identity:
  atom_id: AN-S-262
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 27
  updated_at: 2026-10-27 19:59:33 +0400
---
## Summary

Verify package one extension for exact installation

# Verify package one extension for exact installation

## Claim checked

CA-O-044 produces a reproducible exactly versioned Extension package whose manifest exactly accounts for its package contents.

## Applicable when

apply whenever Extension packaging, manifest, versioning, **or** package-content derivation changes.

## Test case

package the same sealed Extension candidate twice, compare manifests **and** package digests, **then** compare **every** package inventory with its manifest **without** performing an installed-state operation.

## Acceptance criteria

both builds have identical identity, exact version, manifest, **and** package digest; **every** package inventory matches its manifest exactly. installation, uninstallation, update, downgrade, **and** installed-state verification are delegated **to** CA-O-042.

## Failure disposition

reject the package **and** preserve candidate frontier, both builds, manifests, digests, package inventories, manifest comparisons, **and** delegation boundary.
