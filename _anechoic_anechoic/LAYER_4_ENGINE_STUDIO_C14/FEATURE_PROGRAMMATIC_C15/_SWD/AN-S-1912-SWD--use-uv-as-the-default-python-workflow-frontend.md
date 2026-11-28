---
atom_family: SPEC
atom_id: AN-S-1912
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: "active"
  version: 17
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---

## Summary

Use uv as the default Python workflow frontend

## Claim

### Prose Claim

Use uv as the default frontend for every admitted Python workflow capability that it provides. Use uv alone for governed Project Python workflows. Follow AN-S-1259 for the isolated execution environment, including development, installed Project Tools and host launchers.

This Method selects the frontend. Configuration and Implementation materialize the selection. Delivery governs its Carriers. Operations defines reusable Workflow behavior. Journal Records supply the evidence required by the business-lifecycle contract.

## Details

### Applicable when

Apply when developing, evaluating, building, packaging, or executing PROGRAMMATIC Python source, including installed Project Tools and host launchers.

### Procedure

1. Use the accepted Method and canonical Project technical configuration to identify the supported Python boundary. Preserve the selected isolated environment and locked dependencies in packaged runtimes.
2. Declare dependencies selected by accepted Methods in `pyproject.toml`. Use `uv add` or `uv remove` so the declaration and the reviewed `uv.lock` change together.
3. Use `uv tool run` only for an isolated Python CLI outside the admitted Project dependencies. Pin the Tool version and command. Exclude unpinned ephemeral execution from acceptance evidence.
4. Use `uv build` or `uv publish` only when an accepted Delivery authorizes the package or publication target.
5. Put uv cache, build and staging state in `.anechoic_tmp/`.

### Failure or stop

Stop under AN-S-1259. Also stop when the lockfile is stale, a command would implicitly update the environment during evidence collection, or a capability gap or external boundary would require another Python workflow manager.

### Sources

- [uv: Features](https://docs.astral.sh/uv/getting-started/features/)
- [uv: Installing and managing Python](https://docs.astral.sh/uv/guides/install-python/)
- [uv: Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
- [uv: Tools](https://docs.astral.sh/uv/concepts/tools/)
- [uv: Configuring projects](https://docs.astral.sh/uv/concepts/projects/config/)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
