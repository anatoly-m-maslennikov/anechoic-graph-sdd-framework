---
atom_family: SPEC
atom_id: AN-S-4746
container:
  component: C54
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4745@1
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Guide atom authoring

## Claim

### Prose Claim

The prompt instructs the agent to preserve meaning and applicability, derive Summary last, use the lifecycle result, and report unresolved uncertainty. Missing necessary input for a new Atom is a question to the Actor.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_ATOM_AUTHORING_PROMPT/atom_authoring.prompt.md`.
The authored rule models only the named condition. It does not prove that
an agent complied or that a tool call occurred.

```lean
namespace AgenticC54Rule

def admitted (gatePassed draftCall : Bool) : Bool := gatePassed && draftCall

theorem admitted_requires_condition (gatePassed draftCall : Bool)
    (h : admitted gatePassed draftCall = true) : gatePassed = true := by
  cases gatePassed <;> simp_all [admitted]

end AgenticC54Rule
```
