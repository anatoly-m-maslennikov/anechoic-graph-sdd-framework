---
atom_family: SPEC
atom_id: AN-S-1608
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 10:48:25 +0400
---
## Summary

Keep Project validation out of Journal admission

# Summary

Keep Project validation out of Journal admission

## Scope

Plain append/read of observable Project events.

## Claim

the Journal **must** preserve observable Project events independently of whether the recorded Project state conforms **to** Applicable Methodology.

- append **and** read supplied observations **without** a Journal validation layer, required historical chain, canonical receipt, digest check, deduplication, retry **or** recovery gate. prior records are **not** prerequisites for a new entry.
- Atom-ID grammar, filenames, placement, Properties, Relations **and** lifecycle conformance belong **to** separate Evaluations **and** their Tools; none is a Journal append/read gate.
- preserve supplied observed values **without** silently repairing them **or** inventing an earlier event, baseline, Actor, session, time **or** result. log entries do **not** prove Project conformance **or** correct execution.
- later Project changes **must not** prevent recording historical observations **or** rebind them **to** current state.
- each explicit append records its supplied data, including repeated data; do **not** suppress it as a duplicate **or** overwrite existing entries.
- retain ordinary authorized Project/filesystem access **and** truthful I/O failure. the Journal grants no permission **to** mutate a source, perform a Git effect **or** bypass access controls. existing records remain readable as recorded **without** migration.

## Details
