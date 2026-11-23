---
atom_family: SPEC
atom_id: AN-S-264
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Evaluate the installed Toolset across supported boundaries

# Evaluate the installed Toolset across supported boundaries

## Claim checked

the Operator-installed Toolset is self-contained **and** usable within **every**
declared Python **and** platform boundary **without** depending on development-only uv
state **or** project-source imports.

## Test case

apply **to** the same content-addressed Tool release **and** installation shape that an
Operator uses.

## Check

build **or** install that deliverable **and** run its public evaluations under **every**
declared Python **and** platform boundary. inspect imports **and** runtime access for
undeclared state outside the selected release under `.anechoic_runtime/tools`,
persistent operational state under `.anechoic_runtime`, **and** disposable state
under `.anechoic_tmp`.

## Acceptance

pass **only** **when** **every** supported combination succeeds **without** project-source
imports, a project environment, uv, **or** undeclared external state. report **every**
unsupported combination explicitly.

## Failure and stop

fail **when** **only** the local source tree passes, an installed boundary fails, **or**
the release depends on an undeclared source, environment, runtime place, **or**
temporary place.

## Sources

- [Pytest: tests outside application code and installed-package testing](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [PyPA: requires-python](https://packaging.python.org/en/latest/specifications/core-metadata/#requires-python)
