---
atom_family: TKT
atom_id: AN-T-2143
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 08:35:07 +0400
---

## Summary

Verify the release package image

## Details

The v3 run passed all 61 focused modules, with 517 cases and two skips. Docker then failed to find the Engine path for the ca Skill. The package now verifies the same source Skill files at its Engine build path and at SKILLS/ca.

The corrected release package built and verified image `sha256:b582c4437bbd49823601f31c16f89a0d106f12465ef1d77e7f0a970991c3bff6` in scratch. The runtime was still serving the previous installation. Evidence is under `.anechoic_tmp/CA-P-2791/CA-P-2818/release-preflight/`.
