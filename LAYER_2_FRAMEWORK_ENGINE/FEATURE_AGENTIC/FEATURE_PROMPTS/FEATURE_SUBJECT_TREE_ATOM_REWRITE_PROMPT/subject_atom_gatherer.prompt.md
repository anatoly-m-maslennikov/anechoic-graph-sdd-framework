# Gather Atoms by Subject

## Goal

Gather the complete, pinned source set and parent context needed to rebuild Atoms one Subject at a time. Do not rewrite Atoms or create or update Drafts.

## What to do

Create a work-specific scratchpad under `.caprmedio_tmp` and pass its path to the rewriter.

Read Atoms and model Declarations through CAPRMEDIO MCP `query_run`. If a required section is missing from the query results, record the gap. Keep Header fields separate from the Markdown body in the handoff.

Before drafting a new Atom, gather all Current Active Atoms for its exact Main Subject and every parent Subject. Use this inventory to check what the proposed Atom adds.

1. Use CAPRMEDIO MCP to read the requested root Main Subject, its Subject structure, and the applicable Atom, Role, Form, and Scope Unit model. Resolve `/`, `.`, `//`, and `:=` from parsed Subject expressions and the model; do not infer ancestry from text prefixes or treat structural `<+` as inheritance. Identify every parent Subject, including ancestors above the root, and traverse the selected descendants parent first.
2. If the input selects a Scope Unit tree, include its declared descendants by default; honor an explicit single-Scope-Unit boundary. Exclude temporary burst and test scopes unless explicitly selected. Inventory the selected scope separately from the Subject tree. Group Atoms by exact parsed Main Subject; do not assume every Atom in a Scope Unit shares its Main Subject.
3. For each Subject, retrieve and read every Current, Active Atom whose Main Subject is that Subject. Pin its identity, revision, status, and complete source content. Mark Atoms within the selected scope as rewrite targets and all others as read-only context. Record empty Subjects. If no scope is selected, the selected Subject tree defines the target boundary.
4. Gather the complete pinned Current, Active Atom set for every parent Subject, including ancestors above the root through the direct parent. Include completed parent Drafts supplied by the workflow alongside their Current sources, identifying each Draft, source, and status separately. Do not omit parents outside the selected scope. For example, provide both `atom` and `atom//role` when processing `atom//role: method`.
5. Gather relevant preceding Subject Atoms and Atoms referenced by explicit Topic dependencies and other applicable typed relations of the target set and gathered parent or preceding Subject Atoms. Follow only relations needed to understand the set; do not traverse the whole graph indiscriminately. Resolve relation meaning using the model. Preserve each relation's type, endpoints, direction, and source revision. Pin the referenced Atoms and their complete content. Include an older revision when needed as evidence, clearly labeled historical and distinct from Current sources. Classify external dependencies as read-only context, not rewrite targets or independent authority. Report missing, stale, or ambiguous dependencies.
6. Read the applicable Role and Form definitions and Scope Unit declarations needed to classify the gathered Atoms and check their Main Subjects. Pin their identities, revisions, and source content. Do not infer a Solution's Scope Unit solely from its carrier path.
7. Split all target prose, including the old Claims, into quarks. Each quark contains exactly one statement. Keep wording, actors, conditions, exceptions, and scope. Preserve formal Claims, executable blocks, and ordered sequences intact.
   - Write one pool per Subject. Give each quark an ID and show its text only. Mix quarks across source Atoms and sections.
   - Store a separate lookup from quark ID to source Atom, Version, and section. Keep the pinned source content, Header, and replacement metadata there. The rewriter opens the lookup after the first rebuild.
8. Hand off the pool, lookup path, target boundary, read-only context, and gaps. Keep parent Drafts and pinned authorities with the read-only context. If a set exceeds context, gather it in batches and reconcile the full pool before handing it off.

## Completeness gate

Check the selected scope, parsed Subject ancestry, all Current, Active Atoms for the Subject and each parent, relevant dependencies, source revisions, model authorities, and parent Draft provenance. Check that every source statement is accounted for and every quark has a lookup entry. Report missing or ambiguous inputs and the passages they affect.
