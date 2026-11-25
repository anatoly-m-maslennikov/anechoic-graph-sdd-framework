---
atom_family: SPEC
atom_id: AN-S-1612
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 28
  updated_at: "2026-11-25T21:49:46.747672+00:00"
---
## Summary

Keep Evaluation realization chains distinct

## Claim

### Prose Claim


Evaluation realization chains and their associated implementation, evidence, and operational contributions.


an Evaluation Atom's realization chains **must** remain distinct between deterministic test implementations **and** qualitative, probabilistic, statistical, rubric-based, **or** model-judged evaluation implementations.

**every** chain **must** keep these contributions distinguishable:

- its executable Implementation;
- its configuration **or** rubric;
- its factual execution result;
- its Evidence;
- its Verification judgment.

## Details

a shared runner, prompt, judge, report, **or** gate **must not** merge the chains' meanings, results, **or** coverage. the source authority, executable mechanisms, factual Journal Records, **and** reusable Operations definitions retain their distinct roles under CA-R-1683-CORE_META_MODEL-CORE-REQUIREMENT--authority-evaluation-and-operations-remain-distinct **and** CA-R-1684-CORE_META_MODEL-CORE-REQUIREMENT--separate-analysis-from-factual-execution-records.
