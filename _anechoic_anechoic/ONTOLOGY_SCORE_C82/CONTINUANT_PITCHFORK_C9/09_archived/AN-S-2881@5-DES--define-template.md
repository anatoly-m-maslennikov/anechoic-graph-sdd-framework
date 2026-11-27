---
atom_family: SPEC
atom_id: AN-S-2881
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T19:17:02.458721+00:00"
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
