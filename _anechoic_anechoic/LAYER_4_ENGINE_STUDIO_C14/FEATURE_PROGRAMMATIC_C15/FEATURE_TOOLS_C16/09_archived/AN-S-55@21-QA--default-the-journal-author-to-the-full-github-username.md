---
atom_family: SPEC
atom_id: AN-S-55
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Default the Journal author to the full GitHub username

# Default the Journal author to the full GitHub username

## Claim checked

Context gathering uses the current operator's full GitHub username **when** no author is supplied.

## Test case

Configure Git display name `Anatoly Maslennikov` **and** GitHub username `anatoly-m-maslennikov`, omit the author input, **and** gather one valid file-change context.

## Acceptance criteria

the sealed context author is exactly `anatoly-m-maslennikov`, **and** the predicted Journal filename begins `anatoly-m-maslennikov-` rather than using the display name, email, abbreviation, **or** repository owner inferred ambiguously.

## Failure disposition

Reject the Finder **if** it emits another author value **or** continues **when** the current full GitHub username cannot be resolved unambiguously.
