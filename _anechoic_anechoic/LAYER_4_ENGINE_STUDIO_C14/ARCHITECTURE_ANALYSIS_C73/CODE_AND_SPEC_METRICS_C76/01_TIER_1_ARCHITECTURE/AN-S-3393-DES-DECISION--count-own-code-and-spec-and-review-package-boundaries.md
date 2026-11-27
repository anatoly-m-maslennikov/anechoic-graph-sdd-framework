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
  - AN-S-3397
state:
  status: active
  version: 1
  updated_at: '2026-11-26T16:38:01.188014+00:00'
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

This model admits a row when its status is Current and its ID has the SPEC marker. It carries the supplied body measurements unchanged. It does not prove ownership or the accuracy of the supplied measurements.

```lean
def admitCurrentSpec (current hasSpecMarker : Bool) (bodyBytes bodyLines : Nat) : Option (Nat × Nat) :=
  if current && hasSpecMarker then some (bodyBytes, bodyLines) else none

theorem admitted_preserves_body (current marker : Bool) (bytes lines : Nat)
    (h : admitCurrentSpec current marker bytes lines ≠ none) :
    admitCurrentSpec current marker bytes lines = some (bytes, lines) := by
  cases current <;> cases marker <;> simp_all [admitCurrentSpec]

theorem total_includes_test (implementation tests : Nat) :
    implementation ≤ implementation + tests := by
  omega
```

## References

- [Parnas, On the Criteria To Be Used in Decomposing Systems into Modules](https://doi.org/10.1145/361598.361623)
- [Microsoft, Code metrics](https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-values)
- [Zimmermann et al., Mining Version Histories to Guide Software Changes](https://doi.org/10.1109/ICSE.2004.1317478)
