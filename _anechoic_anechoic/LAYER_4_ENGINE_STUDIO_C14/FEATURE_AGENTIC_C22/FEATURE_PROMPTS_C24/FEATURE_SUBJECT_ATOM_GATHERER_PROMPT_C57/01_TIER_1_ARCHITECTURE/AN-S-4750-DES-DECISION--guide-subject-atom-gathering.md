---
atom_family: SPEC
atom_id: AN-S-4750
container:
  component: C57
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4749@1
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Guide subject atom gathering

## Claim

### Prose Claim

The gatherer prompt is located in FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT, not a separate C57 directory. It instructs a read-only handoff and forbids rewriting Atoms or creating or updating Drafts.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT/subject_atom_gatherer.prompt.md`.
The authored rule models only the named condition. It does not prove that
an agent complied or that a tool call occurred.

```lean
namespace AgenticC57Rule

def admitted (inSelectedScope isRewriteTarget : Bool) : Bool := inSelectedScope && isRewriteTarget

theorem admitted_requires_condition (inSelectedScope isRewriteTarget : Bool)
    (h : admitted inSelectedScope isRewriteTarget = true) : inSelectedScope = true := by
  cases inSelectedScope <;> simp_all [admitted]

end AgenticC57Rule
```
