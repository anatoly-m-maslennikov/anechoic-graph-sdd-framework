---
atom_family: SPEC
atom_id: AN-S-1814
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Validate Tool Action bindings and Evaluation ownership

# Summary

Validate Tool Action bindings and Evaluation ownership

## Scope

a ANECHOIC Tool's methodology binding **and** Evaluation responsibility.

## Claim

the Evaluation of a ANECHOIC Tool's methodology binding **must** check the canonical Action owner, binding cardinality, **and** division of Evaluation responsibility under CA-R-1515-PROJECT_CONFIGURATION-GENERAL-REQUIREMENT--keep-canonical-actions-and-workflows-in-methodology, CA-R-1516-PROJECT_CONFIGURATION-REQUIREMENT--bind-each-tool-to-one-methodology-action, CA-R-1517-PROJECT_CONFIGURATION-REQUIREMENT--keep-tool-operational-authority-outside-its-own-subtree, **and** CA-R-1518-PROJECT_CONFIGURATION-GENERAL-REQUIREMENT--separate-methodology-and-tool-evaluation-responsibilities.

## Details

### Cases and expected results

- the Tool implements **`=1`** resolvable applicable Action owned by a methodology source outside the Tool's subtree: pass the binding check.
- the Tool has **`=0`** **or** **`>1`** implemented Action bindings, an unresolved definition, **or** a copied operational definition owned by the Tool: fail.
- an implementation reference targets an O Atom owned by the Tool's Scope Unit **or** a descendant: fail. a methodology Evaluation checking its own O definition **must not** fail this Tool-only containment rule.
- Tool Evaluations check the Tool's realization of its Action while methodology Evaluations check the operational definitions: pass the responsibility check.
- a Tool Evaluation independently owns Action **or** Workflow definition-validity rules: fail for misplaced authority; invoking an existing methodology check does **not** transfer that authority.
- a Workflow **contains** an unresolved Step Action **or** an unbounded retry loop: report the defect against the methodology definition through its methodology Evaluation, rather than silently repairing the Workflow inside the Tool's specification.

report binding conformance separately from actual Implementation results. valid ownership **and** references alone **must not** be reported as proof that the Tool works **or** that **all** indirect cycles are absent.
