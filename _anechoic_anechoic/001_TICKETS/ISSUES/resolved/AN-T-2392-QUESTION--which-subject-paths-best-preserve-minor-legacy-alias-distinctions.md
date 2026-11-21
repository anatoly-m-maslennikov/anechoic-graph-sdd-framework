---
atom_family: TKT
atom_id: AN-T-2392
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: resolved
  version: 2
  updated_at: 2026-10-24 17:00:51 +0400
---
# Summary

Which Subject paths best preserve minor legacy alias distinctions?

## Question

Do these bounded Subject choices preserve the intended topic without creating
another entity, property or Type?

## Scope

Only the listed Subject aliases in the Current Candidate #7 migration.
The owning source text and runtime behavior do not change.

## Details

- CA-M-266: Task is a Plan Label, not a separate Plan Type. Use the existing
  Plan Content Role for the dependency, retaining the Task-specific conditions
  in the source text. Do not introduce `Plan/Type: Task` again.
- CA-M-238: the old Governed Subject Set means the GOVERNS portion of an
  Atom's Subjects. Use Atom.Subjects as the dependency while the source text
  keeps its explicit GOVERNS-only selection. It does not mean that GOVERNS
  and DEPENDS_ON have become the same relation.
- CA-R-644: a materialized representation can be a Carrier, not only a derived
  Projection. Use the existing Engineering Carrier topic for its necessity
  constraint; do not create a generic materialized-representation entity.

The Operator authorized recording small uncertainties as Questions, applying
the best available existing meaning and continuing. These are local alias
choices, not new global definitions. Recheck them during the separate content
review. The Question is not an approval gate or proof of a runtime result.

Checked: Candidate #7, its application plan, this chat's human inputs from
2026-10-22 through 2026-10-24, and active MECE/DRY/necessity/coherence principles.
Existing Draft and Archived Atoms are not migrated. No PROGRAMMATIC
implementation is authorized by this Question.

## Resolution

Operator answers consolidated on 2026-10-24.

The recorded bounded interpretations follow the Operator's settled model:
Task is a Plan Label, not a Type; a GOVERNS-only selection can use Atom.Subjects
with its exact boundary in Content Scope; materialized representation concerns
Carrier rather than requiring a new generic entity. These are topic mappings,
not permission to merge GOVERNS with DEPENDS_ON or to invent a new Domain kind.
The source-specific choices remain visible in Details; this resolution makes
no new claim about content migration or runtime execution.
