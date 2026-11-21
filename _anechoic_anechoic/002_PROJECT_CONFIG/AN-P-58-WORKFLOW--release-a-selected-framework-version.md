---
atom_family: PROJECT_CONFIG
atom_id: AN-P-58
structure:
  container:
    component: C27
context:
  template: workflow
state:
  status: active
  version: 38
  updated_at: '2026-11-21T21:51:04.697298+00:00'
---
## Summary

Release a selected Framework Version

## Operation

Local Release is the Operator-invoked local Workflow for one Project. It validates input paths, commits permitted pending changes, bumps the candidate Version, and runs C19 Test Suite unit checks. It reads checked-in assets, prepares the Framework and runtime package, and builds one candidate image directly with Docker.

C19 then runs end-to-end checks against that exact image and a disposable canary. After both pass, Local Release installs the verified package and Skill, starts the same candidate for Project MCP, verifies readiness, and applies the production tag. A failed or unsafe phase stops and reports its observed effects.

The Workflow preserves protected settings, authoring sources, Project state, and unrelated resources. It invokes no ANECHOIC runtime Components or Journal and does not compile or regenerate assets. Public Release is separate and prepares drafts without running a suite.

## Steps

| Step | Action | Boundary |
| --- | --- | --- |
| AN-P-30 | AN-P-25 | validate input and delivery paths |
| AN-P-31 | AN-P-26 | prepare checked-in Methodology assets |
| AN-P-35 | AN-P-29 | install verified delivery and check Project MCP |

The C19 unit, end-to-end and canary checks, Git checkpoints, package preparation and Docker operations are internal Workflow work. The image is built only after the unit checks pass; installation starts only after end-to-end and canary checks pass.

## Details

Invoke `LAYER_5_FRAMEWORK_DELIVERY/release.py local --project-root <project-root> --run-id <run-id> [--image-mode refresh|existing] [--test-module <repo-relative-module> ...]` in the governed environment. Both image modes use checked-in assets. A focused test selection is reported as focused; it is not a complete-suite result.

The initial Git checkpoint commits permitted tracked and untracked nonignored changes and requires a clean index and worktree. Environment-file exclusions and path protections remain. Failure stops before tests or Docker work. Later checkpoints retain their actual results without empty commits.

Cleanup removes only positively identified obsolete Project-owned resources that are safe to remove. Preserve container-referenced, foreign, unowned, protected, and uncertain resources. Report incomplete cleanup.
