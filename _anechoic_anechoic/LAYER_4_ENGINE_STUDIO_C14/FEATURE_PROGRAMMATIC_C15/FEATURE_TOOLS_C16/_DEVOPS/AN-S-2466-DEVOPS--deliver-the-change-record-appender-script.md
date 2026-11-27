---
atom_family: SPEC
atom_id: AN-S-2466
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 32
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver the change-record appender script

## Scope

The canonical APPEND_CHANGE_RECORDS executable Carrier, its CLI and Project-bound MCP transport, and shared Journal append/read serialization.

## Claim

### Prose Claim

APPEND_CHANGE_RECORDS **must** be delivered through the canonical source script `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/APPEND_CHANGE_RECORDS/append_change_records.py` **and** its content-identical Carrier **in** the selected `.anechoic_runtime/tools` release.

- expose the common Doer CLI contract with dry-run **and** apply modes.
- Use the release-local shared Journal library for append and read under AN-S-40. The library is not an executable Tool. Append without prior-record lookup or schema/digest validation. Preserve historical records even when they fail Current rules.
- Preserve supplied values and actual replacement references through serialization. Do not invent a baseline, earlier event, Actor, session, time, or outcome.

## Details

### Project-bound append/read transport

The same canonical script **must** expose the existing Project-bound `append_change_records` interface through its registered descriptor **and** CA-O-222, using the shared append/read library. Apply AN-S-5181 to the Project-bound request and modes.

The appender **must not** acquire a Git-effect lease, alter the index, create a Commit, reconstruct observations from current files **or** perform the recorded source/lifecycle operation. Public parameters express data **and** requested operations, **not** authorization; retain the existing authorized Project-MCP boundary **and** ordinary filesystem access. Preserve truthful I/O failure **and** any actually observed partial append; do **not** claim an unobserved completion **or** automatically replay an effect. There is no Journal validation, idempotency, receipt, reconciliation **or** recovery prerequisite.

```toml
[tool_binding]
name = "APPEND_CHANGE_RECORDS"
mcp_name = "append_change_records"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/APPEND_CHANGE_RECORDS/append_change_records.py"
action_ids = ["CA-O-222"]
```
