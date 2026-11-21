---
atom_family: TKT
atom_id: AN-T-2034
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-20T20:35:37.537273+00:00"
---
## Summary

Existing Summary punctuation blocks lifecycle writes

## Claim

### Prose Claim

In the ANECHOIC working tree based on commit `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/placement.py`, `_slug` and `derive_filename`, reject Summary characters outside ASCII letters, digits, spaces and hyphens. Draft preparation uses this function even for a content-only revision of an existing carrier. CA-D-282@26 defines the Filename Summary Slug as lowercase ASCII kebab-case serialization of the complete Summary.

The local MCP rejected content-only revisions of CA-D-672@21, CA-M-464@16, CA-M-500@11 and CA-R-2729@10 at `placement.derive_destination` before any effect. Their existing Summaries contain commas or periods. The tool returned a generic `backend_failure`. The requested spec corrections remain unpromoted. The change to an existing Summary or the filename conversion rule is open for discussion.
