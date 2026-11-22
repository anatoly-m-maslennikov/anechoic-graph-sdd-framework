---
atom_family: TKT
atom_id: AN-T-2932
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 5
  updated_at: '2026-11-22T11:49:27.339015+00:00'
---
## Summary

Admit Project Axioms, Project Contracts, and Applicable Principles

## Work

Apply the Operator's Project Atom tier decision in general SPEC at the
Project root.

| Project Atom | Tier | Content |
| --- | ---: | --- |
| Project Axiom | 0 | State a premise accepted in the scope of the Project Goal. |
| Project Contract | 0 | State what a user supplies and what the Project provides in return. |
| Project Applicable Principle | 1 or 2 | State a rule that guides decisions when its applicability conditions hold. |
| Main Project Solution, Policy, or Standard | 3 | State a main Project solution or governing rule. |

Each Project has exactly one Current Project Manifest at Tier -1. It
declares the Project and its configuration. The Project Goal also stays
at Tier -1.

Create three Tier 0 Project Contract Atoms. Use the existing Contract base
and the Project as their Container.

Admit the Project Axiom, Project Contract, and Project Applicable Principle
templates. Move the existing Project Axioms to Tier 0 and classify the
existing Applicable Principles at Tiers 1 and 2. Move main Project Solutions,
Policies, and Standards to Tier 3. Preserve authored content, stable IDs,
exact revision references, and source history. Keep legacy release inputs intact.

Connect the Project Atoms in two chains.

- Tier 1 Principles apply Axioms and serve the Project Goal. Tier 2 Principles
  contribute to Tier 1 Principles. Tier 3 Solutions, Policies, and Standards
  contribute to Tier 2 Principles. Tier 4 Solutions and Component Manifests
  contribute to Tier 3 Solutions.
- Tier 0 Contracts serve the Project Goal. Tier 3 Solutions address
  the guarantees in those Contracts.

Author relations from the more specific Atom to its target. Derive the
inverse direction for navigation.

### Shared repository input and guarantees

- The user selects one or more repository roots. ANECHOIC reads across the
  full tree of each selected repository, including files outside
  `.anechoic_*`. Each derived analysis states its coverage and reports
  exclusions, unsupported inputs, and failed reads that affect the result.
- One ANECHOIC runtime serves multiple repositories. Every request or
  action resolves to one selected repository. Scope reads, writes, and
  query results to that repository. Keep its saved Workspaces and Views
  separate from those of other repositories.
  Reject a missing, ambiguous, or mismatched selection when the request
  cannot be bound to one repository.
- ANECHOIC keeps all files it owns for a repository in `.anechoic_*`
  directories. The sole exception is the Package Spec Binding sidecar,
  named `<package folder name>__spec_bind.yaml` at the Package root.

Reconcile the file-placement guarantee with the Current Module
`.spec_trace.md` rule and the release-installed `.agents/skills/ane` path.
Resolve their ownership and placement before claiming conformance. Keep
Module revision pins resolvable and preserve agent discovery of the skill.

### Project Contracts

#### Ontology + Methodology

The user supplies Project concepts, intent, existing Specification and
Realization, and the change or work to be done. The user gets a
representation in versioned Specification Atoms and typed relations, with
guidance for making and checking changes.

Given authored records to check, return findings the user can act on.
Given implementation or test evidence with trace bindings, let the user
resolve the exact Specification revisions that the evidence refers to.

#### MCP

The caller supplies an admitted operation and its required arguments. A
request on the shared service supplies the selected repository explicitly.
The caller gets structured information, a result that identifies the
effects of an operation, or an actionable correction or error.

Query results can arrive inline or by file reference. If a query succeeds
and saving fails, return the query result and identify the save failure.

#### Web Interface

The user opens a repository's Workspace and submits queries or supported
actions. The user gets query results, including graph-query results, and
can reopen saved Views and Workspace state.

Show the result of an action or why it failed. Show when data is unavailable
or still updating. Confirm whether the Contract also includes visual graph
rendering before adding that guarantee.

## Verification

- Verify each of the three Project Atom templates at its admitted Tiers.
  Reject other Tiers for these templates. Verify exactly one Current
  Tier -1 Project Manifest per Project. Preserve the Project Goal and
  existing Component Contract rules.
- Verify that reclassified Atoms keep their IDs and that exact references
  still resolve to the preserved revisions.
- Use one runtime and two repositories with distinct content outside
  `.anechoic_*`. Use the same Workspace ID in both. Interleave reads and
  writes. Verify that selecting one repository cannot return the other
  repository's data or change its saved state. Reject an invalid selection.
- Check the analysis coverage and diagnostics for unsupported and unreadable
  inputs. Check where each ANECHOIC-owned file is written and that only
  Package Spec Binding sidecars use the agreed exception.
- Verify that users can inspect a versioned Specification, act on a
  validation finding, and follow a trace to the exact revision.
- Verify an inline MCP result, a file result, and query success with save
  failure. In the Web Interface, reopen a saved View in the selected
  repository and check the result of a rejected action.

## References

AN-T-2910, AN-T-2791, AN-S-3113, AN-S-3114, AN-S-3129, AN-S-3014, AN-S-1383,
AN-S-2256, AN-S-3037, CA-A-1461, CA-A-1462, CA-A-1463.
