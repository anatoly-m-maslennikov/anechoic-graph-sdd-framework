---
identity:
  atom_id: AN-S-2256
context:
  container:
    component: C15
  tier: 2
  lens: SWD
state:
  status: "active"
  version: 2
  updated_at: "2026-11-20T14:16:10.334733+00:00"
---
## Summary

Store RMEDO pins in Markdown spec references

## Claim scope

Authoring implementation trace and package policy records in PROGRAMMATIC.

## Claim

### Prose Claim

Store Module pins in `<full module filename with extension>.spec_trace.md` beside the Module, including the Module’s original extension. Store Package pins in `<folder name>__spec_bind.yaml` at the Package root. Use the full Module filename or Package folder name to identify the owner. Standalone CI/CD workflow files that implement Delivery behavior count as Modules for tracing. Assets and individual golden corpus files are outside the trace scope. If a golden corpus itself realizes an Evaluation Claim, record the pin once in the owning evaluation Package’s spec trace.

Record what the Module or Package implements or follows today. In a Module sidecar, use a Markdown list under `## Implements`. In a Package Spec Binding file, use YAML lists under `implements` and `applies`. Each entry contains one exact Atom ID and Version.

- Put Solutions in the owning Package’s `implements` list when the Package directly implements them.
- Put Engineering Standards that the Package follows in its current implementation in its `applies` list.
- Put Decisions, individual Requirements, and Test or Evaluation Cases in the Implements section of the Module that directly implements them. Apply the same ownership rule to other Claims.

Keep pins for all cited versions, including non-Current versions. Archiving an Atom or publishing a newer version leaves the sidecar unchanged. Update the pin explicitly when the implemented or applied Claim changes.

Omit empty lists and empty sidecars. Record a package entry once. Build descendant rollups from the sidecars.

## Details

For example, `query.py` and a sibling `query/` Package use `query.py.spec_trace.md` and `query/query__spec_bind.yaml`. A CI/CD workflow at `.github/workflows/publish-release.yml` uses `.github/workflows/publish-release.yml.spec_trace.md` for the Delivery Claims it implements. The Package reference can contain:

```yaml
implements:
  - CA-M-123@4
applies:
  - CA-M-456@2
```