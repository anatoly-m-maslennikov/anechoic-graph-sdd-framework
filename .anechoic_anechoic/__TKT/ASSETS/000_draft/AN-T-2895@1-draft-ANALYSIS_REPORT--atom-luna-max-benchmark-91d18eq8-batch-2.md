---
identity:
  atom_id: AN-T-2895
context:
  container:
    component: C00
  tier: 3
  template: Analysis Report
state:
  status: draft
  version: 1
  updated_at: '2026-11-13T17:40:44.228792+00:00'
---
## Summary

Atom Luna max benchmark 91d18eq8 batch 2

## Details

```json
{
  "model": "gpt-6-luna",
  "effort": "max",
  "role_evidence": {
    "query_id": "d0a2cd6c1cc641d49e195775e1e8ab86",
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
        "CA-R-2514",
        "Declare Atom/(.Role := Evaluation)",
        null,
        "An Evaluation specifies falsifiable checks and how their evidence is interpreted to determine whether required results are achieved.",
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
    "row_count": 6,
    "source_row_count": 6,
    "column_count": 5,
    "offset": 0,
    "page_size": 30,
    "has_more": false
  },
  "atoms": [
    {
      "source_ref": "CA-E-462",
      "source_version": 33,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-462",
        "version": 33,
        "summary": "Evaluate Atom replacement event evidence",
        "prose_claim": "An Event Record offered as evidence of Atom replacement **must** undergo an actual Evaluation against CA-R-807. Available evidence and Journal acceptance do **not** prove that the replacement is correct.",
        "details": "### Checks\n\nThe Evaluation of the Event Record **must** run and report a passing, failed, or unresolved result. It **must**:\n\n- report a failed replacement result **if** a predecessor or successor identity is missing, unresolved, duplicated, self-referencing, or mismatched;\n- verify that **every** named successor was Active **before** the predecessor was archived; verify that the archived predecessor preserves its body, Summary, identity, numeric Version, and prior Updated At, with only its archived Status changed on its Archive Carrier; verify that the retained exact prior Revision bytes include the prior Version, Status, and Updated At; and verify that **`=1`** authoritative Journal Event Record records the replacement;\n- distinguish evidence of the selected Carrier representation from proof that the replacement is correct; and\n- treat repeated submission of the same Event Record as no evidence of another authoritative record.\n\n### Failure disposition\n\nAn Event Record whose actual Evaluation reports failure or uncertainty **must not** be treated as a conforming replacement because the Journal preserves it under CA-R-1491. Its correction disposition **must** route a governed-source change through its authorized Workflow. It **must not** rewrite accepted history.\n\nThis Evaluation **must not** require a Git Commit or a particular Journal serialization. Available evidence without the performed Evaluation and its reported result is **not** a passing result.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-2634",
      "source_version": 2,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-2634",
        "version": 2,
        "summary": "Declare Project.Settings.Authority Modes.Project Authority Mode values",
        "prose_claim": "The permitted values are `strict` and `casual`. The applicable authority-mode resolution determines the effective selection.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-231",
      "source_version": 34,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-231",
        "version": 34,
        "summary": "Derive Navigation Projections from Authoritative Content",
        "prose_claim": "Derive an Atom's navigation values from its authoritative content, not from another navigation value.\n\nTo derive the values:\n\n- For a new Atom, derive its Summary from its finalized primary contribution within its applicability under CA-R-2499 and CA-M-442. For RMED, read the Claim within Scope; do not use Scope alone.\n- Derive **every** requested Projection from its applicable complete source content, including relevant textual applicability restrictions. Do not derive it from the Summary.\n- For an existing Atom identity, retain its Summary and check that it is faithful to the source. A required Summary change follows CA-R-1464 and **must not** be applied as a same-identity refresh.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-E-483",
      "source_version": 21,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-483",
        "version": 21,
        "summary": "Evaluate the ANECHOIC Routing Tree",
        "prose_claim": "The Evaluation of the ANECHOIC Routing Tree registered under CA-R-1640-PROJECT_CONFIGURATION-RULE--register-one-canonical-routing-tree **must** reject a Routing Tree **if** any of these conditions apply:",
        "details": "- its schema is invalid;\n- it has an unknown target;\n- precedence is ambiguous;\n- a route identity is duplicated; or\n- it has an authority effect that is not explicitly declared.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-442",
      "source_version": 5,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-442",
        "version": 5,
        "summary": "Author a scoped Atom contribution and derive its Summary and Translations",
        "prose_claim": "This Method governs authoring an Atom's prose CCE primary contribution, its applicability, and its derived Summary. The same Claim may contain readable prose and an optional R-only nested Formal claim under the Claim definition.\n\nTo author one CCE Claim and its derived Summary, an Author **must** apply these constraints:\n\n1. Express **`=1`** coherent contribution. One precise Summary must cover its full meaning and use the applicable CCE Content Role profile. Put the contribution under the primary contribution heading registered for its Content Role. Do not impose the literal heading Claim on every Role.\n2. Resolve **`=1`** Claim Target Scope Unit independently of ownership. Use the current Scope Unit as the authoring default, or select a different target if permitted. Carry the resolved value under the target Scope Unit carrier definition. Express applicability under the applicability carrier definition. For RMED, state in Scope what the Claim applies to, including applicable conditions and exclusions. Do not merely repeat the carried current or target Scope Unit. These restrictions alone do not make the Atom Relational.\n3. Keep Details within the primary contribution. For RMED, read the Claim within its Scope; Details **must not** change either. **If** supporting content reveals an incomplete or inaccurate contribution or applicability, explicitly revise the affected Scope or primary contribution and recheck their agreement. Do not hide the change in Details.\n4. Write Summary **only after** completing the other body sections and contribution review. Shorten the finalized primary contribution. Use plain wording that expresses the Claim's meaning. Preserve established principle names such as DRY and MECE; do not paraphrase them. A familiar name or short instruction **may** be the Summary; do not force a declarative sentence. For RMED, summarize the Claim within its finalized Scope, **not** Scope alone. Do not use supporting Results or TLDR as the source.\n5. For an existing Atom, retain the established Summary and check its faithfulness. **If** it needs to change, use a new Atom identity under the Atom identity rule.\n6. Derive **every** Translation from the full corresponding source content, **not** the Summary.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-1635",
      "source_version": 42,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-1635",
        "version": 42,
        "summary": "Require Production Evaluation Checklists for production readiness",
        "prose_claim": "**Every** production-relevant component or governed scope **must** define a Production Evaluation Checklist **before** it can pass a production-readiness gate. The checklist states how operators can determine during real work whether the realized system remains healthy, correct, supportable, and within its accepted operating boundaries.\n\n**Every** operational condition or invariant **must** be owned by one `evaluation_control` Atom. The control identifies:\n\n- the Requirement, Demand For, Constraint, Method, or other governed Claim it assures;\n- the production signal and authoritative data source;\n- the healthy condition, expected range, threshold, or failure predicate;\n- the evaluation window, cadence, and permitted detection delay;\n- the component, entity, lifecycle state, or workflow boundary to which it applies;\n- the accountable owner and escalation destination;\n- the alert, incident, investigation, degradation, rollback, or recovery action triggered by failure;\n- the diagnostic context needed to investigate the condition;\n- the required factual execution record and evidence-retention boundary; and\n- known blind spots, sampling limits, unavailable signals, and other evaluation limitations.\n\nA Production Evaluation Checklist is a Catalog Projection over the applicable `evaluation_control` Atoms. It organizes and navigates those controls without absorbing, paraphrasing, or replacing their Claims. It does not acquire the Content Role of its source Atoms.\n\n**Every** control distinguishes its governed meaning from its realization and results:\n\n- The Evaluation Control defines the production evaluation condition.\n- Monitors, dashboards, alerts, health checks, and operational automation are Implementation.\n- Recorded metrics, logs, traces, alerts, incidents, and check outcomes are factual execution records, **not** reusable Operations definitions.\n- A Concern Atom of Type `problem` records a material discrepancy that requires disposition.\n\nA Production Evaluation Checklist presents the applicable controls for real production operation without becoming their authority. It is **not** a QA Case. Passing pre-release Test or Evaluation implementations does **not** by itself satisfy the production-evaluation obligation.",
        "details": "Pre-release QA demonstrates behavior under bounded conditions. Production Evaluation **must** detect degradation, incorrect state, and supportability failures during actual operation. Atomic controls preserve independent lifecycle and replacement. The checklist provides a navigable scope view without conflating definitions, implementations, and observations.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-704",
      "source_version": 6,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-704",
        "version": 6,
        "summary": "Deliver code-owned MCP registration in the installed package",
        "prose_claim": "The MCP package carries `tool_providers.json` as its code-owned provider inventory, `generate_tool_registry.py` as its generator, and `tool_registry.json` as its generated runtime registration asset in `FEATURE_MCP`. The generator accepts `--package-root`. It reads the inventory and installed provider code. It does not read Project Atom carriers or execute a capability. Equivalent installed inputs produce equivalent bytes by using canonical descriptors, models, and adapters.\n\nIn refresh mode, generate the asset in the staged package before final inventory verification and image build. In existing mode, copy the checkout asset unchanged. Include the asset's bytes in the package and image identities. A missing asset or failed refresh stops delivery before startup. Direct source development uses the same asset and generator. Do not add a daemon, watcher, Workflow scheduler, or Atom fallback.\n\nThe inventory carries provider keys, implementation and factory symbols, descriptor factories, and an explicit global `mcp_blacklist`. The generated data carries resolved provider and Tool registration and exclusions. Keep these as configuration files, not as a fixed Python Tool-name list.\n\nThe installed adapter distribution keeps its version-bound interface declaration at the existing MCP Delivery location. Use canonical descriptor and model symbols. Preserve protocol revision, capability, and result meanings. The declaration carries the supported protocol revision and capabilities, admitted progress, cancellation, correlation, and resource-bound fields, and existing result meanings. Derive its descriptor schema only from installed canonical model symbols. Do not accept a caller-supplied descriptor schema. Keep declarations, schemas, and examples credential-free.\n\nRegistration, schema derivation, projection, and refresh do not invoke a capability, start a Workflow, or infer approval. Registration and schema generation grant no effect permission.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-1008",
      "source_version": 1,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-1008",
        "version": 1,
        "summary": "Use one Gateway for HTTP and stdio",
        "prose_claim": "Use the same MCP Gateway handlers and Tool registration for HTTP and stdio. The installed runtime provides the same Tool behavior over both transports.",
        "details": "Use the installed MCP SDK's Streamable HTTP application for HTTP Sessions. Close Sessions on shutdown. Apply code and compiled contract changes by starting a rebuilt runtime under CA-M-551.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-E-357",
      "source_version": 23,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-357",
        "version": 23,
        "summary": "Reject PROGRAMMATIC objects without persistent ownership",
        "prose_claim": "#### Claim checked\n\nAdmit one PROGRAMMATIC object **only when** it requires identity across calls **and** owns state, an invariant, a resource, a lifecycle, or a replaceable adapter.\n\n#### Test case\n\nEvaluate one changed object that **only** wraps a bounded one-shot effect and owns no responsibility across calls.\n\n#### Acceptance criteria\n\nPass **only when** the object is rejected and the effect is allocated to a specifically named bounded function.\n\n#### Failure disposition\n\nReject the object until persistent ownership is demonstrated or its wrapper is replaced by a function.\n\n#### Sources\n\n- [CA-M-408 — Allocate owned state and lifecycle to objects](../05_method/CA-M-408-PROGRAMMATIC-ENG_POLICY--allocate-owned-state-and-lifecycle-to-objects.md)",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-E-451",
      "source_version": 23,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-451",
        "version": 23,
        "summary": "Require a named benefit for a new runtime-dependent Python idiom",
        "prose_claim": "Reject a runtime-dependent Python idiom adopted only for novelty unless it has a named benefit within its supported boundary. A t-string that replaces a trusted immediate f-string fails if it has no processor or lacks a correctness, clarity, safety, or measured-performance benefit.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    }
  ]
}
```
