---
atom_family: SPEC
atom_id: AN-S-1342
container:
  component: C15
tier: 2
context:
  lens: DevOps
state:
  status: archived
  version: 21
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Materialize the Project temporary boundary

# Materialize the Project temporary boundary

the shared Project Temporary State path boundary **must** be carried **in**
canonical source under `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/` **and** the selected
`.anechoic_runtime/tools/` release.

the root `pyproject.toml` carries the admitted development **and** Evaluation-tool
cache-path configuration. dependency launch Carriers carry explicit temporary,
staging, build, **and** cache-path parameters **when** that dependency does **not**
read `pyproject.toml`. those configured temporary Carriers occupy descendants
of `.anechoic_tmp/`.

Python bytecode caches use `.anechoic_tmp/cache/python/`; the corresponding
entrypoint, test-runner, **or** service-launcher Carrier stores that path **or** the
disabled-bytecode-write setting. the delivered Runtime State root **must not**
contain `__pycache__/` Directory Carriers **or** `.pyc` File Carriers.

temporary-path representations carry owner **and** run identity. the boundary
diagnostic representation carries the violating owner **and** path.

CA-R-1473 owns confinement, identity, cleanup-independence, **and** diagnostic
outcomes. CA-M-289 owns temporary-path construction **and** configuration
conventions; CA-E-467 checks their conformance.
