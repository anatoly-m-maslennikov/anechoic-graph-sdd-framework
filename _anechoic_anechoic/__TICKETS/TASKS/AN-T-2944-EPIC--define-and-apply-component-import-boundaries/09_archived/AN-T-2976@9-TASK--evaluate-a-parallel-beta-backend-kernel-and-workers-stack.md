---
atom_family: TKT
atom_id: AN-T-2976
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
  label: Task
state:
  status: "archived"
  version: 9
  updated_at: "2026-11-22T13:57:01.021470+00:00"
---
## Summary

Evaluate a parallel Beta Backend, Kernel, and Workers stack

## Prerequisite

Complete the MCP bridge under AN-T-2944. MCP maps the Backend JSON Tool catalog, forwards calls, and returns responses.

## Work

- Build Kernel, Orchestrator, Workers, and Backend alongside the current
  stack. Name each Beta Component `<component name>_beta_<new component ID>`.
- Use one `stack` setting in the `LAYER_5_FRAMEWORK_DELIVERY/project.toml`.
  Its value selects `current` or `beta` as a set. Build each selection
  as a distinct image.
- Confirm child Components and Component Seeds with the proposed map in
  AN-T-2958. Add one `__shared` entry Module to each Beta Package with
  direct code. Other Packages may import only that Module, subject to
  Code Access. Give each Seed one Manifest, an ID such as `CS123`, and
  an exact Spec Binding in its implementation Package.
- Inspect existing behavior and adopt the pieces that satisfy Beta's
  Contracts, state ownership, and interfaces.
- Start the comparison with a real Project query backed by Worker-built
  Model and Structure artifacts. Refresh those artifacts after a file
  change. Use identical fixtures and acceptance checks for both images.
- Record discrepancies in either image and evaluate each against the
  applicable Specs and Contracts.

## Outcome

Use the two-image evidence to decide whether to continue with Beta and what corrections each stack needs.

## Verification

Local Release built separate Current and Beta images from the same
selector. Both answered an inline query through MCP and the Web API.
Beta served distinct rows from two Projects on a shared host.

Fresh images ran against identical copies of a Project with a Tier 4
Component Manifest. Both published its initial Structure, added a valid
revision, recorded a failed build for an invalid revision, and recovered
on the next valid edit.

During the failed build, Beta kept both artifacts and the accepted query
row. Current kept both artifacts and exposed the invalid row through its
separate projection path. At that checkpoint the two query schemas used different Summary
column names. In that comparison, Beta exposed one Tool and omitted paging and type metadata.

The comparison of remaining Tool behavior and Contracts continues.

The normal shared launcher started a Beta image with one Backend and
separate Kernel and Orchestrator peers for two Projects. MCP and Web
read the public SQL schema. Queries reused the same peers and a valid
edit refreshed one Project without changing the other. Single-Project
launcher verification passed through the same schema Tool.

The Realization Graph verified one shared entry in each of seven Beta
Packages, two allowed imports between those Packages, and zero denied
or unresolved sites. The static Test Suite passed the 300-line module
limit and the 45-line function limit.

The Beta image returned typed query pages from the owning Kernel and
presented `content.summary` in the public schema. Real MCP and Web
requests passed for run, page, and check. One admission process served
the shared Backend while two Projects reused separate Kernel and
Orchestrator peers. A valid edit refreshed one Project.

The Beta comparison still needs the remaining Workbench operations and
storage settings.

The Beta Worker builds the enabled Realization Graph, and Kernel admits
it together with the matching Project rows, Model, and Structure.
The fresh Beta image published the graph schema by default. After a
source rename, MCP and Web returned the changed resolution while the
other Project kept its own data. A Project can disable the graph.

The Local Release canary passed on the fresh Current and Beta images.
The Beta comparison continues for persisted storage, remaining
Workbench operations, and Component relationships in the graph.

## Paired verification update

Both images passed the Local Release MCP canary. The paired Docker suite
ran 13 cases per image. Current passed 12 and Beta passed 7. The browser
launcher failed in the managed environment for both images.

Beta passed the Realization Graph relation-count queries, including
DuckPGQ MATCH. Its View flow then stopped at an unavailable Tool. The
other differences were Work Journal, native reference and relation
projection, lifecycle Tools, and View execution and rebuild.

Focused tests verified that Beta disk storage reopens the accepted
generation after a failed rebuild. Its property graph remains queryable
after rollback and restart. These checks do not establish Journal parity.
