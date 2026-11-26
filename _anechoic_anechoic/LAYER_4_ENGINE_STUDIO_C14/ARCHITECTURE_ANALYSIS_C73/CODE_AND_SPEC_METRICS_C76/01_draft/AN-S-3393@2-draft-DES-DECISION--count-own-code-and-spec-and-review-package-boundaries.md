---
atom_family: SPEC
atom_id: AN-S-3393
container:
  component: C76
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3397@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:55:48.664879+00:00'
---
## Summary

Count own code and Spec and review Package boundaries

## Claim

### Prose Claim

Count authored implementation and declared Test Package code separately. Report test assets separately. Binary assets contribute bytes only. Use the Realization Graph inventory and its generated-file, dependency, and Test Package classifications. Report unclassified files separately.

Attribute implementation files to their nearest Package. A Package's own implementation excludes files in descendant Packages. A test belongs to a Package only through a Test Package relation to that Package, regardless of where the test lives. Component totals include their directly owned implementation and tests, including tests linked to their Packages. Count each file once per total. Keep Component-wide tests at Component scope.

Use the admitted Current Spec inventory under the AN-S-3390 ownership rule. For a Package ratio, count whole Spec carriers with an explicit binding to that Package or its own files. Count shared carriers at Component scope and flag the affected Package ratios as partial. Show Packages without an explicit Spec binding as unbound.

Report six code-to-Spec ratios by bytes and by physical lines, including blank lines. Use implementation, test code, and their sum as numerators. Use the full Markdown carrier and the body after the YAML frontmatter as denominators. Expose exact bytes and display decimal kB or MB. Use an empty ratio for a zero denominator.

Report each Package's own implementation bytes, lines, file count, and largest files. Show distinct resolved incoming and outgoing Package dependencies and the contributing imports from AN-S-3351. Use size outliers to select review candidates. Calibrate the size signals from the Studio baseline.

Recommend a split when a separable responsibility can hide its decisions behind a small interface without adding cycles or excessive coupling. Check whether the proposed parts tend to change independently when useful Git history is available. Review a large file that serves one responsibility for an internal module split.

### Formal Claim

```python
component_workflow(
    component='C76',
    action='report_code_and_spec_metrics',
    machine={
        'id': 'c76_code_and_spec_metrics',
        'initial': 'capturing',
        'states': {
            'capturing': {'on': {
                'inventory_captured': {'target': 'admitting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'code_inventory', 'outcome': 'captured'}}},
            }},
            'admitting': {'on': {
                'current_spec_admitted': {'target': 'binding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'current_spec', 'outcome': 'admitted'}}},
            }},
            'binding': {'on': {
                'file_and_spec_bindings_identified': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'file_and_spec_bindings', 'outcome': 'identified'}}},
            }},
            'reporting': {'on': {
                'report_returned': {'target': 'returned', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'report_returned'}}},
            }},
            'returned': {'type': 'final'},
        },
    },
)
```

## Coverage and limits

The trace requires captured code inventory, admitted Current Spec evidence, and identification of file and Spec binding provenance before a report is returned. It does not check the formulas, counts, classification, ownership, attribution, dependency resolution, or review judgments described above.

The source does not define a complete-versus-partial report outcome. This trace therefore models a returned report and does not establish completeness. The prior Lean model in AN-S-3393@1 admits Current rows with a SPEC marker and preserves supplied body measurements. It also states that the implementation-plus-test total includes test code. Its body measurements and arithmetic are not checked by this trace.

## Sources

- [Parnas, On the Criteria To Be Used in Decomposing Systems into Modules](https://doi.org/10.1145/361598.361623)
- [Microsoft, Code metrics](https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-values)
- [Zimmermann et al., Mining Version Histories to Guide Software Changes](https://doi.org/10.1109/ICSE.2004.1317478)
