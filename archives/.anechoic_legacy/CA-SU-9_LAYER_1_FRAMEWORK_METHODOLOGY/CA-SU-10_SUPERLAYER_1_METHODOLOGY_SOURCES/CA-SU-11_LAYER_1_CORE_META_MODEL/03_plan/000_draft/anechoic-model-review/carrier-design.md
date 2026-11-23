# Anechoic Atom carrier proposal

CA-P-3074 task 9 (CA-P-3087). Based on the live `@1-draft` revisions of CA-A-1461 through CA-A-1465 and the Operator's later decisions on Concern migration and status transitions.

## Header

Use Markdown with one YAML frontmatter. Keep `## Summary` in the Body as the source of the filename slug. This Spec example assumes the target Concern exists and the containing Component enables `DES`.

```yaml
---
identity:
  atom_id: AN-S-123
context:
  container:
    component: C43
  tier: 3
  lens: DES
  template: DECISION
concern:
  path: "Model/Graph/Node//Artifact"
  subject: atom
  relation: narrower_than
state:
  status: active
  version: 2
  updated_at: "2026-11-19T00:00:00Z"
---
```

| Field | Rule |
|---|---|
| `identity.atom_id` | Required. `<project prefix>-<S\|T\|P>-<number>`, where the number is a nonempty sequence of ASCII digits. Preserve the exact spelling. The family comes from the ID and is fixed. |
| `context.container` | Required. Exactly one of `component: <Component ID>` and `atom: <stable Atom ID>` records the direct container. Resolve the containing Component through that chain. Reject unresolved targets and cycles. Compute `contained_by` from this field. |
| `context.tier` | Integer when used. Validate locally to the containing Component and the template. Project Goal and Manifest use −1, child Component Purpose and Manifest use 0, and Axioms use 1. Tier 1 is the working placement for a child Component Contract. Applicable Principles use 2. |
| `context.lens` | Optional Project-wide lens name. When authored, it must be enabled by the containing Component's effective whitelist. Represent `DES/DOM` by its unique lens name `DOM` and derive the lens path from the graph. An omitted lens stays absent even where `SPEC` is enabled. |
| `context.template` | Omit when no template applies. When present, use the family-admitted template name. Any required axis or template-specific property is checked by its declaration. |
| `concern` | Optional Header mapping. When present, all three nonempty keys `path`, `subject`, and `relation` are required. Check every hop in the full path and its final relation to the subject. Component Purpose and Manifest identify the described child in their declared content, which supplies their structural Concern. A Component Contract may derive its Concern from its containing Component. Where a template requires an effective Concern, validate that the explicit or structural Concern exists. |
| `relations` | Optional mapping from registered outgoing relation name to a list of targets. Use stable IDs for semantic links and exact revision references for pins. Derive inverse endpoints. |
| `state.status`, `state.version`, `state.updated_at` | Required. Use a family-admitted lower-case status, a positive integer Version, and a timezone-qualified datetime. `draft` and `archived` select their respective groups. In the base review model, SPEC and PMETA admit `active` in Current. TKT admits `backlog`, `active`, `done`, and `canceled`. Only an `active` PMETA Workflow can start a Run. |

Keep template-specific data in the carrier under its declared schema. For `PKG`, persist `context.package_id` explicitly, for example `pkg3344`, and include the short Purpose and Contract in the Body. The package ID binds to the Realization Package, such as `create_order_pkg3344/` immediately below its Component Package. A PKG revision keeps the Spec Atom's own ID when its lens or Summary changes. A single Package may have one PKG Spec identity and several revisions of that identity. The resolved Component, family classification and any template-preset axes are derived. Generate references and file destinations from source fields and relations.

## Revision references

| Input | Selection |
|---|---|
| `ID` | Current for the stable Atom ID, when one exists. |
| `ID@V` | The exact non-Draft revision at Version `V`, either Current or Archived. |
| `ID@V-draft` | The Draft at Version `V`. |

Permit at most one Current per ID, one non-Draft revision per ID and Version, and one Draft per ID and Version. A Draft and an Archived revision at the same Version remain separately addressable. Promotion preserves ID and Version and must reject a collision with an existing non-Draft revision. Moving Current to Archived preserves its exact reference. A Run pinned to `AN-P-9@2` still selects that revision after version 3 becomes Active.

## Filename and destination

```text
filename = marker ["-" lens-token] ["-" template-token] "--" summary-slug ".md"
Current marker  = ID
Draft marker    = ID "@" V "-draft"
Archived marker = ID "@" V
```

Generate suffixes in lens, then template order. Use the source value for each present token. Serialize ASCII token words in uppercase joined by underscores, using the existing structured-token rule. Lens paths never become path separators in a filename. For a printable Summary, collapse each run outside ASCII letters and digits to one hyphen, strip edge hyphens, and lowercase the result. This preserves the existing renderer's result for printable ASCII and also admits Unicode punctuation. Report non-printable input or an empty serialization as a carrier diagnostic. Preserve the original Summary in the Body.

Resolve destinations from the selected Project root. SPEC uses the owning
Component Spec Section, with `draft/` and `archived/` shared across lenses.
Active SPEC carriers go directly in their lens directory, such as `DES/`.

TKT uses `.anechoic_anechoic/__TKT/`. Each of `TASKS/` and `ISSUES/`
holds its Active carriers at the branch root and uses its own `draft/`,
`archived/`, `backlog/`, `done/`, `canceled/`, and `resolved/` subdirectories.
Linked Ticket assets live beside their Ticket and keep their own exact
references. Standalone assets use `__TKT/ASSETS/` with status subdirectories.

PMETA uses `.anechoic_anechoic/_PMETA/` for Active records, with shared
`draft/` and `archived/` directories across its record types. REAL covers
files outside the Anechoic records directory.

Keep container relationships logical. Validate the physical family, status
and applicable lens or Ticket branch. Recompute the basename from the
Header and Body.

## Acceptance examples

Each row shows the exact reference and filename for the stated Header and Summary.

| Family | Group | Exact reference | Filename |
|---|---|---|---|
| SPEC | Current | `AN-S-123@2` | `AN-S-123-DES-DECISION--bound-query-latency.md` |
| SPEC | Draft | `AN-S-123@3-draft` | `AN-S-123@3-draft-DES-DECISION--bound-query-latency.md` |
| SPEC | Archived | `AN-S-123@1` | `AN-S-123@1-DES-DECISION--bound-query-latency.md` |
| TKT | Current | `AN-T-8@2` | `AN-T-8-TASK--review-query-latency.md` |
| TKT | Draft | `AN-T-8@3-draft` | `AN-T-8@3-draft-TASK--review-query-latency.md` |
| TKT | Archived | `AN-T-8@1` | `AN-T-8@1-TASK--review-query-latency.md` |
| PMETA | Current | `AN-P-9@3` | `AN-P-9-WORKFLOW--run-local-release.md` |
| PMETA | Draft | `AN-P-9@2-draft` | `AN-P-9@2-draft-WORKFLOW--run-local-release.md` |
| PMETA | Archived | `AN-P-9@2` | `AN-P-9@2-WORKFLOW--run-local-release.md` |
| PKG | Current | `AN-S-124@2` | `AN-S-124-SWE-PKG--create-order.md` |
| PKG | Draft | `AN-S-124@3-draft` | `AN-S-124@3-draft-PKG--create-order.md` |
| PKG | Archived | `AN-S-124@1` | `AN-S-124@1-SPEC-PKG--create-order.md` |

- The package examples all carry `context.package_id: pkg3344`. `SWE` and `SPEC` are admitted in their respective examples. The Draft has no selected lens and omits that token. Reject a missing package ID, a PKG in PMETA or TKT, and a lens token unsupported by the Header or containing Component.
- Reject Current with `@2` in the filename, Draft with no `-draft`, Archived with `-draft`, and a versioned reference with a filename suffix in the Atom ID. A bare ID selects only its Current; an exact reference without the Draft qualifier never selects a Draft.
- Reject `AN-P-9@2-draft` as a Workflow launch source. Reject promoting it while its `AN-P-9@2` non-Draft slot is occupied. A Ticket's `active` to `done` change preserves ID, Version, exact reference, and basename.
- Reject an S carrier under `_PMETA/` or `__TKT/`, a T carrier under
  `_PMETA/`, and a carrier in the wrong status, lens, or Ticket branch.
  A PMETA extension defining a local Component kind uses a P identity.
- Accept the explicit Concern in the Header above with all graph hops present. Reject its incomplete path `Model/Node//Artifact`, missing `subject`, unknown `relation`, and an empty or null Concern mapping. Accept a structural Concern through the Component graph, with the whole mapping omitted.
- For a synthetic migration case in which two subjects occur in stored order, use the first. If that subject lacks a mechanically mappable complete path, omit `concern` and record the source reference plus the original selected subject verbatim in the migration report. Reject a partial or legacy-specific Concern object in the new Header. If `CA-R-42@2` maps to `AN-S-123@2`, the lookup preserves the identity and Version represented by the exact legacy reference.
- The legacy Current CA-M-537 has the Summary “DRY — Don’t Repeat Yourself.” Its Summary yields `dry-don-t-repeat-yourself`, matching the slug in its legacy filename. A punctuation-only Summary yields an empty slug and fails validation.

## Review decisions

Retain the grouped identity, context, state, and relation conventions. The proposal adds a standalone `concern` mapping and removes derived reference and destination fields from new Headers. It adopts the existing marker and slug conventions where they fit. The current source resolver treats `ID@V` as Archived-only, and current placement rejects negative tiers and adds legacy scope and tier tokens. Anechoic needs the revised selection and filename grammar to admit its exact Current references and Tier −1. Relax the existing renderer's ASCII-input check so observed punctuation cases can migrate mechanically. A Summary with no ASCII alphanumeric characters still needs a reported conversion exception.

The proposal selects lens-then-template ordering, the leaf lens name, a lensless PKG filename when the Header omits the lens, the SPEC status set for PMETA, and status subdirectories without an Atom-container directory dependency. These are review choices for the generated model. CA-P-3075 owns the source inventory and migration.
