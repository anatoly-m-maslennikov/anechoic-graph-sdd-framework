---
atom_family: SPEC
atom_id: AN-S-4743
container:
  component: C74
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3394
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T00:00:00+00:00'
---
## Summary

Compare a bounded carrier model

## Guarantee

For the selected carrier pilot, derive a Lean model from the admitted Python source and compare observed cases with the supplied formal Contract and Draft Solution. Retain source evidence and report unresolved coverage or execution failures. With `--formal-only`, compare the authored Contract and Solution on selected cases without implementation evidence. This pilot does not compile arbitrary Python Specs to Lean.

## Claim

### Prose Claim

For a completed selected carrier comparison, the admitted Python source is used to build the bounded model, source evidence is retained, and the selected observations are compared with the supplied formal claims. Failed execution, an unavailable Lean executable, or a failed comparison is unresolved. This claim does not establish coverage beyond the selected cases.

`formal_compared` is the modeled outcome for `no_mismatch_in_cases` in formal-only mode. It covers only the authored formal cases. It does not establish implementation conformance. Manifest comparison and unmodeled behavior remain unresolved.

### Formal Claim

```python cli
declare_cli_contract(
    interface='carrier_compare',
    action='carrier_compare',
    runner='managed_python',
    module='ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare',
    arguments=('--root <project-root>', '[--lean <executable>]', '[--formal-only]'),
    output='compared',
    must_effect=(('carrier_model', 'built'), ('source_evidence', 'retained'), ('selected_cases', 'compared')),
)
```

```python trace
declare_trace_contract(
    action='carrier_compare_formal_only',
    output='formal_compared',
    must_effect=(('formal_cases', 'compared'),),
    forbid_effect=('carrier_model', 'source_evidence'),
)
```

```python trace
declare_trace_contract(
    action='carrier_compare_formal_only',
    output='unresolved',
    must_effect=(('coverage', 'unresolved'),),
)
```
