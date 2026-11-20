---
identity:
  atom_id: AN-S-1085
context:
  container:
    component: C00
  tier: 5
  lens: QA
state:
  status: active
  version: 27
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Evaluate Operator control of AI permissions

## Claim

### Prose Claim


the Operator can create, inspect, limit, modify, suspend, **and** revoke AI Agent Delegations **and** mandatory authorization rules for identified AI Agents.

## Applicable conditions

apply **to** **every** supported delegation **or** mandatory-authorization-rule Carrier **and** **after** a material change **to** their governance **or** Implementation.

## Check

for one identified AI Agent, exercise creation, inspection, limitation, modification, suspension, **and** revocation on one test AI Agent Delegation **and** one test mandatory authorization rule through Operator-controlled paths. **after** **every** operation, inspect the effective state of the affected delegation **or** rule **and** verify that it matches the Operator action. check **every** applicable control operation for the test delegation **and** the test authorization rule; successful delegation control **must not** substitute for authorization-rule control.

## Acceptance

pass **only** **when** **every** required operation for delegations **and** mandatory authorization rules is available **to** the authorized Operator **and** produces the inspected effective state requested by that Operator.

## Failure

fail **and** report **every** unavailable operation, unauthorized state change, **or** mismatch between requested **and** effective delegation **or** authorization-rule state.
