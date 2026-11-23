---
atom_family: PROJECT_CONFIG
atom_id: AN-P-5
structure:
  container:
    component: C16
context:
  template: action
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 17:05:24 +0400
---
## Summary

Package one Extension for exact installation

# Package one Extension for exact installation

Package Extension **means** the reusable Action that produces one verified, exactly versioned, reproducible Extension package **without** changing the installed state under CA-R-1150. its modeled boundary is the complete requested result; partial comparison, incomplete attribution, **or** an unreported unresolved input is **not** an independently successful outcome.

## Applicable when

use this Action **when** an accepted Extension candidate is ready **to** become an exactly installable package.

## Action

1. seal the Extension identity, exact version, source Atom revisions, dependency contract, **and** compatibility boundary.
2. assemble **only** declared authority, implementations, deliveries, **and** required package metadata into a deterministic manifest.
3. build the package reproducibly from that manifest **and** record the manifest **and** package digests.
4. compare the package contents with the manifest **and** reject **any** omitted, additional, **or** nondeterministic packaged item.
5. finish packaging **without** changing installed state. installation, uninstallation, update, downgrade, **and** installed-state verification belong **to** the separate CA-O-042 Action; packaging does **not** invoke that Action as a required final step.

## Outcome

the Extension has one stable identity, exact version, deterministic manifest, **and** reproducible package digest.

## Failure or stop

do **not** publish a package with unresolved dependencies, mutable version identity, nondeterministic contents, **or** a manifest-package mismatch.
