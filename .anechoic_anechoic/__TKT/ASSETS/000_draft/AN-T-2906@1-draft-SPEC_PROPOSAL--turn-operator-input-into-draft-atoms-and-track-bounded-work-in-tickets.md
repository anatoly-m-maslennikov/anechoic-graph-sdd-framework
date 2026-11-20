---
identity:
  atom_id: AN-T-2906
context:
  container:
    component: C00
  tier: 3
  template: Spec Proposal
state:
  status: draft
  version: 1
  updated_at: '2026-11-16T21:31:34.864781+00:00'
---
## Summary

Turn Operator input into Draft Atoms and track bounded work in Tickets

## Proposal

Use a direct Draft when the Operator’s input gives a clear individual change.
For changes that span several claims, develop one proposal with the Operator and
attach it to its Ticket when one exists.

1. Split the input into statements. Identify project intent, Ticket work, and
   durable rules about the product or the Project. Put product claims in
   SPEC, repeatable Project procedures and local model extensions in PMETA,
   and individual cases in TKT.
   Identify the governing Component, Concern, and relevant axes.
2. Group spec statements around one claim per Atom. Use SQL to find existing
   Atoms by typed fields, relations, and their explicit Concern Path or
   implicit Component context.
3. Add substantive new material to a Draft revision of the matching Atom.
   Give a distinct claim its own new Draft. Link the claims that depend on
   or support one another.
4. Compare Drafts with one another and with Active Specification before promotion.

In SPEC, PMETA, and TKT, edit a Current Atom’s content or authored
properties through a Draft revision with the same Atom ID. Work Logs and
other Ticket assets follow the in-place editing rule below. Review a Draft
before promotion. A status transition preserves the Atom ID and Version.

The Operator supplies the choices that matter. If review or implementation uncovers
an ambiguity that could change one of those choices, ask the Operator and capture the
durable answer where the rule belongs. Implement using the Specification and
existing code. Keep routine coding decisions in the code.

### Project Meta

The PMETA tree holds the Project’s internal Workflows and local meta-model
extensions. Tickets live in the TKT tree. Internal
Workflows include local and public release and rules for Ticket work. They
operate on top of Anechoic and can start through MCP. The Operator can add
or change them. SPEC covers the result and its Realization.

An executable PMETA Workflow has an `AN-P` Atom ID. A Step or Action
can have its own `AN-P` ID. Only an Active PMETA Workflow revision can
start a Run.

Every execution attempt has its own Run ID. The Run records the Workflow
Atom ID and the exact revision it started from. Multiple attempts can refer
to the same Ticket ID. CA-C-744 tracks the deferred proposal to use the
Task Atom ID as that shared reference.

Atom lifecycle belongs in Anechoic’s SPEC. Product behavior such as order
lifecycle belongs in the product’s SPEC. DevOps, including intended CI/CD
behavior on merge or deployment, also belongs in SPEC. The Realization
contains the code and pipelines that enact it. PMETA holds the Project’s
internal procedures, which can call those pipelines. Classify a process by
what it does, regardless of its entry point.

### Tickets

Tickets record one occurrence of work. They can track a task, issue, epic, version
plan, or configuration change. A work Ticket has one Task and one Work Log.

Give each Task, Work Log, and related Ticket asset Atom its own `AN-T` ID.
Use the Task's Summary for its Work Log and related asset Atoms. Each uses
the template for its own record type. Each Work Log and related asset Atom
has an explicit relation to the Task's `AN-T` ID. If an Epic contains the
Task, the Work Log and related assets use that same Epic as their
`container`.

Edit Work Logs and other Ticket assets in place in both Draft and Current
status groups. Attach analysis, proposals, and other work assets as needed.
Place a linked Ticket asset beside its Task or Issue. Keep its own Atom ID
and exact references. Standalone analysis and other Ticket assets live in
`__TKT/ASSETS/` and follow the same editing rule.

Specification uses Draft, Active, and Archived. Ticket Status is a flat set of
values: Draft, Backlog, Active, Done, Canceled, Resolved, and Archived. Map legacy Queued
to Active during migration. Apply status grouping through classification. A canceled Ticket uses `Canceled` even when some work was completed. Keep delivery state separate from work status.

### Source notes

Gemini transcript lines 4290–4295, 12656–12682, 18234–18338, 23054–23066,
23282–23292, and 23470–23472.
Second brainstorm, lines 499, 533, 595, and 645.
Third brainstorm, lines 2015–2445 and 3211.
