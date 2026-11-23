---
atom_family: SPEC
atom_id: AN-S-1823
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: 2026-09-28 16:14:59 +0400
---
## Summary

Store one review report per source Atom

# Summary

Store one review report per source Atom

## Scope

temporary evidence Carriers of a batched RMED Atom review Run.

## Claim

the Run **must** store its temporary evidence under **=1** caller-admitted Run directory using this layout:

- `manifest.json`: Run identity, complete requested selection, selected batch **and** deferred members, source identity/Revision/path/SHA-256 bindings, effective limits **and** their provenance, estimated work, authority bindings, permissions, confidence **and** retry policy.
- `reports/<ordinal>.json`: **=1** report for **every** selected source Carrier, using its fixed four-digit batch ordinal rather than an untrusted filename **or** a possibly invalid Atom ID.
- `mechanical/`: unchanged mechanical checker requests **and** raw results referenced by the reports.

**every** report **must** contain `schema_version`, `run_id`, `ordinal`, the original `source` binding, `evaluations`, `repairs`, `current_sources`, **and** `state`. **every** evaluation records its own source binding, authority bindings, **all** CA-E-520 check results, evidence, findings **and** proposed fixes, missing coverage, mechanical evidence, **and** overall result. findings identify the affected section **or** Property, an exact excerpt **or** observed absence, the checked authority, **and** concise reasoning. **every** repair records the exact input/output bindings, changed paths, disposition, **and** verification references.

keep initial evaluations **and** later attempts **in** the same report; do **not** overwrite earlier evidence with a final pass. include passed **and** blocked Atoms, **not only** failed Atoms. report states are `evaluated`, `unchanged`, `verified`, **or** `blocked`; a verified state requires a current passing evaluation of **every** resulting source **and** completed affected-reference checks. these files are derived temporary evidence, **not** Atom authority **or** a substitute for required durable history.

## Details

a missing **or** ambiguous Atom ID is represented explicitly, **not** invented. source path **and** digest still identify the inspected Carrier. replacements **or** splits retain their predecessor/successor mapping **in** the original report. a report's apparent pass becomes stale **when** a bound source **or** applicable authority changes. **every** evaluation also carries `context_sha256` binding its complete review-input snapshot **and** `parts` retaining the raw CCE, Properties, **and** coherence records. **every** part identifies its `evaluator`, the same source **and** context bindings, **and** its assigned results. the combined `checks` contains **every** required check exactly once; `coverage_gaps` retains **all** unresolved evidence **without** averaging part outcomes.
