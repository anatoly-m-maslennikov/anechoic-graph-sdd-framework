---
atom_family: SPEC
atom_id: AN-S-3310
container:
  component: C72
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 6
  updated_at: '2026-11-22T12:50:53.527842+00:00'

---

## Summary

Isolate Python roots and environments by Project child

## Solution

Engine Studio, Release, and Setup are separate uv Projects. Each child
owns one Python import root and its executable entry points. Store each
child's `pyproject.toml` and `uv.lock` in its own subdirectory under
`LAYER_3_ENVIRONMENTS_C72/`. Keep the Python import roots in the code
folders of Engine Studio, Release, and Setup.

Run each executable through uv in its owning Project. Engine Studio
exposes runtime and test commands. Release exposes image build, Local
Release, and Public Release. Setup exposes installation.

A child calls another child through its CLI or API. For example, Release
invokes the Engine Studio test executable in the dev environment.
The Import Graph resolves each child's code from that child's Python root.

Use four environments.

- `release` runs Release executables.
- `setup` runs Setup executables.
- `prod` contains the Engine Studio runtime dependencies. Use it in the
  runtime image.
- `dev` contains the Engine Studio runtime and QA dependencies for tests
  and static analysis.

Build `prod` and `dev` from the same Engine Studio lock.

Check child boundaries in the static QA phase after the import migration.
Find cross-child Python imports and report the source and target. Test
each launcher separately to verify its Python root and environment.

## References

AN-T-2977, AN-T-2980, AN-T-2983.
