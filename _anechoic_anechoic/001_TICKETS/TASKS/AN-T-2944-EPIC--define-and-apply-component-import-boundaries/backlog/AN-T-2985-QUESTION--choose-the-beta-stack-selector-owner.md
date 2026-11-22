---
atom_family: TKT
atom_id: AN-T-2985
container:
  atom: AN-T-2944
priority: 2
context:
  template: question
state:
  status: "backlog"
  version: 2
  updated_at: "2026-11-22T11:21:46.087633+00:00"
---
## Summary

Choose the Beta stack selector owner

## Decision

Use the framework checkout's root `project.toml` as an image build input.
Its one `stack` setting selects `current` or `beta`. The runtime image
builder and Local Release read and fingerprint the same selector. The
comparison passes the same admitted Project settings to both images.

Current source closure selection is implemented. The Beta image needs
its runtime entry point and the complete selected stack.

## Acceptance

An explicit stack selection produces the matching immutable candidate
image. Compare both images against identical fixture copies and verify
the selected process boundaries through the real API.

## References

AN-T-2944, AN-T-2976, AN-T-2958, AN-S-1900, and AN-S-1992.
