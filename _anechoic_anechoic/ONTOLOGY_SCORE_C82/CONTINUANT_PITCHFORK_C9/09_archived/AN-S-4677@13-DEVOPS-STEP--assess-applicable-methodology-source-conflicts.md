---
atom_family: SPEC
atom_id: AN-S-4677
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 13
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Assess Applicable Methodology source conflicts

# Summary

Assess Applicable Methodology source conflicts

## Operation

this Step is the assess node **of** CA-O-011, Applicable Methodology Compilation, invoking **`=1`** Action, CA-O-005, Assess Source Conflicts.

### Inputs and parameters

bind the exact selected source frontier returned by CA-O-152 and the Workflow Run's applicable Core expansion-boundary and conflict authority.

check Core expansion-boundary conformance under CA-R-1375 **and** the applicable conflict authority, including CA-R-1373; detect **every** boundary violation, duplicate selected Atom identity, unresolved replacement, incompatible retained Candidate, **and** unresolved priority. retain conflicting source Atoms rather than silently discarding them. calculate one deterministic digest of the exact selected frontier **and** report the complete deterministic conflict set **before** changing Applicable Methodology membership.

### Agentic invocation binding

for an invocation whose actual bound Action is Agentic, bind **`=1`** Integrated **or** Isolated context under CA-R-1527 from the admitted invocation's supplied `agentic_execution_context` runtime parameter **before** dispatch. missing, ambiguous **or** unsupported values, **or** unavailable required context/capability, block that Agentic invocation; do **not** default **or** silently substitute. retain the selected context with the Step Run. a Programmatic invocation does **not** acquire an Agent context **or** require this parameter. this binding grants no additional authority **and** does **not** change the Action's identity **or** behavior.

## Details
