---
atom_family: SPEC
atom_id: AN-S-39
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: active
  version: 34
  updated_at: 2026-10-27 20:00:11 +0400
---
## Summary

Gather provisional programmatic action context concurrently

# Gather provisional programmatic action context concurrently

COMMIT_CONTEXT **must** be independently invocable **and** strictly read-only. from **`=1`** durable trigger, it **must** gather provisional action context containing the sealed Initiative **and** action identity, observed repository frontier, affected subject identity, expected **and** observed Revisions **or** digests, candidate change, Git state, Journal state, **and** available provenance bindings.

- multiple context gatherers **may** work concurrently because their output is provisional **and** mutation-free. identical input **and** an unchanged observed frontier **must** produce the same context identity.
- context capture **must not** require the observed Project state **to** conform **to** Applicable Methodology. retain observable Carrier identity **and** evidence **when** Atom classification, names, properties, **or** relations are unresolved **or** invalid; do **not** invent a conforming identity **or** successful classification.
- no gathered context grants authority **to** mutate.
- a consumer changing governed Project state **or** Git state **must** revalidate its mutation preconditions against the current repository frontier, expected subject Revision **or** digest, **and** durable action state immediately **before** that effect.
- Journal admission follows CA-R-1491 instead: preserve intact sealed observations about the recorded event. subsequent Project changes alone **must not** prevent historical recording; altered **or** incomplete event envelopes remain storage-integrity failures.
