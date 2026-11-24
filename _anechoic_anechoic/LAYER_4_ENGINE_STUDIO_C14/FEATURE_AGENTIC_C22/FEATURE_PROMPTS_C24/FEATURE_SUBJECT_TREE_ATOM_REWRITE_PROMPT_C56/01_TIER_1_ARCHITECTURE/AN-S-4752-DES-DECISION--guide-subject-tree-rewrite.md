---
atom_family: SPEC
atom_id: AN-S-4752
container:
  component: C56
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4751@1
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Guide subject tree rewrite

## Claim

### Prose Claim

The prompt calls for parent-first processing, quark classification, source comparison, and source-to-Draft mapping. It instructs MCP Draft writes and verification, without itself performing them.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT/subject_tree_atom_rewrite.prompt.md`.
The authored rule models only the named condition. It does not prove that
an agent complied or that a tool call occurred.

```lean
namespace AgenticC56Rule

def admitted (sourcesCompared verifiedDraft : Bool) : Bool := sourcesCompared && verifiedDraft

theorem admitted_requires_condition (sourcesCompared verifiedDraft : Bool)
    (h : admitted sourcesCompared verifiedDraft = true) : sourcesCompared = true := by
  cases sourcesCompared <;> simp_all [admitted]

end AgenticC56Rule
```
