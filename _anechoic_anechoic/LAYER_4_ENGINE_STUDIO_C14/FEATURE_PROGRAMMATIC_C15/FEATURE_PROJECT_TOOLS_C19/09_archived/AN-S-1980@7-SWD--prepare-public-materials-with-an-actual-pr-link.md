---
atom_family: SPEC
atom_id: AN-S-1980
container:
  component: C19
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Prepare public materials with an actual PR link

# Summary

Prepare public materials with an actual PR link

## Scope

the selected public documentation closure.

## Claim

the public-release Tool **must** prepare README, one full PR body, and short Version History bullets from the selected Version. Its one public-writing prompt produces the full PR body with distinct **What's new** and **What's fixed** sections. It discovers an existing matching PR before push and defers a new Version History hyperlink until the remote returns its actual PR URL.

## Details

Version History remains a concise summary plus actual URL. The Tool completes the one fresh public suite after its initial material closure is frozen and before its first publication. If no matching PR exists, it adds that URL through one mechanical metadata-only follow-up commit and push after creation. That follow-up reopens the actual passed initial public-suite and current source/material evidence; it does not rerun the suite, request a separate review or prompt, or change any non-metadata Version/source/material binding.
