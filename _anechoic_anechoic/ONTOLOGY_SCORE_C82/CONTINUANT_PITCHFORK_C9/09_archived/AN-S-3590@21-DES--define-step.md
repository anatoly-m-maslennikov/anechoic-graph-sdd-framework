---
atom_family: SPEC
atom_id: AN-S-3590
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-27 19:59:56 +0400
---
## Summary

Define Step

# Summary

Define Step

## Scope

the Step entity.

## Claim

a Step **means** a node **in** a Workflow, defined by **`=1`** Step Atom. a leaf Step, including a leaf substep, specifies invocation of **`=1`** reusable Action with the parameters **and** inputs for that invocation; a containing Step with nested substeps specifies no own Action launch.

## Details

- the binding identifies the source of **every** required input **or** parameter, including a Workflow input **or** an earlier Step result **when** applicable; it need **not** fix runtime values **in** the definition.
- a substep is a nested Step, not a separate Type. a containing Step owns its nested substeps and does **not** launch an Action of its own.
- a Linear Step has ordered nonconditional substeps and no conditional substeps. a Conditional Step chooses **exactly one** branch in its own definition from its declared result condition and **may** use Actor input; result-based routing belongs to that Conditional Step definition.
- different Steps **may** reference the same Action with different bindings **without** copying **or** redefining that Action.
- an Agentic invocation selects Integrated **or** Isolated context under CA-R-1527; a Programmatic invocation does **not** acquire an Agent context by this rule.
- the Step definition is distinct from its referenced Action **and** from a Step Run. internal Tool calls remain execution details under CA-R-1528, **not** additional Step definitions.
