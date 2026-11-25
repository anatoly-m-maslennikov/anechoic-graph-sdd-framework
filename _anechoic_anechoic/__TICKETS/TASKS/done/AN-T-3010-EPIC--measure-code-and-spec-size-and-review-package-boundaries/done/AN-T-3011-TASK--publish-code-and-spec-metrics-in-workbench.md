---
atom_family: TKT
atom_id: AN-T-3011
container:
  atom: AN-T-3010
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 4
  updated_at: "2026-11-23T07:35:05.075739+00:00"
---
## Summary

Publish Code and Spec Metrics in Workbench

## Work

Implement and verify the six ratios, Package size and dependency profiles, and explicit Spec binding coverage. Verify native updates and run scoped Local Release with AN 3 coordination.

## Acceptance

Query architecture_ratios, package_review_profiles, and package_largest_files from the installed Workbench. Verify the repository's 45/300 checks and Code Access findings for the new code.

## Outcome

Scoped Local Release 0.4.4.81 completed on port 51487 in run `an-t-3010-architecture-admitted-db`. The release passed 20 static checks, 552 host tests, 15 image tests, and the packaged MCP canary. The release retained images with foreign or incomplete ownership evidence.

The installed MCP and Workbench verified all six ratios. C76 measured 3,678 implementation bytes and 3,430 test code bytes. The full Spec measured 3,348 bytes and its body measured 2,796 bytes. Both exact Spec bindings and the decimal kB and MB conversions passed.

The Studio baseline measured 50 Components and produced 46 Package review profiles. The two largest Packages were Kernel Mixer and Adapters. The review identified shared query state in Kernel Mixer and a broad subject notation interface in Adapters. That evidence supports further boundary review.

The scoped changes passed the repository's 45/300 limits and Code Access checks. AN-T-3012 tracks earlier intermittent browser failures. The image gate now preserves browser failure traces.