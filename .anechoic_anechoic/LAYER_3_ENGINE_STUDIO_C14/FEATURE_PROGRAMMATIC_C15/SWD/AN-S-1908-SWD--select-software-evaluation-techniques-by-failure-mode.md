---
identity:
  atom_id: AN-S-1908
context:
  container:
    component: C15
  tier: 4
  lens: SWD
state:
  status: active
  version: 16
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Select software Evaluation techniques by failure mode

## Claim

### Prose Claim

**to** select behavioral software Evaluation techniques for a PROGRAMMATIC component, the Actor selecting the portfolio **must** take the applicable Spec, declared failure predicates, **and** active Evaluation authority as inputs; identify candidate checks for **every** predicate; evaluate candidate portfolios against the applicable Core **and** General Evaluation policy **and** each selected technique's own acceptance **and** disposition rules; select one admitted portfolio; repeat **until** all predicates are covered **or** no candidate remains; produce the selected Evaluation identities **and** selection rationale; **and** return unresolved predicates for authority **or** design clarification **when** no portfolio is admitted.

Before coding or selecting a check, identify the relevant state transitions, side effects and failure boundaries for the declared behavior, then choose Evaluation cases that can distinguish them.

## Details

### Scope

selection of behavioral software Evaluation techniques for PROGRAMMATIC components.


1. enumerate the failure predicates established by applicable authority **and** bind each predicate **to** the observable behavior that can distinguish acceptance from rejection. Include the applicable state transitions, side effects and failure boundary in that predicate description.
2. identify applicable Evaluation Atoms across test scopes, purposes, boundary-realism choices, execution environments, **and** release stages **without** treating those labels as a universal ranking.
3. construct candidate portfolios from those Evaluation Atoms. include a specialized technique **only when** its Evaluation applicability **and** evidence preconditions are satisfied.
4. evaluate **every** candidate portfolio under the Core evidence invariant in CA-E-637, the General portfolio criteria in CA-E-389, **and** the acceptance **and** disposition rules of **every** selected Evaluation Atom. apply the canary safety and evaluation criteria in CA-E-536 **when** a candidate includes canary evidence. A focused pass cannot overrule a failure in the combined suite; retain a regression check for each confirmed fixed failure class.
5. stop with one traceable admitted portfolio **when** all predicates are covered. **when** no candidate passes, return the uncovered predicates, failed policy conditions, **and** missing evidence rather than inventing a test-count ratio **or** silently accepting incomplete coverage.

### Sources

- [CA-E-389-PROGRAMMATIC-POLICY--combine-complementary-software-behavior-evidence](../06_evaluation/CA-E-389-PROGRAMMATIC-POLICY--combine-complementary-software-behavior-evidence.md)
- [CA-E-536-PROGRAMMATIC-POLICY--admit-safe-canary-evaluation](../06_evaluation/CA-E-536-PROGRAMMATIC-POLICY--admit-safe-canary-evaluation.md)
- [CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)

- [CA-E-637 — Require observable evidence for behavioral acceptance](../06_evaluation/CA-E-637-PROGRAMMATIC-POLICY--require-observable-evidence-for-behavioral-acceptance.md)

### Public interface tests

For an isolated failure predicate, select the least costly stable observable boundary supported by evidence. Prefer end-to-end tests through real browser, MCP and HTTP interfaces for critical public journeys, integration or emergent failures that narrower checks cannot expose. For applicable public-interface behavior, assert user-visible results rather than private classes, constructor arguments, call counts or internal call order. For internal behavior, observable domain state and effects are also valid outcomes when they distinguish the applicable failure predicates. Remove unit tests that merely mirror implementation or add no distinct failure evidence. Keep focused tests for behavior that the end-to-end tests do not cover.
