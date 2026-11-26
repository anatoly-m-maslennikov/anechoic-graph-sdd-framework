---
atom_family: SPEC
atom_id: AN-S-2336
container:
  component: C9
tier: 6
context:
  lens: SWD
state:
  status: archived
  version: 15
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Write Operations Claims with Type-specific CCE Profiles

# Summary

Write Operations Claims with Type-specific CCE Profiles

## Scope

Operations Claims written with their admitted Operations Type-specific CCE Profiles.

## Claim

**to** write an Operations Claim, the Author **must** first resolve its admitted Operations Type **and** **then** apply **`=1`** primary Type profile:

1. for Action, use **means** to define the named reusable operational behavior. state its required inputs, preconditions, operational contribution, returned results, observable effects, **and** failure results. modality, condition, temporal, quantification, logical, restriction, predicate, **and** comparison Operators **may** constrain that behavior.
2. for Workflow, use **means** to define the reusable graph through Step references, entry, typed transitions, result conditions, **and** terminal outcomes. use condition, temporal, logical, restriction, predicate, **and** comparison Operators **only** with explicit transition scope under CA-M-305-CORE_META_MODEL-METHOD--write-workflow-schemes-using-step-references.
3. for Step, define the invocation binding of **`=1`** referenced Action with its parameters **and** inputs. do **not** copy the Action behavior **or** define another Workflow.
4. for Actor, define participation, responsibility, capability, authorization, **or** prohibition using **must**, **may**, **must not**, **only**, conditions, **and** explicit boundaries as applicable. do **not** encode one particular execution as reusable Actor authority.

## Details

an Operations Claim **must not** combine more than one primary type profile. subordinate inputs, conditions, results, failures, transitions, **and** effects remain part of the selected type's single operational contribution.
