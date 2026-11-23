---
atom_family: SPEC
atom_id: AN-S-498
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-10-27 20:00:06 +0400
---
## Summary

Define Project.Framework Settings.Parameter Resolution

# Summary

Define Project.Framework Settings.Parameter Resolution

## Scope

resolution of one framework parameter from explicit Framework Settings or Default Settings.

## Claim

Parameter Resolution **means** selecting the effective framework parameter value from explicit Framework Settings **or** Default Settings under the parameter's governing rules.

## Details

Evidence: CA-M-279 defines the existing resolution method; CA-R-1402 and CA-R-1441 define its two configurations. Candidate #6 decisions 2 and 13 retain the governed setting and distinguish defaults from explicit selections. This definition adds no receipt, history-admission gate, stored result or fallback rule. Detailed precedence and invalid-value handling remain in the governing Method. The concrete ANECHOIC mechanism belongs in Project Configuration.
