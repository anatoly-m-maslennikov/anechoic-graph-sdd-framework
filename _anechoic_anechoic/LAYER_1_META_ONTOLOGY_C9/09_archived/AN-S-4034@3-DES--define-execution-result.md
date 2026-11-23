---
atom_family: SPEC
atom_id: AN-S-4034
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-10-29 10:28:51 +0400
---
## Summary

Define Execution Result

## Claim

Execution.Result is data actually produced by that execution, including returned values and observed-effect information when provided. It belongs to the execution rather than to an API contract. A Journal Event Record can preserve the result or describe it without becoming the execution itself.

The producing specification determines the Result shape. Counts apply to direct primitive values: an absent or structured Result may have zero direct values, and a sequence may have several; declared child properties are counted separately. This does not require multiple logical Result objects or a universal payload envelope.

### Formal claim

```text
Execution.Result
Execution.Result[scalar]{0+}
```

## Semantics

For an Update Atom execution, the result can state which Atom version was created or archived. The API contract can specify the shape and meaning of that data; it does not prove that the change happened. An actual failure result is not evidence of successful completion.

## Details

CA-A-1276 records the Operator decision. The defining identity and simple schemas are adopted; this does not implement a result envelope or Journal writer.
