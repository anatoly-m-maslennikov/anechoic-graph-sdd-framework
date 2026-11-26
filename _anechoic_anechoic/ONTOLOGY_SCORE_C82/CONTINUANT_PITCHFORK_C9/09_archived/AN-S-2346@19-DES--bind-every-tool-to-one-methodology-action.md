---
atom_family: SPEC
atom_id: AN-S-2346
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 19
  updated_at: "2026-11-25T23:09:45.407868+00:00"
---
## Summary

Bind **every** Tool to one methodology Action

## Claim

### Prose Claim


Tools in the anechoic Project.


**in** the anechoic Project, **every** Tool **must** implement **`=1`** Action defined by an existing applicable methodology O Atom.

## Details

- the Tool's RMED identifies that Action as the behavior it realizes **and** specifies its implementation obligations **without** copying the canonical Action definition.
- a Workflow Step binds its Action under CA-R-2465; the corresponding Tool realizes that Action rather than redefining the Workflow graph.
- this cardinality constrains the Action implemented by the Tool. it does **not** count internal instructions, API calls, interactions, **or** retries.

the binding is **not** a requirement **to** use that Action **or** a particular Workflow **to** build the Tool.
