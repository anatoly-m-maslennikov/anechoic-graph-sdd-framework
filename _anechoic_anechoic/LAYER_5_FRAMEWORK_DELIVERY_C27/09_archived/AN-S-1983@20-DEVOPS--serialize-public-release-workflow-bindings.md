---
atom_family: SPEC
atom_id: AN-S-1983
container:
  component: C27
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 20
  updated_at: '2026-11-12T17:10:15.004765+00:00'
---
## Summary

Serialize public-release Workflow bindings

## Claim scope

The Operation identities and execution boundary of one public release.

## Claim

### Prose Claim

Public Release finds the matching open PR, or creates a Draft PR from the already-published branch. Without an actual matching PR URL, stop before pushing. Prepare the PR materials and newest-first Version History with that URL, then commit the candidate and run the full required test suite on that exact commit.

After the suite passes and the checkout still matches the tested commit, push that SHA once. Verify the matching PR's head SHA, update its prepared body and mark it ready for CI. Stop on failed tests, changed inputs, a mismatched PR head or an uncertain remote effect. Report effects already completed. Do not merge or replay the push.
