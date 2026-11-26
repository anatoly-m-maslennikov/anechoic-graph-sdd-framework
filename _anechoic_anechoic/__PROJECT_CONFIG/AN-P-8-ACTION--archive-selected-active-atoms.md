---
atom_family: PROJECT_CONFIG
atom_id: AN-P-8
structure:
  container:
    component: C18
context:
  template: action
state:
  status: "active"
  version: 24
  updated_at: "2026-11-25T22:24:06.688421+00:00"
---
# Summary

Archive selected active Atoms

## Operation

Archive Selected Active Atoms **means** the reusable Action that archives one explicit current logical Atom under its applicable lifecycle model, preserving its identity, Summary, content and recoverable history. This Atom lifecycle Action offers no Atom deletion; file cleanup is separately scoped.

### Action

1. bind the exact Atom ID and Version, owning Scope Unit, current Status and private source evidence. Resolve its applicable Content Role/Type archival transition and current permission under AN-S-1616 and the historical Role/Type rule AN-S-1590@27. Do not assume a universal Archived value or reinterpret resolved/canceled Concern states as archival meaning.
2. require one eligible current non-archived Atom and an explicitly allowed archival transition. Reject Draft, already archived, missing, ambiguous or stale targets, unavailable archival models and unsafe or occupied destinations before effects.
3. derive its private governed history destination under AN-S-3160, preserving ID, Summary, body and unrelated metadata. Preserve exact prior Version N bytes as history, and materialize the archival effect with Archived status, version-qualified identity `ID@N`, and predecessor Version N. Set Updated At to the time of the Status change; a real replacement update is separate, with its Active successor receiving Version N+1 and the actual Project-time Updated At. Never rewrite the preserved N predecessor.
4. execute only through the current admitted Project-local route with exact sealed permission and rechecked source/destination evidence. Safely perform and verify this one Atom's archival effect, retaining its actual result and independently retained Run/effect evidence; a Journal append remains a separate business-provenance attempt.
5. on failure recover only this Action's verified mutable frontier while preserving earlier successful Atoms and pre-existing history. Retain truthful failed/partial/unknown effects when independent Run/effect evidence is incomplete. A Journal append failure yields a `recording_error` diagnostic and does not downgrade an independently evidenced outcome or block dispatch, completion or recovery.
6. return the actual archived Atom ID and Version. In replacement 100 -> 200, archival targets and reports 100; it neither reports 200 as the archived target nor automatically changes references from 100 to 200.

For a folder-backed Plan, include its optional matching Directory Carrier in this one Atom's admitted placement map. Derive the Archived Carrier and its companion folder under AN-S-3160. Preserve the declared containment tree. The calling Workflow always composes the recursive Archive of all contained latest Atoms under CA-R-1521, including descendants already Done, without an optional descendant mode. Each selected Atom receives its own independently admitted Action under its qualified model and ordinary safeguards. Complete descendant Actions before a parent relocation would silently move an independent current child; this single-Atom Action neither selects descendants nor reports their changes complete. For a folder-backed Workflow or Step, derive the companion placement from its owning Atom. Retained-history subtrees and non-Atom assets may accompany the matching Directory Carrier byte-for-byte unchanged, without rewriting older Revision metadata or inventing asset Status. Do not independently flatten or rewrite noncanonical legacy `archive/` trees. Referenced Atoms outside containment remain untouched. No per-child human confirmation, optional mode or cross-Atom rollback is added.

### Batch and stop boundary

A requested batch is an ordered list of independently authorized Atom Actions. Invoke one Action at a time; advance to the next distinct explicit Atom only after confirmed success. On the first failure, stop, retain all earlier successful effects and their evidence, and leave the remaining targets untouched. Never roll back earlier successful Atoms to simulate a cross-Atom transaction. Validation, stale-source checks, permissions, safe effects and recovery within the failing Atom Action remain required. Automatic retry or resume of this new batch policy is deferred; existing recording-only recovery must not replay a performed Action.

An archive preview or no-op is not an invented effect. Historical references remain resolvable without an automatic reference rewrite.

## Details

Bind each actual standalone **or** nested Action Run **to** the shared every-Run contract in CA-P-1117 v3, Done CA-P-1443 J01–J08, independently reviewed by CA-P-1451: exact admitted definition Revision, actual Run identity/lineage, safe input/result/effect references, start, truthful terminal **or** still-pending interruption, **and** independently retained Run/effect evidence. Workflow-contained bindings also follow AN-S-1617; standalone coverage is the selected Epic obligation, **not** a broadened applicability claim for that Requirement. Reuse the shared recording capability **without** owning another Journal implementation. A Journal append remains a business-provenance attempt; its failure yields a `recording_error` diagnostic and is not proof, permission, completion or recovery gate. Preserve accepted events **and** pending evidence without waiting for Journal append success; a later explicit append records its supplied observation, may repeat an observation, and never replays a performed Action. No Journal append, intake acknowledgment, **or** Git Commit alone proves successful effects **or** complete Run recording.
