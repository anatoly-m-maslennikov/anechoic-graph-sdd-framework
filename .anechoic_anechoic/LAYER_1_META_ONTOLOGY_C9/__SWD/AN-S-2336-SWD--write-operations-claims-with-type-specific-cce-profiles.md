---
atom_family: SPEC
atom_id: AN-S-2336
structure:
  container:
    component: C9
  tier: 6
context:
  lens: SWD
state:
  status: active
  version: 27
  updated_at: 2026-11-11 14:09:10 +0400
---

## Summary

Write Operations Claims with Type-specific CCE Profiles

## Claim

### Prose Claim

Operations Claims written with Action, Workflow, and Step CCE Profiles when their primary Form is Action, Workflow, or Step.

**to** write an Operations Claim whose primary Form is Action, Workflow, or Step, the Author **must** first resolve that Form **and** then apply **`=1`** primary Form profile:

1. for Action, use **means** to define the named reusable operational behavior. state its required inputs, preconditions, operational contribution, returned results, observable effects, **and** failure results. modality, condition, temporal, quantification, logical, restriction, predicate, **and** comparison Operators **may** constrain that behavior.
2. for Workflow, use **means** to define the reusable graph through Step references, entry, typed transitions, result conditions, **and** terminal outcomes. use condition, temporal, logical, restriction, predicate, **and** comparison Operators **only** with explicit transition scope under CA-M-305-CORE_META_MODEL-METHOD--write-workflow-schemes-using-step-references.
3. for Step, define the invocation binding of **`=1`** referenced Action or Workflow with its parameters **and** inputs. Reference the called definition without copying its behavior.

For an Operations Scope Delegation, Solution, Direct Policy, Approach Policy, or Decision whose actual primary contribution matches Operations semantics, write the Claim under that Form's admitted semantics. Do **not** apply an Action, Workflow, or Step profile merely because the Role is Operations. Those Forms create no executable binding.

## Details

an Operations Claim whose primary Form is Action, Workflow, or Step **must not** combine more than one primary Form profile. subordinate inputs, conditions, results, failures, transitions, **and** effects remain part of the selected Form's single operational contribution.
