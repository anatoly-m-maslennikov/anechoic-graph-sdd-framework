---
atom_family: SPEC
atom_id: AN-S-3729
container:
  component: C21
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Derive exact acceptance-carrier relocation admission

# Summary

Derive exact acceptance-carrier relocation admission

## Scope

the one registered relocation of three acceptance carriers under the current Epic.

## Claim

**to** admit the exact acceptance-carrier relocations, derive one candidate from the current binding and the closed CA-D-592-MCP-DELIVERY--register-exact-acceptance-carrier-relocations registration before applying the existing authorized publication lifecycle.

## Details

1. reopen CA-D-592-MCP-DELIVERY--register-exact-acceptance-carrier-relocations, its exact canonical input bytes and the three retained current source carriers; require each current carrier's bytes, identity, version and digest to match its registration.
2. replace only the three registered source-path occurrences from the listed prior path to the listed current path. retain every other manifest field, route, graph, registry pin and source digest unchanged except the resulting canonical serialization and its derived `canonical_manifest_sha256`; the route-identical `selected_binding_digest` remains unchanged.
3. validate the whole candidate against current source pins and the existing selected-route schema. reject any changed topology, alias, unregistered path or mismatched occurrence before intent.
4. seal and publish only through the existing typed Operator context, lock, pending intent, rederivation and atomic readback lifecycle; record the actual result through the existing Work Journal.
5. retain pending publication or recording evidence for recovery. when the exact registered original input, sealed intent and current sources still match, an interrupted pre-effect attempt may retry the same candidate once under the existing lock. once that exact candidate exists, recovery is recording-only and performs no rewrite; ambiguous bytes refuse. historical evidence and installed runtime remain unchanged.
