---
identity:
  atom_id: AN-T-2798
context:
  container:
    atom: AN-T-2791
  tier: 3
  template: task
state:
  status: "done"
  version: 2
  updated_at: "2026-11-20T12:17:30.061313+00:00"
---
## Summary

Freeze the shared Anechoic migration map

## Work

Account for all source carriers, exact references, and trace pins. Resolve identity and family exceptions before freezing deterministic allocation.

Use the resolved CA-C-761, CA-C-766, CA-C-768, and CA-C-769 decisions in
the next migration replay. Keep the dispositions that those decisions
explicitly hold. Freeze the applied map at the files and digests below.

## References

CA-P-3075, CA-C-761, CA-C-766, CA-C-768, and CA-C-769.

## Verification

- `_migration/native-id-map.tsv` has 5,999 stable mappings. Its SHA-256 is
  `140d94484a8c5f9d0b3edc5a216b1bace8051c1753a0468783007c51ced98078`.
- `_migration/native-aliases.json` has 6,413 original paths, all resolved to
  exact native references through MCP. It supplies 6,388 legacy ID aliases.
  Its SHA-256 is `063b3224551cad238ef90571dd1af2656acf8e7e88ccb000610b75fcb612d89a`.
- The trace audit verified 93 legacy pins. Keep CA-R-2728@8 at its retained
  legacy path. Keep all 169 held Drafts in legacy. Archive transfer receipts
  preserve the original paths and digests of historical files.
