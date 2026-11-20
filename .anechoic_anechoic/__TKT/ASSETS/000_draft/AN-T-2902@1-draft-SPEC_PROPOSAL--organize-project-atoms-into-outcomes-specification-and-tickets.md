---
atom_family: TKT
atom_id: AN-T-2902
structure:
  container:
    component: C9
  priority: 2
context:
  template: Spec Proposal
state:
  status: draft
  version: 1
  updated_at: '2026-11-14T12:27:48.253001+00:00'
---
## Summary

Organize project Atoms into Outcomes, Specification, and Tickets

## Proposal

The project model has four groups: **Intent, Tickets, Specification, and Implementation**. Implementation includes Documentation.

**UDEQO** is the working name for the five parts of the Specification: UX, Domain, Engineering Design, QA, and Operations.

### Naming options

| What we are naming | Working name | Other options |
|---|---|---|
| What realizes the Specification | Implementation | Realization, Code |
| The Role that specifies technical choices | Engineering Design (E) | Implementation Design (I), Technical Design (T), Implementation Approach (I) |

The Engineering Design name alternatives give **UDIQO** or **UDTQO**, as shown by the letters above.

### Intent

Intent states what the Project aims to achieve and why it matters. It guides the Specification. The Product is the result the Project creates.

Example: Make failed Atom updates easy for AI Agents to recover from. A specific improvement, such as reducing the time callers spend correcting failed updates, can be tracked as a Ticket.

### Specification

The Specification describes what should be. It is one document made of many Atoms. Each Atom owns one contribution with its own Main Subject and Summary.

Start with **expected UX**. Describe what the experience should be like for users and AI Agents. State the guarantees that matter and leave the other design choices to the implementing agent. The Product provides capabilities that enable that experience.

For example, correcting a rejected update should take little effort. The agent can choose a design that lets callers resend only the fields that need correction. Documentation then describes how that feature works in the Product.

| Role | What it specifies |
|---|---|
| UX | The expected experience and the guarantees that matter to users and AI Agents. |
| Domain | The concepts, rules, and processes that govern the work the Product supports. |
| Engineering Design | Architecture, coding rules, internal file structure, and choices about how to realize the other Specification Roles. |
| QA | What to test, evaluate, or lint across the other Specification Roles, and what counts as a pass. |
| Operations | CI/CD, deployment, environments, infrastructure, and resources such as CPU and RAM. |

Specify a stable user-facing filename in UX when users need that guarantee. Document the filename the Product uses. Specify an internal filename in Engineering Design when it matters to the build. An Engineering Design coding rule can apply to QA code. The test case and its pass criteria belong to QA.

Use two Forms in every Specification Role:

- **Invariant** states what must hold whenever it applies. A Declaration is an Invariant that defines an entity, a binding, or a structural fact.
- **Process** specifies a graph of actions. A step can call an Action or another Process with parameters, including a Process in another Role. An Action can be reused. A Step is one use of it.

For example, a Domain Invariant says an invalid Draft leaves the Current Atom intact. A Domain Process checks the Draft before archiving the Current Atom. An Engineering Design Process can specify how to look up the Current Atom. QA specifies the checks and expected results.

A **Template** gives a Form a writing structure. The main candidates are **Business Rule** for a Domain Invariant, **Process** for a Process, and **Task** and **Work Log** for Ticket parts. A **User Story** can specify expected UX and point to the Intent it serves. A **Bug Report** can capture the issue that gives rise to a Task. Its placement is open too.

### Tickets

A Ticket tracks a specific piece of work on an Intent, the Specification, or an implementation artifact. A backlog groups Tickets. Each Ticket contains exactly one **Task Atom** and one **Work Log Atom**. The Task describes the work. The Work Log records what happened and is updated in place as a draft.

The Tickets Role also includes **Analysis Report Atoms**. A report records findings and can stand on its own or link to a Ticket when it supports that work.

Bugs, problems, opportunities, risks, and questions are Issues. Decide whether an Issue is part of a Task or has its own record.

### Implementation

Implementation is the code, tests, configuration, and other artifacts that realize the Specification. Link those artifacts to the Specifications they implement and the Tickets that track the work.

#### Documentation

Documentation describes what exists. It describes the UX the Product actually provides. It records how to use the implemented interfaces, CLI commands, API endpoints, and other public features. This lets the Specification focus on the intended experience and the decisions that shape it. Document the concrete details once the Product implements them.

### Artifacts and ephemeral activity

Specifications are reusable continuant artifacts. Tickets and Analysis Reports are one-shot occurrent artifacts. A Ticket tracks one case through its lifecycle. An Analysis Report records the findings of one analysis. Both can remain as history. Work and Process Runs are ephemeral occurrents. A live Runtime can be an ephemeral continuant.

## Review

- Challenge the partition itself. Compare five alternative role systems. Test them on Intent above the Specification, expected UX within it, domain rules, public and internal filenames, cross-Role Processes, QA, Operations, Tickets, and Implementation including Documentation.
- Give five natural names for each group and Role. Compare Intent, Goals, Value, Outcome, and Product for the group above the Specification. Compare UX, Capabilities, Experience, Output, and Behavior for the user-facing Specification Role. Compare Engineering Design, Implementation Design, Technical Design, and Implementation Approach for the Role. Compare Implementation, Realization, and Code for the artifacts that realize the Specification.
- Review **Form** and **Template** as terms. Check Invariant, Process or Workflow, User Story, Business Rule, Process template, Bug Report, Task, Work Log, and Analysis Report.
- Decide where Issues, Rationales, and Spec Proposals belong. Check how existing Declarations fit the Invariant Form and how other Forms fit before choosing any migration.
