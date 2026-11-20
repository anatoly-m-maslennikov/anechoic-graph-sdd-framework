---
atom_family: TKT
atom_id: AN-T-2894
structure:
  container:
    component: C00
  priority: 2
context:
  template: Analysis Report
state:
  status: draft
  version: 1
  updated_at: '2026-11-13T17:38:07.516649+00:00'
---
## Summary

Atom Luna max benchmark 91d18eq8 batch 1

## Details

```json
{
  "model": "gpt-6-luna",
  "effort": "max",
  "role_evidence": {
    "query_id": "adc4bcb7e1bf4aea8b895ffe408d226b",
    "columns": [
      {
        "name": "reference",
        "type": "VARCHAR",
        "has_values": true
      },
      {
        "name": "content.summary",
        "type": "VARCHAR",
        "has_values": true
      },
      {
        "name": "content.claim.prose_claim",
        "type": "VARCHAR",
        "has_values": true
      },
      {
        "name": "content.semantics",
        "type": "VARCHAR",
        "has_values": true
      },
      {
        "name": "version",
        "type": "BIGINT",
        "has_values": true
      }
    ],
    "rows": [
      [
        "CA-R-2508",
        "Declare Atom",
        "Each Atom instance has exactly one outgoing HAS_ACTIVE_SUBJECT link. Its target is the declared entity or instance resolved from Header.Topics.Main Subject. An unresolved Subject is a diagnostic.\n\nFor each Atom instance, the outgoing GOVERNS Relation has cardinality 0..1 and targets only the canonical Subject the Atom governs through its applicable content. These are separate named outgoing permissions and do not grant an inverse or another Relation. The target-omitted bounds count each Atom’s outgoing links within each Relation Declaration’s admissible endpoint domain; they do not create links.\n\nEach Atom instance's outgoing IS_CONTAINED_BY Relation targets the Atom instance or Scope Unit instance selected by its Header.Container.",
        "An Atom is the smallest independently governed Object.",
        13
      ],
      [
        "CA-R-2512",
        "Declare Atom/(.Role := Requirement)",
        null,
        "A Requirement states a required outcome, behavior, property or constraint, or defines a governed model and its constraints. It applies across Aspects, including domain behavior, engineering performance, evaluation effectiveness and delivery reliability.",
        7
      ],
      [
        "CA-R-2513",
        "Declare Atom/(.Role := Method)",
        null,
        "A Method specifies domain and engineering designs, mechanisms or working approaches for achieving required results.",
        7
      ],
      [
        "CA-R-2515",
        "Declare Atom/(.Role := Delivery)",
        null,
        "A Delivery specifies how results are represented, packaged, stored and made available through their Carriers at their intended destinations.",
        7
      ],
      [
        "CA-R-2702",
        "Declare Atom.Header.Role",
        "Role Order Number classifies the Role-qualified Atom kind in the Model. Each Role Declaration assigns exactly one positive integer. Order numbers are distinct across Roles. Gaps are allowed.",
        null,
        3
      ]
    ],
    "row_count": 5,
    "source_row_count": 5,
    "column_count": 5,
    "offset": 0,
    "page_size": 30,
    "has_more": false
  },
  "atoms": [
    {
      "source_ref": "CA-D-463",
      "source_version": 26,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-463",
        "version": 26,
        "summary": "Give each Atom Revision one authoritative Carrier Bundle",
        "prose_claim": "Each Atom Revision must have exactly one authoritative Carrier Bundle on the Project filesystem. The bundle must contain exactly one Markdown File Carrier and may contain zero or more additional Carriers permitted by its applicable Delivery authority. The Markdown File Carrier carries the Atom's own Properties under CA-D-478 and CA-D-479. Each additional Carrier represents the same Revision. It does not replace the mandatory Markdown File Carrier or independently define the Atom's Properties.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-669",
      "source_version": 4,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-669",
        "version": 4,
        "summary": "Keep configuration surfaces in their owning Atoms",
        "prose_claim": "An owning Atom may carry its defined machine-readable Properties in YAML frontmatter. Its ordinary RMED Claim is a zero-value container. It has one or both of these children: Formal Claim and Prose Claim. Each child has zero or one Markdown value. A Formal Claim value contains a CFEL-labelled fence. Frontmatter is not a second Claim or an independent source. Project initialization inputs and applicable ANECHOIC behavior and configuration choices belong to Project Settings. The Project's structural declaration belongs to its Scope Unit Declaration Atom. A non-Project Scope Unit's structural declaration belongs to its Scope Delegation Atom.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-1630",
      "source_version": 41,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-1630",
        "version": 41,
        "summary": "Gate atomic admission and one-step promotion",
        "prose_claim": "The effective atomic admission strictness setting must be either `medium` or `high`.\n\nAt medium strictness, ANECHOIC requires accepted authority, exactly one primary Claim, exactly one enabled Artifact Type, an owning Scope, creation provenance, material relations, priority for Concern Atoms only, and enough precision to establish a stable Artifact identity and initial accepted Revision. Optional, non-authoritative context may remain explicitly unknown.\n\nAt high strictness, ANECHOIC stops before emission while any material authority, definition, boundary, classification, Scope, lineage, Conflict, or Evaluation question remains ambiguous. It asks focused questions until the Atom meets the same one-primary-Claim identity standard.\n\nThe two strictness levels assess one-step promotion eligibility. Promotion is proposed only when the Claim applies unchanged at the broader enabled Scope. Promotion always requires explicit Operator acceptance.\n\nAdmission does not prohibit later Revisions with the same ID. Every later change passes the atomic change-class gate. A change to the primary Claim identity requires a replacement.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-460",
      "source_version": 2,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-460",
        "version": 2,
        "summary": "Write Claims that preserve constraints on active Subjects",
        "prose_claim": "- Keep each Claim on its active Subject.\n- Prefer positive statements that preserve the constraint.\n- Use ancestor rules for inherited constraints.\n- Reuse applicable shared rules.\n- State a permission when it changes an applicable restriction.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-282",
      "source_version": 26,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-282",
        "version": 26,
        "summary": "Derive each filename slug from the complete Summary",
        "prose_claim": "The Summary Slug in every Atom Filename must be the lowercase ASCII kebab-case serialization of the complete Atom Summary.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-309",
      "source_version": 27,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-309",
        "version": 27,
        "summary": "Bind materialized representations to their regeneration sources",
        "prose_claim": "Each admitted materialized representation Carrier must have a recoverable binding to its exact canonical source Revision and exactly one deterministic regeneration or reconciliation rule.\n\nThe binding may be recovered through the selected authoritative source frontier and governing derivation authority. Source metadata does not have to be embedded in every resulting Carrier. An applicable Carrier specification determines whether and how an explicit binding is serialized.\n\nFor Applicable Methodology projected Atom Carriers, CA-D-305 requires an explicit one-way binding to the original source Atom Carrier. The binding must preserve its authored content, identity, and Revision. It must not create duplicate source authority or impose a blanket persisted source frontier on other Projections contrary to CA-R-1494.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-279",
      "source_version": 26,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-279",
        "version": 26,
        "summary": "Put each Markdown prose paragraph on one unwrapped line",
        "prose_claim": "Each prose paragraph in the Main Content of a Markdown Atom Carrier must occupy one unwrapped source line. Put one blank line between adjacent paragraphs.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-1349",
      "source_version": 21,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-1349",
        "version": 21,
        "summary": "Use one Type Property for Type Subjects in an Entity occurrence",
        "prose_claim": "Within one Entity occurrence, all qualified Type Subjects must identify the same Type Property.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-1441",
      "source_version": 26,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-1441",
        "version": 26,
        "summary": "Define Default Settings",
        "prose_claim": "Default Settings means the authoritative Artifact that contains reusable baseline values for registered ANECHOIC Framework Instance Settings parameters. It does not mean Project initialization inputs or a Project's explicit Operator selections.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-1692",
      "source_version": 39,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-1692",
        "version": 39,
        "summary": "Requirement — Freeze a target Version only after its authorized release is recorded",
        "prose_claim": "Each target Version must remain mutable until its selected authorized release event succeeds and the shared Journal records that outcome for the exact released candidate.\n\nThe release record is a factual Journal Record under CA-R-1712, not an Operations Atom.\n\nThe exact manifest binds the released governing Atom Revisions, Implementation and Delivery Revisions, applicable Evaluations and evidence, and the release identifier.\n\nThe selected release policy defines the event boundary. Applicable Delivery authority defines the manifest and Journal representation. A selected Extension owns mechanism-specific references.\n\nPlanning allocation, implementation completion, readiness acceptance, and release-candidate naming do not freeze the Version before the successful event.",
        "details": "This Project Configuration Claim does not require every Project to use this release Workflow.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    }
  ]
}
```
