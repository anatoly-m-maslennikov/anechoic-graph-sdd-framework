---
atom_family: TKT
atom_id: AN-T-2985
container:
  atom: AN-T-2944
priority: 2
context:
  template: question
state:
  status: resolved
  version: 3
  updated_at: "2026-11-22T11:46:04.570866+00:00"
---
## Summary

Choose the Beta stack selector owner

## Decision

Use the framework checkout's root `project.toml` as an image build input.
Its one `stack` setting selects `current` or `beta`. The runtime image
builder and Local Release read and fingerprint the same selector. The
comparison passes the same admitted Project settings to both images.

Local Release built both selections as separate immutable images. The
host runtime image manager admitted each by the same source fingerprint.
Each image answered the same MCP and Web API query from its own copy of
the Project fixture.

## Acceptance

An explicit stack selection produces the matching immutable candidate
image. Compare both images against identical fixture copies and verify
the selected process boundaries through the real API.

## References

AN-T-2944, AN-T-2976, AN-T-2958, AN-S-1900, and AN-S-1992.
