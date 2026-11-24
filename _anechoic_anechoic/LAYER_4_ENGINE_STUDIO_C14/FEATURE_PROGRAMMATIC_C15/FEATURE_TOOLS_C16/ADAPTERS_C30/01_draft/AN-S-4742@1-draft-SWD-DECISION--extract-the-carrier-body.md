---
atom_family: SPEC
atom_id: AN-S-4742
container:
  component: C30
tier: 1
context:
  template: DECISION
  lens: SWD
relations:
  IS_SOLUTION_FOR:
  - AN-S-3303@15
state:
  status: draft
  version: 1
  updated_at: '2026-11-23T22:54:35.599814+00:00'
---

## Summary

Extract the carrier body.

## Claim

### Prose Claim

For `frontmatter_bounds` and `source_body` in `carrier_body__pub.py`,
select the first eligible exact closing delimiter after an exact opening
line. Return its byte bounds and the unchanged body, or an explicit
missing-delimiter outcome. These operations have no Project state,
filesystem, or network effects.

### Formal Claim

Inputs are byte lists (each `Nat` is at most 255). The outcome abstracts
`source_body`'s path-bearing unsupported-delimiter error. The path is
provided by the caller and is not a filesystem access.

```lean
import Lean

namespace CarrierBodySolution

def opening (xs : List Nat) : Option Nat :=
  if xs.take 4 == [45,45,45,10] then some 4
  else if xs.take 5 == [45,45,45,13,10] then some 5
  else none

def closingLength : List Nat → Option Nat
  | 13 :: 10 :: 45 :: 45 :: 45 :: 13 :: 10 :: _ => some 7
  | 13 :: 10 :: 45 :: 45 :: 45 :: 10 :: _ => some 6
  | 10 :: 45 :: 45 :: 45 :: 13 :: 10 :: _ => some 6
  | 10 :: 45 :: 45 :: 45 :: 10 :: _ => some 5
  | _ => none

def firstClosing : List Nat → Nat → Option (Nat × Nat)
  | [], _ => none
  | x :: xs, pos =>
    match closingLength (x :: xs) with
    | some n => some (pos, pos + n)
    | none => firstClosing xs (pos + 1)

def bounds (raw : List Nat) : Option (Nat × Nat × Nat) := do
  let start ← opening raw
  let (close, stop) ← firstClosing (raw.drop (start - 1)) (start - 1)
  some (start, close, stop)

inductive Outcome where
  | missingDelimiter
  | body (bytes : List Nat)
  deriving Repr, BEq, DecidableEq

def body (raw : List Nat) : Outcome :=
  match bounds raw with
  | none => .missingDelimiter
  | some (_, _, stop) => .body (raw.drop stop)

end CarrierBodySolution
```

## Details

The intended framing model is independent of the implementation. Scoped
effect claims are implementation obligations, not consequences of the pure
model.
