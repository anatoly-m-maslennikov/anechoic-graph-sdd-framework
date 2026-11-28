---
atom_family: SPEC
atom_id: AN-S-5048
concern:
  subject: Executable File
  path: Model/Carrier/File
  relation: is_narrower_than
container:
  component: C15
tier: 0
context:
  template: STANDARD
  lens: SWD/SWCS
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-27T20:35:14.221449+00:00"
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

### Prose Claim

Limit each physical source line to 79 characters.
