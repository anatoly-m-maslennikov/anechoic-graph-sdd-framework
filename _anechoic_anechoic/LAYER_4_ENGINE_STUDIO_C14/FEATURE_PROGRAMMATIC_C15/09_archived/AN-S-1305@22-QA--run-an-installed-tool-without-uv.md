---
atom_family: SPEC
atom_id: AN-S-1305
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 19:59:34 +0400
---
## Summary

Run an installed Tool without uv

## Claim

### Prose Claim

#### Claim checked

one installed ANECHOIC Tool executes from `.anechoic_runtime/tools` **without** uv, a
project virtual environment, **or** another dependency outside the selected
runtime release.

#### Test case

invoke one installed Tool **in** a clean process **where** uv **and** the project virtual
environment are unavailable.

#### Acceptance criteria

pass **only** **when** the Tool reaches its declared entry boundary using solely its
installed carrier **and** admitted host prerequisites.

#### Failure disposition

reject the installed-runtime claim **until** the external workflow dependency is
removed.

#### Sources

- [CA-M-429 — Use uv as the default Python workflow frontend](../05_method/CA-M-429-PROGRAMMATIC-ENG_POLICY--use-uv-as-the-default-python-workflow-frontend.md)
