---
atom_family: SPEC
atom_id: AN-S-498
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 15
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Define Project.Framework Settings.Parameter Resolution

## Claim

### Prose Claim


resolution of an effective framework parameter.


Resolve each effective framework parameter from explicit Framework Settings or Default Settings under the applicable precedence. The result is derived; do not store it as a new Project.Settings Property.

## Details

Evidence: CA-M-279 defines the existing resolution method; CA-R-1402@27 and CA-R-1441 define its two configurations. Candidate #6 decisions 2 and 13 retain the governed setting and distinguish defaults from explicit selections. This definition adds no receipt, history-admission gate, stored result or fallback rule. Detailed precedence and invalid-value handling remain in the governing Method. The concrete ANECHOIC mechanism belongs in Project Configuration.
