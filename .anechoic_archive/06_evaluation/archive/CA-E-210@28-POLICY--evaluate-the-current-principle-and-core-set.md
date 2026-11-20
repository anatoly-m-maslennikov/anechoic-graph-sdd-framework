---
version: 28
updated_at: 2026-10-27 19:59:30 +0400
relations:
  child_of:
  - CA-M-001
  - CA-M-002
  - CA-E-001
cce_version: cce_1
cce_form: evaluation
subjects:
  governs: Subject/ANECHOIC/Graph/Node/Project Model/Project.Principle Universe
  depends_on:
  - Subject/ANECHOIC/Graph/Node/Project Model/Project
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom.Tier
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: Operator'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom.Content
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Evaluation'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Plan'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Requirement'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Method'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Delivery'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations'
  - Subject/ANECHOIC/Graph/Node/Project Model/Actor
llm_session_ids:
- codex:01a02650-eff7-7453-8c37-0699b36773c6
atom_id: CA-E-210@28
status: Archived
content_role: Evaluation
author: Anatoly Maslennikov
current_scope_unit: anechoic
type: Policy
tier: 1
---
# Evaluate the current Principle and Core set

the Principle **and** Core set Evaluation **must** return `fail` **if** a known Project-wide invariant has no canonical owner, a Principle is **only** a narrow application rather than a broad commitment, a required supporting Core Claim is absent, Claims conflict **or** independently duplicate authority **in** the same context, **or** an Atom has an incompatible Local Tier **or** Content Role; **otherwise**, it **may** return `pass` for the reviewed frontier **without** claiming that undiscovered gaps are impossible. evaluate Principle Content Roles under CA-E-482; the former Actor-policy interpretation of Plan does **not** create an exception **to** current Content Role authority. faithful Core specialization **must not** count as duplicate authority; fixed child counts, a universal RMED checklist per Principle, expansion from Intent, **and** formula/text equivalence **must not** be acceptance conditions. report missing support **and** conflicting owners **to** the Operator **without** silently selecting a winner.
