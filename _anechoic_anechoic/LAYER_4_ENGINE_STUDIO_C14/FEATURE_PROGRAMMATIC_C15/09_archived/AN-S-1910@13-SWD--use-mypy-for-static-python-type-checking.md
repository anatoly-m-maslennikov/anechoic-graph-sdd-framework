---
atom_family: SPEC
atom_id: AN-S-1910
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 13
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Use Mypy for static Python type checking

## Claim

### Prose Claim

use Mypy as the selected static type checker for hand-authored PROGRAMMATIC
Python source. CA-E-540 owns strict-profile, baseline, **and** suppression
acceptance policy.

## Details

Candidate source: [CA-M-283@9](archive/CA-M-283-PROGRAMMATIC-CORE-METHOD--use-mypy-for-static-python-type-checking@9.md)

### Applicable when

apply **to** new **or** materially changed Python source within Tools, App, **or** MCP.

### Procedure

1. materialize one pinned Mypy profile **and** bounded target set **in**
   `pyproject.toml`.
2. run Mypy through the selected uv workflow.
3. provide the current diagnostics **and** recorded baseline **to** CA-E-540.
4. bind suppression rationale **to** the affected line **or** symbol for evaluation
   under CA-E-540.
5. keep static typing evidence distinct from runtime validation **and** behavioral
   evidence.

### Outcome

changed Python interfaces become more explicit **without** making untyped legacy
source an unrelated whole-project blocker.

### Failure or stop

return unavailable configuration **when** the profile **or** target set is absent.
typing acceptance, baseline regression, **and** suppression disposition follow
CA-E-540.

### Sources

- [Mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [Mypy: using Mypy with an existing codebase](https://mypy.readthedocs.io/en/stable/existing_code.html)
- [Mypy: strict mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
