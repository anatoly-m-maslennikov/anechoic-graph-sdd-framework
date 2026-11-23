---
atom_family: SPEC
atom_id: AN-S-387
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Compare and add numeric values in CFEL

## Claim

### Prose Claim


- `x > y`: x is greater than y.
- `x >= y`: x is greater than or equal to y.
- `x < y`: x is less than y.
- `x <= y`: x is less than or equal to y.
- `x + y` returns the numeric sum of two numeric operands. If both operands are integers, the result is an exact integer.
- Each operand resolves to one numeric value. No string coercion is allowed.
- Evaluate `+` before `=`, `!=`, `>`, `>=`, `<` and `<=`. Parentheses override this order.
- `=` tests equality, including in a Claim invariant; it does not assign a value.
- A missing or multi-valued operand makes an evaluated comparison invalid.
- Guard optional Properties by their occurrence before comparing their values.
- A comparison in Claim must hold. In an IF condition, it tests the values.
- An IF conclusion is evaluated only when its condition holds.
- A Declaration applies the comparison to each matching instance.
- Comparisons do not assign values or change occurrence counts.
- `+>`, `<+`, `>|` and `|<` remain distinct Relation operators.

## Details

```CFEL
# model
Atom.Header.Version >= 1;

Atom.Header.Tier >= -1;

# instances
Atom/(.Header.Role: Plan)//$atom;

IF ($atom.Header.Work Sequence Number{=1})
THEN ($atom.Header.Work Sequence Number > 0);
```
