---
atom_family: SPEC
atom_id: AN-S-1902
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: "active"
  version: 19
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---

## Summary

Emit structured operational diagnostics

## Claim

### Prose Claim

emit structured operational diagnostics for PROGRAMMATIC work under the active
Logging Policy **in** `ANECHOIC-GOV-REQU-315`, including its ERROR, WARNING, INFO,
**and** DEBUG meanings. this Method applies that authority **to** PROGRAMMATIC
diagnosis; it does **not** own the level vocabulary, level meanings, **or** Journal
meaning.

## Details


### Applicable when

apply **when** a Tool, App backend service, **or** MCP component reports normal
operation, degraded operation, failure, recovery, **or** diagnostic detail.

### Procedure

1. Apply AN-S-1252 and CA-M-396 for diagnostic severity and request errors.
   Preserve partial results under CA-M-405 and business recording under CA-M-399.
2. emit records through one project-owned logging abstraction **and** schema.
   include timestamp, level, component, operation, outcome, **and** the canonical
   action **or** event identity **when** one exists.
3. include actionable, contextual, sanitized fields **and** keep DEBUG bounded **to**
   diagnosable need.
4. Apply AN-S-4741 to Studio stream routing, logging configuration, and
   Docker retention. For Project-bound records, use the validated prefix from
   the selected Project. For unbound records, keep the host context and omit
   the Project prefix. Apply AN-S-2325 to business Journal events.
5. declare retention, loss, **and** back-pressure behavior at those bounded
   materialization **and** operational boundaries.
6. make logging failure observable **without** silently breaking primary work.

#### Bounded-scan warnings

When a bounded scan isolates a schema-invalid Atom and continues with a warning,
emit a structured warning through the diagnostic stream configured above with the
validated Project prefix, repository-relative path, and reason, and preserve the
incomplete result (`complete: false`) in the operation response.

### Outcome

Operators can diagnose component behavior **without** exposing secrets, confusing
operational diagnostics with governed Journal history, **or** relying on an
undeclared sink behavior.

### Failure or stop

stop emission **or** release of the affected diagnostic path **when** required context
cannot be sanitized, a logging failure is hidden, **or** the component would use
the Journal as a substitute logging sink.

### Sources

- [Python Logging HOWTO](https://docs.python.org/3.14/howto/logging.html)
- [Python Logging Cookbook](https://docs.python.org/3.14/howto/logging-cookbook.html)
- [OpenTelemetry: logs](https://opentelemetry.io/docs/concepts/signals/logs/)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
