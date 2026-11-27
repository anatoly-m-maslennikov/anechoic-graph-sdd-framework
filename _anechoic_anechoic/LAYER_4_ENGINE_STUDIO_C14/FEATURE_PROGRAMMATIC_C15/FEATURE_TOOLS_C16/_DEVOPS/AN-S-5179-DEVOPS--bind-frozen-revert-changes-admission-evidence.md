---
atom_family: SPEC
atom_id: AN-S-5179
container:
  component: C16
tier: 4
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-27T17:35:02.229098+00:00'
---

## Summary

Bind frozen REVERT_CHANGES admission evidence

## Claim

For admission, every frozen evidence reference uses one `evidence_pin`:
`{ evidence_ref, evidence_hash }`. `evidence_ref` is either an existing
canonical Journal Event reference `event:<event_id>` or a safe
Project-relative declared-carrier/member reference; it is not a URL, code,
resolver, symlink, traversal path, `.git`, or secret file. `evidence_hash` is
the SHA-256 of canonical Journal Event bytes for `event:<event_id>`, or of the
referenced member's raw bytes. The bounded reader resolves only configured
Project authority/evidence roots and rejects unsafe, missing, ambiguous,
oversized, changed, or unresolvable references; it creates no authority or
Journal and synthesizes no evidence.

`reversal_request` carries exact pins for `selected_change`, each retained
`history_record`, `before_record`, `after_record`, and each
`affected_reference`. `governing_definition` additionally carries
`{ atom_id, revision, evidence_ref, evidence_hash }`; `operator_decision` and
`executor_permission` carry `{ evidence_ref, evidence_hash }` with their
existing decision/capability fields. Operator-decision evidence records the
current Operator's exact ordered approved effects; executor-permission evidence
records the supported capability and current grant. Existing
`capability_permission` evidence remains separately required. Any changed,
revoked, missing, unsafe, unsupported, or hash-mismatched pin is a precise
pre-effect blocker; no ID, status, or hash-shaped value permits inference.
