---
atom_family: SPEC
atom_id: AN-S-1093
structure:
  container:
    component: C16
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Verify normalize portable repository text bytes

# Verify normalize portable repository text bytes

## Claim checked

CA-M-201 produces one semantic-preserving **and** byte-idempotent representation of supported repository text.

## Applicable when

apply whenever the repository text-normalization policy **or** normalizer implementation changes.

## Test case

prepare equivalent supported text files with mixed line endings, optional byte-order marks, different final-newline states, **and** one undecodable file. normalize the supported files twice **and** compare decoded text **and** bytes.

## Acceptance criteria

**all** supported variants become byte-identical while decoded semantic text is preserved; the second pass changes no bytes; the undecodable file is rejected **and** remains byte-identical **to** its input.

## Failure disposition

reject the realization **and** preserve policy version, input **and** output digests, decoded comparisons, second-pass result, **and** rejected-file bytes.
