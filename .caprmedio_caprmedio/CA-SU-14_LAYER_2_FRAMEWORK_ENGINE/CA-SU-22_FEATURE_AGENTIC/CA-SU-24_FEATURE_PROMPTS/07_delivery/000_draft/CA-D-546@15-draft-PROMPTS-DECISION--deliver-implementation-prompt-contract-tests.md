---
atom_id: CA-D-546
ref_id: CA-D-546@15-draft
container:
  scope_unit: CA-SU-24
role: Delivery
form: Decision
topics:
  main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Quality
    <+ Verification <+ Test Design
  dependencies:
  - PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Development <+ Authoring
    <+ Prompt Authoring
  - MODEL//CAPRMEDIO <+ Atom/(.Header.Context.Role := Evaluation)
  - MODEL//CAPRMEDIO <+ Carrier
tier: 3
status: draft
version: 15
updated_at: '2026-11-14T08:20:21.428519+00:00'
carrier_destination:
  file:
    name: CA-D-546@15-draft-PROMPTS-DECISION--deliver-implementation-prompt-contract-tests.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-22_FEATURE_AGENTIC/CA-SU-24_FEATURE_PROMPTS/07_delivery/000_draft
current_scope_unit: PROMPTS
claim_target_scope_unit: PROMPTS
author: Anatoly Maslennikov
relations:
  IS_REPLACEMENT_FOR:
  - CA-D-546
---
## Summary

Deliver implementation prompt contract tests

## Claim

### Prose Claim

Cover the Implementation Workflow prompt contract with static and mock E2E
tests. Check source freshness, coverage of shared-context prompt carriers,
and exact Action, context, and result labels.

## Details

- Check R/D, M, and E packet separation, golden E2E preparation, handoff
  boundaries, and truthful retry and repair results.
- Use these tests as evidence of prompt conformance only. Live LLM execution,
  implementation completion, Docker coverage, and MCP delivery need other evidence.
