---
atom_family: SPEC
atom_id: AN-S-250
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Roll the Journal part after one hundred events

# Roll the Journal part after one hundred events

## Claim checked

**every** author-date Journal segment **contains** **<=100** accepted events.

## Test case

prepare `<author>-2026-08-20-part-1.ndjson` with 99 valid events, append two new events for the same author **and** date, **and** inspect both receipts **and** carriers.

## Acceptance criteria

the first append becomes line 100 of `part-1`; the second append becomes line 1 of `part-2`; neither segment **contains** more than 100 events; **and** no part number is skipped.

## Failure disposition

reject the Journal Tool **if** it overfills `part-1`, opens `part-2` early, skips a part number, **or** rewrites an admitted record.
