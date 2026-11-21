---
atom_family: SPEC
atom_id: AN-S-2881
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 3
  updated_at: 2026-10-29 01:07:23 +0400
---
# Summary

Define Template

## Claim

A Template is a parameterized, non-executable Asset used by runtime or evaluations to construct a result.

### Formal claim

```text
Asset/Template
```

## Semantics

Instructions executed by an LLM are Prompts rather than Assets. Parameterization alone does not make a Prompt an Asset.

## Details

CA-A-1278 removes Resources and preserves this useful classification under Asset. This next-version Draft does not promote or retire Current sources.
