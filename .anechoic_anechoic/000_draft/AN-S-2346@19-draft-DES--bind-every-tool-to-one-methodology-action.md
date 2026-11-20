---
identity:
  atom_id: AN-S-2346
context:
  container:
    component: C00
  tier: 3
  lens: DES
state:
  status: draft
  version: 19
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Bind **every** Tool to one methodology Action

## Claim scope

Tools in the anechoic Project.

## Claim

**in** the anechoic Project, **every** Tool **must** implement **`=1`** Action defined by an existing applicable methodology O Atom.

## Details

- the Tool's RMED identifies that Action as the behavior it realizes **and** specifies its implementation obligations **without** copying the canonical Action definition.
- a Workflow Step binds its Action under CA-R-2465; the corresponding Tool realizes that Action rather than redefining the Workflow graph.
- this cardinality constrains the Action implemented by the Tool. it does **not** count internal instructions, API calls, interactions, **or** retries.

the binding is **not** a requirement **to** use that Action **or** a particular Workflow **to** build the Tool.
