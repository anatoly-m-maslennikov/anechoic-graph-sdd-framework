---
atom_family: SPEC
atom_id: AN-S-4739
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: QA
state:
  status: active
  version: 3
  updated_at: '2026-11-27T11:11:44.727957+00:00'

---

## Summary

Check Engine source quality

## Claim

### Prose Claim

#### PROGRAMMATIC Standards

For PROGRAMMATIC source, check the C15 Standards for Module and function
size, line length, Python records, and authored web source. Apply the
Python record and web language checks to authored Project source.

#### Analyzer profile

Check Python imports and mutable defaults with the required Static Ruff
selection F401 and B006. Use the committed Ruff formatter and
lint/complexity profile, including its configured C901 limits. This selection
does not make every Ruff rule required. Run the locked Mypy profile against
its declared targets.

#### Web analysis

Within the Static source roots, run each Package's declared `check:types`
script. Run `lint` when the Package declares it and configures typed ESLint.

#### Suppressions and evidence

Keep each local static-analysis suppression explicit, narrow, and justified
at its affected line or symbol. Record analyzer diagnostics, baseline, and
suppression evidence separately from runtime and behavioral checks. Apply
AN-S-3359 to floating promises and honor intentional shared-state exceptions
under AN-S-3355.

#### Source size

Outside PROGRAMMATIC, where `enforce_source_size` is enabled, limit Python,
JavaScript and TypeScript modules to 300 nonblank lines and functions to 45.
Use the locked frontend parser to measure web functions. When the line
length gate is enabled, check source covered by the root EditorConfig.

#### Prose comments

Engine source and tests must contain no prose comments. Keep comment syntax
only when an interpreter, build tool or static analyzer uses it, including
shebangs, encoding declarations, type annotations and applicable lint
suppressions. The required source check must report prose comments by file and
line and fail without mutating source. An explicit purge must preserve code
behavior, string literals, docstrings and required directives.

#### Cache placement

Apply AN-S-1342 to Python cache placement.
