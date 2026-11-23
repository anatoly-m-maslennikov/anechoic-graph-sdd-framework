---
atom_family: PROJECT_CONFIG
atom_id: AN-P-42
structure:
  container:
    component: C00
context:
  template: action
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Prepare bound public-release materials

# Summary

Prepare bound public-release materials

## Action

Prepare bound public-release materials **means** the sole content prompt for one selected Version and source snapshot. It returns the full public PR body and concise Version History summary.

## Details

The PR body distinguishes What’s new and What’s fixed. README, Version History edits, and all remote effects are mechanical later work. If the actual URL is not yet known, CA-O-198 appends it after PR creation; no placeholder is valid. A different Version or changed code, Methodology, or package requires a fresh full suite before public release.
