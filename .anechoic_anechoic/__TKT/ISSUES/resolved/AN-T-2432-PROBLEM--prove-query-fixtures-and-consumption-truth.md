---
identity:
  atom_id: AN-T-2432
context:
  container:
    component: C16
  template: problem
state:
  status: resolved
  version: 3
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Prove query fixtures and consumption truth

## Concern

The Artifact golden corpus omits the same-spelling frontmatter/section namespace case; Journal token consumption reports UTF-8 bytes instead of parser tokens, and several required diagnostic/security fixtures are absent.

## Evidences

CA-P-1544 maps the missing cases to E569/E575/E577/E579. A three-token expression is reported as thirty bytes. CA-P-1546/1548 and the Journal repair own the bounded fixes; shared Run/E580 remains a separate integration gate.

## Blast radius

Resolved disposition: P1546/P1548 supplied namespace collision and actual parser consumption; P1545@3 repaired counts on rejected selectors. Independent P1547@3 accepts Artifact, Journal and the shared parser pure cores. No MCP/Run/image proof is implied.

Neither query Tool is admitted to MCP until its current repair and independent acceptance gates are satisfied. No source write, real Run, image or aggregate Epic completion is inferred from the initial passing unit suites.
