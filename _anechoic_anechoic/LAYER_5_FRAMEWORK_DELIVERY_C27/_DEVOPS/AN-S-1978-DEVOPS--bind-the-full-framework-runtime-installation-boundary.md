---
atom_family: SPEC
atom_id: AN-S-1978
container:
  component: C27
tier: 5
context:
  lens: DevOps
state:
  status: "active"
  version: 31
  updated_at: '2026-11-22T12:51:19.669528+00:00'
---

## Summary

Bind the full Framework runtime-installation boundary

## Claim scope

The installed Framework, local Engine/runtime package and project-local ca Skill delivered inside CA-O-164's local release and CA-O-169's final installation and Project-MCP refresh phase. These are deliveries of the same local release, not a separate installer operation.

## Claim

### Prose Claim

Local Release Version **must** prepare and verify the complete local Engine/runtime package, its bound `ca` Skill, the two verified Active Atom delivery layers and the package-bound candidate Project-MCP image **before** destructive replacement of the installed Framework, runtime or project-local `ca` Skill. It then copies that verified product into `.anechoic_anechoic/000_ANECHOIC_framework/`, installs those same prepared package and Skill bytes at their governed runtime and project-local destinations, and refreshes the Project MCP using that verified image. It **must** preserve protected configuration, authoritative Project sources, existing Journal evidence and unrelated Project data. A failed or uncertain transition **must** stop with its actual observed state and no claim that a partial installation, unavailable MCP or unfinished cleanup completed successfully.

## Details

### Local delivery carriers

After normal source/input/file-safety checks, the C19 functional invocation and checked-in asset preparation, the verified derived product consists of `LAYER_1_META_ONTOLOGY_C9/` and `LAYER_2_META_METHODOLOGY_C58/` at the Project root; the installed Framework copy is `.anechoic_anechoic/000_ANECHOIC_framework/`. Prepare and verify the complete replacement package before clearing any installed Framework, runtime or Skill target; a preparation or verification failure leaves those installed targets untouched. Under the existing one Project installation lock required by CA-O-169, clear only replaceable delivery members at the declared destinations and copy the verified product as-is. Verify that the copy operations succeed and the replacement runtime is healthy before reporting installation success. Neither derived nor installed content becomes authoring authority. Release verification adds no separate Active Atom metadata, placement or relation validation; the specified C19 checks and normal input, permission and file/path safety checks remain. The same C19 entry runs end-to-end tests on the exact candidate image, followed by a C19 disposable canary before production replacement; neither test restarts the production Project MCP.

Prepare the direct local package in a component-owned, Run-specific descendant of the configured Project Temporary State root under `.anechoic_tmp/`, following CA-M-422; staging is not a persistent installation root. The runtime package includes the complete selected Project source package, excluding `.anechoic_<project name>`, `.anechoic_runtime`, `.anechoic_tmp`, and technical transient directories such as `.git`, `.venv` and `.vite`. It carries the two Active Atom layers at those root paths, the three locked uv projects under `LAYER_3_ENVIRONMENTS_C72/`, the complete canonical `ca` payload at `SKILLS/ca/`, and `version.toml`. Install those same prepared bytes at the governed persistent Project runtime package destination outside temporary state; install its complete `SKILLS/ca/` payload at `.agents/skills/ca/` and refresh the package-bound Project MCP bootstrap. This Delivery does not introduce a new persistent MCP path. This Delivery reads checked-in assets without importing ANECHOIC runtime Components.

The prepared runtime supplies the Project-MCP launcher and Docker image inputs. Build one immutable package-bound candidate image in the same Workflow after the functional gate and before any installed target is cleared. Test that exact image through C19 end-to-end mode and a disposable canary. Final installation delivers the prepared bytes, then starts the Project MCP with that exact image on the Project-owned Manifest `project_mcp.http_port` and verifies readiness before applying the production tag to the same image ID; it does not defer image preparation until after replacement. A successful build alone does not prove a working Project MCP. This direct flow requires no candidate-snapshot manifest, retained Full Gate, selected-N execution gate, N+1 promotion, native runtime selector, state-generation proof or bootstrap image-restoration prerequisite.

Fresh local-release image builds record exact Project ownership with `org.anechoic.project` (selected instance ID), `org.anechoic.control_root` (relative control directory) and `org.anechoic.host_project_root` (canonical owning repository root), plus canonical Settings `project.name` in `org.anechoic.project.name` and the full build-time owning-repository Git HEAD commit ID in `org.anechoic.source.head_commit`. Verify those labels by inspecting the built image; missing or invalid Project name or HEAD refuses fresh preparation before building. Name and HEAD are provenance, not ownership gates or proof of a clean checkout or exact built source tree; the runtime source fingerprint and inspected immutable image ID remain the code-identity checks. Docker build cache may be reused without changing candidate identity or transferring ownership. Matching inspected exact ownership labels can identify newly labelled orphan images for bounded cleanup; old unlabelled or otherwise unproven images remain retained and reported.

### Preservation and failure boundary

Keep Settings, runtime configuration, Project Structure, Operator registry, authoritative source carriers, existing Journal and retained evidence outside replacement. Preserve the protected configuration members already present in the derived and installed roots; do not overwrite them from the product. Source and destination paths must remain safe Project-contained regular trees, not symlink aliases. Unrelated Project files, Skills, user directories and other Projects are not replacement targets. Existing ignored Finder metadata and environment carriers remain outside the delivered payload and are not removed by cleanup.

Actual failure reports retain the failed phase and observed result for manual inspection before any separately authorized retry; a report or Journal entry does not prove completion or fabricate a Workflow, approval or earlier event. Release does not call Journal or replay an unknown effect.

Cleanup covers accumulated obsolete release-owned containers and images for this Project, not only the immediate predecessor. Before Project-MCP startup, remove only proven obsolete stopped Project-owned containers; after verified installation and successful startup/smoke, repeat that cleanup and remove proven obsolete images no longer retained by any container or protected reference. Preserve all images and containers carrying the verified current code. A prior Project-MCP container may be stopped and removed only through the existing exact Project-ownership replacement checks; accumulated cleanup preserves other running containers. Unknown ownership or code identity, unavailable inspection, protected use or failed removal retains the target and reports cleanup pending, including unproven orphan images. Tags and version age alone are not proof. Never force-delete containers, remove unrelated or other-Project resources or prune globally. Successful installation does not falsely imply completed cleanup.
