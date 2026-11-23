---
atom_family: SPEC
atom_id: AN-S-1305
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-22 16:26:49 +0000
---
## Summary

Run an installed Tool without uv

# Run an installed Tool without uv

## Claim checked

one installed ANECHOIC Tool executes from `.anechoic_runtime/tools` **without** uv, a
project virtual environment, **or** another dependency outside the selected
runtime release.

## Test case

invoke one installed Tool **in** a clean process **where** uv **and** the project virtual
environment are unavailable.

## Acceptance criteria

pass **only** **when** the Tool reaches its declared entry boundary using solely its
installed carrier **and** admitted host prerequisites.

## Failure disposition

reject the installed-runtime claim **until** the external workflow dependency is
removed.

## Sources

- [CA-M-429 — Use uv as the default Python workflow frontend](../05_method/CA-M-429-PROGRAMMATIC-STANDARD-IMPLEMENTATION_DECISION--use-uv-as-the-default-python-workflow-frontend.md)
