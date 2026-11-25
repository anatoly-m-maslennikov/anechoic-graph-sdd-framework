---
atom_family: TKT
atom_id: AN-T-3916
container:
  component: C27
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-24T13:55:11.475257+00:00'
---

## Summary

Release improvement

## Objective

Keep Local Release resumable and replace the manual steps found in the
[release audit](../../../LAYER_6_OPERATOR_DOCUMENTATION_C25/README.md)
with maintained Release commands.

## Baseline

Local Release journals the target Project, allocated version, completed
phases, package, and exact image under the run ID. From the same checkout,
`local --resume --run-id <id>` resumes at the first unfinished or invalidated
phase and keeps the allocated version.

After interrupted installation or startup, reconcile the files and
container with the journal before repeating either action. After verified
startup, a cleanup failure resumes cleanup alone.

## Work

1. Check the pinned Chromium launch, DuckPGQ extension load, and locked
   frontend dependencies before the long gates. Reuse Test Suite checks.
   Report the failed prerequisite and its cache path or setup step.
2. Add a Release command that builds the canary package and runs the
   existing image suite against its exact image ID. End verification before
   installation and record the result.
3. Install a verified source Git revision into an explicit target Project.
   Check the revision and image before installation. Use the target's
   Manifest port, configuration, and Project data. Reuse `prepare-local`
   when preparing an isolated checkout.
4. Keep source revision, image ID, target Project, readiness, and test
   reports with the run ID. Capture the failed candidate's container state
   and recent logs before cleanup. Report the Docker port or resource that
   blocked the run and retain ownership checks in cleanup.

## Acceptance

- **Specification.** The Release and Local Release Specs define the command
  inputs, early checks, evidence, target selection, and resume behavior.
- **Implementation.** Focused tests cover each early failure, verification
  without installation, mismatched source or target, and evidence
  collection before cleanup. Regression tests cover same-run resume.
- **Review.** Check the results against the Specs. In an isolated rehearsal,
  verify the exact image, install it into the selected target, and exercise
  interruption and recovery. Link the run evidence before closing the Epic.
