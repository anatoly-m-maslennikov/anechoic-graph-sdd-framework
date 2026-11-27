---
atom_family: SPEC
atom_id: AN-S-3116
container:
  component: C45
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-26T16:38:46.186169+00:00'
---
## Summary

Store native Workbench DuckDB data on disk

## Claim

### Prose Claim

- Use one Project-local DuckDB file and the existing serialized owner.
- Keep the database and spill files in Workbench runtime state.
- Keep Project sources and the Journal authoritative for their facts.
- Validate retained data before serving queries.
- Reuse valid parsed imports and reconcile changes made while Workbench was stopped.
- Store live results in the database. Apply expiry, pinning, and startup rules.
- Rebuild one table or all tables on demand. Include dependent tables by default.
- Publish new result IDs with their View bindings and pins.
- Report rebuild failures to stderr and the requesting HTTP or MCP client.
- Roll back failed SQL writes.
- Require an explicit restart if a failure may have invalidated graph registration.
- Make a second writer exit with an explicit lock error.

### Formal Claim

For one HTTP rebuild SQL failure before publication, `diagnostic` is a stderr
report identifying the failed rebuild operation. `clientError` is the terminal
response to the requesting client.

```lean
namespace WorkbenchRebuildFailure

inductive Event where
  | failed | diagnostic | published | clientError | clientSuccess
  deriving DecidableEq

def afterFailure : Bool → List Event → Bool
  | _, [] => false
  | _, .diagnostic :: rest => afterFailure true rest
  | seen, [.clientError] => seen
  | seen, .failed :: rest => afterFailure seen rest
  | _, _ => false

def conforms : List Event → Bool
  | [] => false
  | .failed :: rest => afterFailure false rest
  | _ :: rest => conforms rest

example : conforms [.failed, .diagnostic, .clientError] = true := by decide
example : conforms [.failed, .diagnostic, .diagnostic, .clientError] = true := by decide
example : conforms [.failed, .clientError] = false := by decide
example : conforms [.failed, .published, .diagnostic, .clientError] = false := by decide
example : conforms [.failed, .diagnostic, .clientSuccess] = false := by decide
example : conforms [.failed, .diagnostic, .clientError, .published] = false := by decide

end WorkbenchRebuildFailure
```
