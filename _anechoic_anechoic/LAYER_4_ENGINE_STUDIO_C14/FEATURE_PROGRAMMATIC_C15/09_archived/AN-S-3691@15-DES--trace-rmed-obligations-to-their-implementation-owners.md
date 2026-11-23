---
atom_family: SPEC
atom_id: AN-S-3691
container:
  component: C15
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

Trace RMED obligations to their implementation owners

## Claim

### Prose Claim

Each assessed source module that materially realizes one or more applicable
active Requirement, Evaluation, Delivery, or non-Policy Method (Solution or Decision) Atoms
**must** carry one header comment per Atom before its first code. A narrower set may also appear before an identifiable owning unit when useful. Each comment contains only the current Atom ID
and Version:

```text
# CA-R-2117@13
# CA-M-466@5
# CA-D-674@8
```

Do not add role labels, prose, headings, or an `implementation of` marker. Do
not cite a generic coding Policy merely because it guided implementation, or an
Atom merely called by the source. Many-to-many realization remains valid.

## Details

### Scope

The assessed PROGRAMMATIC implementation boundary: source modules and, when
identifiable, the functions, classes, or other implementation units that
materially realize active Requirement, Evaluation, Delivery, or non-Policy Method (Solution or Decision) Atoms. This includes Tools, Apps, MCP components, and workflows. It
does not automatically include vendor code, generated output, frozen fixtures,
or legacy history.

- A module or unit is an implementation owner only when it materially realizes
  the cited claim. A caller, dependency, test, relation, or projection alone
  does not establish realization.
- The comments are direct trace metadata, not proof of conformance, completion,
  or outcome. The authoritative Atom and observed implementation evidence
  remain required.
- The assessed source boundary applies to current admitted implementation work.
  Out-of-boundary files are reported for explicit disposition rather than
  mass-edited automatically.
- A missing or ambiguous current branch, an unidentifiable owner, or an invalid
  comment is a traceability gap. Preserve the source and report the gap; do not
  invent an Atom ID, parent, policy, or completion claim.

### Retained implementation-trace procedure

To materialize a direct RMED-to-implementation trace, resolve current
applicable authority first and write one header comment for each directly
implemented Requirement, Evaluation, Delivery, or non-Policy Method (Solution or Decision). Each
comment contains only that Atom ID and Version. Do not cite generic coding
Policies merely because they guided the implementation, or an Atom only called
by the implementation.

#### Details

##### Scope

New or materially changed source in the assessed PROGRAMMATIC implementation
boundary, including Tools, Apps, MCP components, workflows, and their owning
modules or units. Vendor code, generated output, frozen fixtures, and legacy
history remain outside automatic editing unless explicitly admitted.

Place the comments before the module's first code. A narrower set may also
appear before an identifiable owning unit when useful. Use the file language's
comment syntax:

```text
# CA-R-2117@13
# CA-M-466@5
# CA-D-674@8
```

Use one Atom per line. Do not add role labels, prose, headings, or an
`implementation of` marker. Preserve the implementation and report a trace gap
when current source cannot resolve, a citation is stale or malformed, or the
owner cannot be identified. Do not invent authority or silently edit excluded
files. The trace does not itself assert conformance, test success, release
readiness, or completion.
