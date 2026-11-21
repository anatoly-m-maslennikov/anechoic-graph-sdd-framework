---
atom_family: TKT
atom_id: AN-T-2031
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: resolved
  version: 2
  updated_at: '2026-11-12T03:19:25.294074+00:00'
---
## Summary

How should Update report corrected input after writing

## Question

If promotion requests corrected input after Update has already saved a Draft and archived the Current Atom, should Update stop and report the error with completed effects, or wait for an explicit correction and resume only promotion?

## Details

CA-R-1105 and CA-M-167 settle the Tool behavior. Before the first effect, the caller can correct input. After an effect, Update stops and returns the error and completed effects. The focused Update failure test confirms that behavior. CA-O-10024@3 still says to wait and resume promotion. Its wording needs the Methodology handoff already tracked in CA-P-2791. CA-O-10018@2 already describes reporting failure with completed effects.
