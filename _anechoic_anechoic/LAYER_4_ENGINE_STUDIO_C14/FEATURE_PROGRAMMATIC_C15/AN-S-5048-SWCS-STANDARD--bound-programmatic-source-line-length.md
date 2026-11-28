---
atom_family: SPEC
atom_id: AN-S-5048
concern:
  subject: Executable File
  path: Model/Carrier/Filesystem/File
  relation: is_narrower_than
container:
  component: C15
tier: 0
context:
  template: STANDARD
  lens: SWD/SWCS
state:
  status: "active"
  version: 3
  updated_at: "2026-11-28T11:52:02.110048+00:00"
---

## Summary

Bound PROGRAMMATIC source line length

## Semantics

The bound applies to each physical line in authored textual source, including
test code. The line ending does not contribute to the count.

## Claim

### Formal Claim

```lean
namespace ProgrammaticLineLength

def conforms (characters : Nat) : Bool :=
  decide (characters ≤ 79)

end ProgrammaticLineLength
```
