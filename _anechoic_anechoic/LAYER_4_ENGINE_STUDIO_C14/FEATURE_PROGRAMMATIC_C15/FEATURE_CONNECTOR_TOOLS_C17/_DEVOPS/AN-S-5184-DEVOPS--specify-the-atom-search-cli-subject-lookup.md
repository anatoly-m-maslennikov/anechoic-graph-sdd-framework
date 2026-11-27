---
atom_family: SPEC
atom_id: AN-S-5184
container:
  component: C17
tier: 4
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-27T17:35:02.240947+00:00'
---

## Summary

Specify the ATOM_SEARCH CLI Subject lookup

## Claim

The delivered `ATOM_SEARCH` wrapper **must** support the existing `--under PATH` and `--lifecycle VALUE` filters and the following Subject lookup options:

- one `--subject VALUE` criterion per request;
- `--subject-field governs|depends_on|both` to select the flat Subject field;
- `--subject-match exact|prefix` for literal equality or delimiter-aware lexical prefix matching;
- optional `--subject-profile legacy|approved`, where omission means `legacy` and an unknown or malformed supplied profile fails;
- repeatable `--content-role ROLE` values as an OR set within the valid-file filter, and `--scope-unit OWNER` as a conjunctive owner filter.

Subject lookup defaults to Active. Explicit `--lifecycle all` can also return valid non-Active originals, including correctly placed Done or Backlog carriers, with their carried Status and exact source pins preserved. Lookup membership does not grant Subject-preview eligibility or cause a lifecycle transition.

Legacy uses `/` as bearer qualification, `:` as Property-to-allowed-value, and literal dots, and rejects every `atom(...)` selector. Approved uses `/` as broader-to-narrower, `.` as bearer-to-dependent, and `:` as Property-to-allowed-value, and accepts only the exact initial lowercase selector forms registered by CA-R-1321; `Atom` and `atom` remain distinct. Exact matching remains literal; prefix matching uses only the selected profile's declared boundaries. Both profiles reject `@`, and approved rejects every other selector construction, escaping, conjunction, wildcard, evaluation, and alias. It is neither a fourth operator nor carrier/display notation.

Each result **must** identify the source pin and exact occurrence: `atom_id`, `version`, `status`, `owner`, `relative_path`, `sha256`, `updated_at`, `field`, `index`, and `value`. `index` is the list index for `depends_on` and is null for the scalar `governs` field. Results are deterministic and path/field/index ordered. The result also carries the selected `subject_profile` and `subject_profile_evidence` containing exactly the five reviewed grammar pins and `native_admission: not_performed`. Malformed, unreadable, duplicate, or rejected selected files appear in a separate `diagnostics` collection; a valid empty match is returned as an empty result and is not a diagnostic. The lookup is lexical only: it never infers target conformance, ontology relations, a native edge, grammar adoption, or source migration.
