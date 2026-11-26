---
atom_family: SPEC
atom_id: AN-S-1612
container:
  component: C58
tier: 1
context:
  lens: DOM/MTD
state:
  status: active
  version: 29
  updated_at: '2026-11-25T21:49:46.814700+00:00'
---
## Summary

Keep Evaluation realization chains distinct

## Claim

### Prose Claim


Evaluation realization chains and their associated implementation, evidence, and operational contributions.


Keep the QA Spec's realization chains distinct between deterministic test implementations **and** qualitative, probabilistic, statistical, rubric-based, **or** model-judged evaluation implementations.

**every** chain **must** keep these contributions distinguishable:

- its executable Implementation;
- its configuration **or** rubric;
- its factual execution result;
- its Evidence;
- its Verification judgment.

## Details

Use Test and Evaluation as mechanism labels. Select the governing QA Spec's Template independently of the mechanism.

a shared runner, prompt, judge, report, **or** gate **must not** merge the chains' meanings, results, **or** coverage. the source authority, executable mechanisms, factual Journal Records, **and** reusable Operations definitions retain their distinct roles under AN-S-1871 **and** AN-S-367.
