---
atom_family: SPEC
atom_id: AN-S-3310
concern:
  components:
  - C72
  - C14
  - C27
  - C65
container:
  component: C72
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 9
  updated_at: '2026-11-23T14:32:18.783461+00:00'

---
## Summary

Isolate Python roots and environments by Project child

## Solution

Engine Studio, Release, and Setup are separate uv Projects. Each owns one Python import root and one `pyproject.toml` and `uv.lock` under `LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/`. Keep import roots in the respective code folders. A child calls another through its CLI or API.

Use Release and Setup environments for their executables. Build Engine Studio `prod` and `dev` from its single lock: `prod` supplies runtime dependencies and `dev` adds QA dependencies.

Keep Python tool caches and retained bytecode under `.anechoic_tmp/python/`. Do not restore root-level Python project or lock files. Check child import boundaries and launchers independently.
