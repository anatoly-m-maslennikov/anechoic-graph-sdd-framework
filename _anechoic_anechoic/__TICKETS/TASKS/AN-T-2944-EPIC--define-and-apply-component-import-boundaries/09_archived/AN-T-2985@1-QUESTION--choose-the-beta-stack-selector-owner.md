---
atom_family: TKT
atom_id: AN-T-2985
container:
  atom: AN-T-2944
priority: 2
context:
  template: question
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T11:21:46.086795+00:00"
---
## Summary

Choose the Beta stack selector owner

## Situation

AN-T-2976 requests `project.toml` for current and Beta image selection.
The checkout has no active reader for this carrier. AN-S-1992 makes the
Project Manifest reader the shared boundary for runtime Project settings.

## Decision needed

Choose where `project.toml` lives and which Component owns its reader.
The proposed boundary is framework image selection. Each image records
the selected stack and the two images use the same admitted Project
settings during comparison.

## Acceptance

An explicit stack selection produces the matching immutable candidate
image. Compare both images against identical fixture copies and verify
the selected process boundaries through the real API.

## References

AN-T-2944, AN-T-2976, AN-T-2958, AN-S-1900, and AN-S-1992.
