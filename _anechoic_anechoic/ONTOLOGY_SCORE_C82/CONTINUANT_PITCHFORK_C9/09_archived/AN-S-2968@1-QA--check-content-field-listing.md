---
atom_family: SPEC
atom_id: AN-S-2968
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T22:00:01.907688+00:00"
---
## Summary

Check Content Field Listing

## Claim

### Prose Claim

The proposed `content.get_list()` contract must distinguish allowed registered Markdown Content headings for a kind from headings actually present in a selected instance. It must return heading names, not heading values, logical-key aliases, unrelated metadata keys, or function names.

The registered headings are `# Summary`, optional `## Claim scope`, `## Claim`, optional `## Semantics`, and optional `## Details`. Formal and natural claims both use `atom.content.claim`; version identity remains `atom.version_number` in YAML. `atom.content.details` returns the text/value under the registered Details heading.

## Details

Use a declared qualified Requirement fixture whose allowed headings include `# Summary`, `## Claim scope`, `## Claim`, and `## Details`, while the selected instance contains only `# Summary`, `## Claim`, and `## Details`. The kind-level result must report all allowed headings, including optional headings; the instance-level result must report only headings actually present. Preserve heading spelling and order. Do not include `atom.property`, colon/property-text layers, unrelated metadata, or `get_list` itself. This remains a proposal, not an executable test or implementation.

## Proposal status

This is a proposed candidate only, tracked by CA-A-1237. Its normative wording is not adopted methodology and must not be promoted as part of relation-notation changes.
