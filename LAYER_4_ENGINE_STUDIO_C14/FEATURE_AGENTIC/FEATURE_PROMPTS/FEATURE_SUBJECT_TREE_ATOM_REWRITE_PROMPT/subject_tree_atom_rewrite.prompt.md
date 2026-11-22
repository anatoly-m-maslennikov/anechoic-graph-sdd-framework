# Rebuild Atoms by Subject tree

## Goal

Rebuild each gathered Subject's active Atom set from its source wording. Use parent and dependency Atoms as context. Preserve meaning unless the input requests a change.

Target at least 10:1 by raw file bytes across the selected Scope Unit tree. Count implementation source bytes and full Current RMEDO Atom bytes, including YAML Headers. Exclude tests, generated assets, and benchmark fixtures.

## What to do

Reuse the gatherer's scratchpad under `.anechoic_tmp`. Create one when useful if the gatherer did not. Keep rewrite notes and review findings there.

Use ANECHOIC MCP `query_run` for Atom reads and the MCP Atom Lifecycle tools for Draft writes. Pass only Markdown in `body`, starting with `## Summary`. Pass Header changes as structured fields. Check that the body has no YAML Header before writing. After writing, verify the Draft reference, status, and Content through MCP.

1. Obtain the Subject's quark pool, source lookup path, and read-only context from `subject_atom_gatherer.prompt.md`. Process parent Subjects before children. Report missing inputs.
2. Read the pool and use the parent, dependency, and model context. Open the source lookup only after the first rebuild. Keep the quark IDs in your grouping so you can trace the new Atoms later.
3. Classify each quark by what it says:
   - **R** covers required domain behavior and outcomes, including internal behavior.
   - **M** covers implementation choices.
   - **E** covers checks, test conditions, and expected evidence.
   - **D** covers carriers and interface contracts.
   - Use the applicable model for other Roles. **O** covers Actions and Workflows.
4. Group quarks by contribution, Role, and Form. Choose main points across the whole pool and move each supporting quark to the point it supports. Keep wording changes small.
   - Set aside exact repeats when meaning, scope, and conditions match. Confirm their owners during review.
   - Keep distinct checks and boundary cases. Combine cases that verify the same behavior. Use a representative example where it explains the rule.
   - Keep supporting quarks that affect the decision, behavior, or acceptance criteria. Apply the Details limits below.
   - Once Details are settled, rebuild the Claim from the chosen main point and its supporting Details.
   - Rebuild the Summary last, from the finished Claim and Details. Check the Main Subject and each Solution's Scope Unit Declaration. Preserve dependencies unless the input or model requires a change.
5. Open the source lookup. Verify the pinned sources through MCP. Compare source and result in both directions. Map each quark to the Draft, its verified owner, or an authorized change. Record moves, merges, and splits. Repair gaps. Preserve source meaning and mark a Draft provisional if uncertainty remains.
   - Before adding an Atom, check the complete Current Active set for its Main Subject and parent Subjects. State only the new contribution. Skip the Draft when existing Atoms already cover it.
6. Use the MCP Atom Lifecycle to create or update in-scope Drafts. For a provisional Draft, reserve the final tier-1 Details slot for `### Proposal`. Mark the Draft provisional and point to the open questions in the scratchpad. For each question there, record the proposed answer, source revisions, and effect, then pass it to the Operator. Use `IS_REPLACEMENT_FOR` to link new Drafts to their source Atom IDs. Record each source-to-Draft mapping, including splits, consolidations, unchanged sources, subject corrections, and open questions. Supply parent Drafts and pinned Current sources to the gatherer with their review status. Use Current authority for unresolved parent decisions. Leave Current and out-of-scope sources unchanged.
7. Size batches to fit context. Reconcile the whole pool before rebuilding. In a handoff, pass the pool, source lookup path, context, completed work, and unresolved questions. Keep the source lookup closed until the first rebuild is ready.

## Writing

- Stay close to the Operator's wording. Use ASD-STE100-aligned prose with short sentences, common words, and exact model terms.
- State the rule directly. Say “all Roles” when it applies to all Roles. List only meaningful distinctions.
- Follow the Markdown structure declared for the Role and Form. Count lines in the Markdown source.
  - **Claim.** At most 3 lines of text across the whole Claim, including formal expressions when present. State the main point and its limits in the Claim. Refer to each tier-1 detail in a short phrase when it helps state the Claim.
  - **Details.** At most 3 tier-1 details. Each may have up to 2 tier-2 details. Stop at tier 2. Each detail has at most 2 lines of its own. Use a subtitle for a tier-1 detail with supporting details, and nest those details under it. Put standalone details directly under `## Details`.
- Keep other paragraphs to at most 3 lines and other list items to at most 2.
- Record architectural and other decisions and the constraints that shape them. Leave routine coding instructions and details the implementing Agent can infer from existing code to that Agent.
- By default, write Requirements and Decisions as static invariants. State what must hold, including any conditions. Put ordered steps in an Operations / Workflow.
- **Method / Decision.** Aim for 5 lines of content, with a maximum of 7. Record the engineering choice and any constraints that would change it.
- **Evaluation / Eval Case.** Describe functional scenarios and expected observable results. Leave unit-test cases and mechanics to the implementer.
- In a rewrite, record what was cut and why. If a cut would remove a distinct obligation or acceptance condition, keep it with its owner or flag it for review.

## Internal gate

Before writing a Draft, check the Claim and Details limits. If the material meaning cannot fit, flag it for review.

Report the baseline and projected size ratio for the selected scope. For the projection, count each Draft once in place of the Current Atoms it replaces. If it misses 10:1, report the gap and what would have to change.

Check complete active-set, parent-context, and dependency-context coverage, target boundaries, parent-first traversal, and the set-wide source-to-result mapping. Compare all material meaning and applicability in both directions; check authorized changes, Role and Form compliance, required sections, Main Subject and Summary alignment, references, and executable content. Correct and recheck issues. An open question permits a provisional Draft and keeps the gate open. Report which Drafts passed and which still need a decision.
