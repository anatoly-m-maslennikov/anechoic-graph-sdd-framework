---
atom_family: SPEC
atom_id: AN-S-2763
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 29
  updated_at: "2026-11-25T22:00:01.535118+00:00"
---
## Summary

Validate self-sufficient Atom Carriers

## Claim

An Atom Carrier supplies the authored values required by its Template. Check the Carrier using AN-S-3160 and the applicable Formal Manifests.

- Read Header values and required Markdown sections from the file. Check missing required values, absent optional values, duplicate YAML keys, repeated declared sections, and example headings inside fenced blocks.
- Accept an absent Concern. When present, check Subject, Path, and Relation together under AN-S-3163 and AN-S-3178. Check a Ticket with multiple locators. Preserve the declared Container and textual applicability when the Concern changes.
- Compare the derived filename and destination with the actual Carrier. Keep the Atom indexed under its declared Container and report a placement discrepancy with the actual and expected paths.
- Check authored Relations and their derived inverses as one fact. Reject a separately authored derived inverse when the applicable Relation Manifest excludes it.
