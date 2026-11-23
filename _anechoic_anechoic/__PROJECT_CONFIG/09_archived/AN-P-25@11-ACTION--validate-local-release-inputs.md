---
atom_family: PROJECT_CONFIG
atom_id: AN-P-25
structure:
  container:
    component: C00
context:
  template: action
state:
  status: archived
  version: 11
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Validate local release inputs

# Summary

Validate local release inputs

## Action

Validate local release inputs **means** the Action that checks the explicit local-release inputs and configured delivery paths for file/path safety before the declared local validation scope. The complete discovered suite remains the default; a focused scope requires the explicit current Operator record admitted by CA-O-164.

## Scope

The Action checks the configured source and delivery paths, Project Structure, protected settings, compiler, and target paths `101_FRAMEWORK_METHODOLOGY/` and `.anechoic_anechoic/000_ANECHOIC_framework/` for ordinary input and file/path safety. It does not separately validate Active Atom metadata, placement or relations; release verification uses the declared scope and records whether it is complete or focused.

## Details

Missing, ambiguous or unsafe required input stops before tests or delivery writes and is reported for manual handling. This Action does not copy or clear product or installed contents, compile, install, push, or open a PR.
