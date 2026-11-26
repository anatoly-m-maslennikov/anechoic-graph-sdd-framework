---
atom_family: SPEC
atom_id: AN-S-1805
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: active
  version: 21
  updated_at: '2026-11-25T20:40:58.851983+00:00'
---
## Summary

Author FPF Analysis Reports

## Claim

### Prose Claim


authoring and content-preserving import of FPF Analysis Report Atoms.


Use the native `analysis_report` Ticket Asset Template for a new report. Preserve the bounded question, scope, approach, results, provenance, and evidence limits. A recommendation needs its own Spec to become an accepted decision.

For a legacy Analysis & Advisory carrier, apply CA-D-479. Apply the following preservation rules to an imported report according to its carrier format.

- On a legacy carrier, retain `role: "Analysis & Advisory"`, `form: FPF Analysis Report`, the actual owning Scope Unit, applicable tier, Status and Version. Summary describes the Question; TLDR summarizes the retained analytical record without replacing Results.
- **when** importing an existing report, preserve its complete original UTF-8 text as quoted Markdown in Results. Quotation is a carrier wrapper, not an edit to the original text. Record its original path, SHA-256 and byte length in Approach so the original bytes can be recovered and checked.
- identify the original inquiry from its explicit task or question where available; otherwise identify the bounded historical report without inventing a missing execution contract. Preserve all native findings, alternatives, citations, limitations and time-relative statements in the quoted record.
- distinguish import metadata and its current Revision timestamp from the original report's provenance. Do not infer an original execution timestamp or completed FPF Run merely from a filename or physical file existence.
- Place a native report under AN-S-3160. For a legacy report, use its applicable Analysis & Advisory placement. Resolve real destination links to the new Carrier while retaining historical Journal, archive and frozen-evidence references unchanged.

## Details

Importing a report does not rerun FPF, adopt a candidate, change project policy or close an issue. Completion of the bounded imported reporting product is distinct from those outcomes.

