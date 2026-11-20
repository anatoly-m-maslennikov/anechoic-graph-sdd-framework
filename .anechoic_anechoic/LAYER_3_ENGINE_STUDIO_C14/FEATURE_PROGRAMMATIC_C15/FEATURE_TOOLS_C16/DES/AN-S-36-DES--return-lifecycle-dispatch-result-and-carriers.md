---
identity:
  atom_id: AN-S-36
context:
  container:
    component: C16
  tier: 3
  lens: DES
state:
  status: active
  version: 16
  updated_at: 2026-10-27 20:00:04 +0400
---
# Summary

Return lifecycle dispatch result and carriers

## Scope

The request/result and carrier handoff at the lifecycle dispatcher boundary.

## Claim

The dispatcher **must** return its typed lifecycle payload inside CA-D-527's one shared outer result. The payload contains request identity; the complete target or predecessor Carrier set and, for Replace, every accepted successor Carrier set; sealed expected and observed Carrier Version/digest metadata; selected operation; model/currentness resolution; authorization disposition; exact native result; diagnostics; changed/unchanged/unknown effects; and actual history/lineage references. A successful Replace names its predecessor and every successor Carrier. A Change Status names the prior and admitted resulting status; an Archive also names every newly broken Relation and active referrer with its separate repair handoff. A preview names no observed mutation.

The shared outer result owns disposition, actual Run IDs and definition bindings when started, actual terminal/partial outcome, and Journal append diagnostics when attempted. A lifecycle result marks a Carrier/effect `unknown` or `unverified` only when its mutation state is not observed; missing Journal state or an append failure is an independent diagnostic, does not invalidate an observed mutation, and never authorizes replay. An unstarted preview, decline, or block carries no invented Run/Event identity.

## Details

The shared Run receipt consumes this payload. This carrier contract creates no second Journal, Event schema, receipt, recording state, or retry mechanism.
