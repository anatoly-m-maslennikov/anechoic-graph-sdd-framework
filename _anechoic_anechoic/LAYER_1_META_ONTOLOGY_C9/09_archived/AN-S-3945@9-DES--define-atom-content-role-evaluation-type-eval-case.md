---
atom_family: SPEC
atom_id: AN-S-3945
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-10-29 09:34:45 +0400
---
## Summary

Define Atom/Content Role: Evaluation/Type: Eval Case

## Claim scope

The Eval Case value in the qualified Evaluation Type domain.

## Claim

Eval Case **means** a specified evaluation instance that identifies the subject and evidence to assess, the applicable acceptance condition, and the expected result or decision criterion.

An Eval Case owns at least one evaluation_for relation to the Current Requirement, Method, Evaluation, Delivery or Operations Atom whose authority it checks. Target authority ordering follows the governing Tier and Scope constraints; evaluation evidence is not the checked authority itself.

## Details

An Eval Case may be realized through deterministic tests, LLM prompts, or other suitable evaluation mechanisms. It does not require a one-to-one mapping to any test or prompt, and it does not constrain an Atom to a particular tier.
