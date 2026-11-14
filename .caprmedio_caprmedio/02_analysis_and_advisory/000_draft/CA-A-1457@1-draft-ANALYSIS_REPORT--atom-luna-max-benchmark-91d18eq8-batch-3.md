---
identity:
  atom_id: CA-A-1457
  ref_id: CA-A-1457@1-draft
context:
  role: analysis_and_advisory
  form: Analysis Report
  tier: 3
  topics:
    main_subject: CAPRMEDIO_STRUCTURE <+ Aspects <+ Engineering <+ Development <+
      Authoring
  container:
    scope_unit: CA-SU-00
state:
  version: 1
  status: draft
  updated_at: '2026-11-13T17:40:47.493476+00:00'
destination:
  file:
    name: CA-A-1457@1-draft-ANALYSIS_REPORT--atom-luna-max-benchmark-91d18eq8-batch-3.md
    path: .caprmedio_caprmedio/02_analysis_and_advisory/000_draft
---
## Summary

Atom Luna max benchmark 91d18eq8 batch 3

## Details

````json
{
  "model": "gpt-6-luna",
  "effort": "max",
  "role_evidence": {
    "query_id": "27ebb642b3d24615996df9eb3ad36beb",
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
        "CA-R-2463",
        "Declare Operations",
        null,
        "An Operations Atom specifies work to perform and how it is coordinated, including its sequence, inputs and outputs.",
        7
      ],
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
      "source_ref": "CA-E-563",
      "source_version": 14,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-563",
        "version": 14,
        "summary": "Verify golden E2E preparation before implementation",
        "prose_claim": "The Implementation passes this Evaluation only when golden E2E cases, selected E authority, and runnable baseline evidence exist before behavior implementation.",
        "details": "### Scope\n\nThis Evaluation checks test-first preparation for one bounded implementation packet.\n\nAn expected initial failing case is a truthful non-pass. It uses zero retries. Mocked external boundaries do not replace the selected behavior under test.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-E-287",
      "source_version": 19,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-287",
        "version": 19,
        "summary": "Distinguish one protocol failure from one Tool failure",
        "prose_claim": "MCP returns stable, model-readable responses that distinguish a protocol failure from a canonical Tool failure.",
        "details": "### Test case\n\nProduce one invalid protocol message and one valid message whose canonical Tool returns a structured failure.\n\n### Acceptance criteria\n\nThe two responses are distinct. They retain applicable provenance. They expose no internal implementation detail.\n\n### Failure disposition\n\nReject the result adapter until it preserves this distinction.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-181",
      "source_version": 15,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-181",
        "version": 15,
        "summary": "Run host-capable Candidate E2E\n\n## Action\n\nRun host-capable Candidate E2E means one explicitly authorized host-capable controller execution against the exact candidate image, package, source frontier, and N/N+1 bindings in CA-O-186.\n\n## Details\n\nThe host-capable Candidate E2E inventory is the current runtime-test set under `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/tests/`. Every declared testcase in that selected runtime-test set must terminal-pass. A skipped, excluded, missing, or zero-coverage testcase is a non-pass. The frozen Docker worker has no Docker socket and cannot claim this phase. A registered, explicit host-capable controller and its exact declared capability are required. A missing, denied, unsafe, unavailable, stale, non-passing, or unjournalable capability produces its actual non-pass outcome.\n\nThis Action never selects N+1, promotes, retires, mutates sources, expands mounts, exposes credentials, or substitutes a cached or focused result. It records one recoverable Journal result. The result is bound to the exact candidate and image identity.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-165",
      "source_version": 23,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-165",
        "version": 23,
        "summary": "Validate local release inputs\n\n## Action\n\nValidate local release inputs is the Action that checks the explicit local-release inputs and configured delivery paths for file and path safety before the declared local validation scope runs. The complete discovered suite remains the default. A focused scope requires the explicit current Operator record admitted by CA-O-164.\n\n## Scope\n\nThe Action checks the configured source and delivery paths, Project Structure, protected settings, compiler, and target paths `LAYER_1_FRAMEWORK_METHODOLOGY/` and `.caprmedio_caprmedio/000_CAPRMEDIO_framework/` for ordinary input and file and path safety. It does not separately validate Active Atom metadata, placement, or relations. Release verification uses the declared scope and records whether it is complete or focused.\n\n## Details\n\nMissing, ambiguous, or unsafe required input stops the Action before tests or delivery writes. The Action reports the issue for manual handling. It does not copy or clear product or installed contents, compile, install, push, or open a PR.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-190",
      "source_version": 11,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-190",
        "version": 11,
        "summary": "Discover a matching public `main` PR\n\n## Action\n\nDiscover a matching public `main` PR is the native read operation that returns zero or one actual open PR identity for the selected personal remote and the `amm/dev`-to-`main` boundary.\n\n## Details\n\nThe Tool-call input, result, and report references are evidence of this Action Run. The Action does not create or update a PR. It does not claim an MCP route.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-491",
      "source_version": 15,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-491",
        "version": 15,
        "summary": "Deliver the VALIDATE_ATOMS command\n\n## Scope\n\nThis Decision covers the `VALIDATE_ATOMS` command Carrier and its delivered test assets in TOOLS.\n\n## Claim\n\nThe `VALIDATE_ATOMS` executable Carrier must be delivered as `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS/validate_atoms.py`, with its automated tests in the adjacent `tests/` directory.\n\n- Expose `validate_atoms.py --input <request.json>` and `--input -` for standard input.\n- Emit **=1** JSON result on standard output under CA-D-493-TOOLS-ENG_DECISION--serialize-atom-validator-results. Put human execution diagnostics on standard error.\n- The path identifies an Implementation Artifact inside TOOLS, not a newly declared Scope Unit. It carries the implementation bound under CA-R-1622-TOOLS-RULE--implement-atom-carrier-validation-in-validate-atoms, not another Workflow authority.\n- Store the end-to-end command tests in `VALIDATE_ATOMS/tests/test_validate_atoms_e2e.py` relative to the delivered TOOLS directory.\n- Store mock Markdown Atoms and supporting mock context in `VALIDATE_ATOMS/tests/fixtures/`, with `good/`, `bad/`, `mixed/`, and `context/` groups. These fixture files are test inputs, not active governing Project Atoms.\n- Store the case and coverage manifest in `VALIDATE_ATOMS/tests/cases.json`. Store independently reviewed expected reports in `VALIDATE_ATOMS/tests/expected/<case_id>.json`. Each manifest case identifies its fixture inputs, request, governing rule identities and Revisions, expected report, and expected exit code.\n\n- `cases.json` is a closed object with `schema_version: 1` and `cases`, a nonempty array. Each case has a unique, nonempty `case_id`; a `request` path; a nonempty `fixture_paths` list; a nonempty `authority` list of exact Atom Bindings under CA-D-492-TOOLS-DELIVERY--serialize-atom-validator-requests; a nonempty `check_codes` list; an `expected_report` path; and an integer `expected_exit_code` in (0, 1, 2, 3). All case paths are relative to `tests/`, stay inside it, and cannot escape through symlinks. Expected reports follow CA-D-493-TOOLS-DELIVERY--serialize-atom-validator-results.\n- Include positive, negative, exception, and boundary coverage for every supported check and declared failure class. Reusable fixture cases may cover multiple rules. The harness verifies the matrix against the independently resolved obligation inventory, not only the implemented checks.\n\n## Details",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-1880",
      "source_version": 18,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-1880",
        "version": 18,
        "summary": "Preserve the prior release and report failures truthfully",
        "prose_claim": "Release Version must preserve the prior runtime until its prepared replacement is ready. It must report actual effects and failures truthfully. It must never replay an uncertain effect automatically.\n\nAfter a successful replacement and Project-MCP readiness, Release Version must retire only verified superseded release-owned images for the current Project. Retirement is allowed only when each image's exact immutable identity and ownership are known and no container or protected reference retains it.\n\nLocal Release must support rebuilding the Engine from a known-good checkout and its generated assets, even if the current service cannot start or the prior image has been removed.",
        "details": "Preserve the current image, unrelated images, images for other Projects, and protected images. Establish current-Project ownership from actual build, launcher, or start evidence that contains the immutable image identity and Project identity. Check this evidence against Docker inspection. A tag prefix alone is insufficient. Cleanup includes the exact prior image when eligible and reports whether it was removed, protected, in use, or unproven. Do not force-remove containers or claim complete cleanup when ownership or use remains uncertain.\n\nIf a failure follows a real effect, report the partial state and failed step for manual handling. Do not claim automatic rollback, restore a retired runtime selector, or replay an unknown effect. A request, test result, or prepared package does not mean that release succeeded. Preserve source data and unrelated configuration. No failure permits broad image pruning.\n\nJournal records describe what happened. Earlier records, baseline rows, terminal-recording recovery, and proof receipts are not prerequisites for a release or its first recorded change. A missing Journal record does not undo a real effect or change its outcome.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-518",
      "source_version": 16,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-518",
        "version": 16,
        "summary": "Register the RMED_ATOMS_BASE_REVISE discovery binding\n\n## Scope\n\nThis Decision covers the TOOLS capability for Tool/RMED_ATOMS_BASE_REVISE/Carrier.\n\n## Claim\n\nThe discovery binding for RMED_ATOMS_BASE_REVISE must be carried in the following TOML table in this Atom's Details.\n\n## Details\n\n```toml\n[tool_binding]\nname = \"RMED_ATOMS_BASE_REVISE\"\nentrypoint = \"LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/RMED_ATOMS_BASE_REVISE/rmed_atoms_base_revise.py\"\naction_ids = [\"CA-O-105\", \"CA-O-106\", \"CA-O-111\"]\nworkflow_ids = [\"CA-O-104\"]\nmcp_name = \"rmed_atoms_base_revise\"\n```\n\nThe binding registers the existing Implementation. `action_ids` identify the bounded selection, evaluation, and repair Actions that it carries. `workflow_ids` retains CA-O-104 as workflow context only. It does not map CA-O-104 as an Action or define an independent Workflow Run engine. Unavailable paths or bindings are explicit discovery findings.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-R-1623",
      "source_version": 10,
      "role": "Requirement",
      "candidate": {
        "ref": "CA-R-1623",
        "version": 10,
        "summary": "Keep Atom validation execution bounded and read-only\n\n## Scope\n\nThis Rule applies to `VALIDATE_ATOMS` Implementation invocations within their admitted input context.\n\n## Claim\n\nThe `VALIDATE_ATOMS` Implementation must keep every invocation read-only and bounded by its admitted input context.\n\n- Permit bounded inventory enumeration and the minimum candidate content needed to determine selection inside declared source roots and allowed read roots. Inspect an excluded candidate only for selection. Exclusion does not permit full validation or add the candidate to target coverage.\n- Read selected targets, applicable authority, and necessary reference inputs only inside admitted read boundaries. Reference resolution does not expand the target set.\n- Enforce actual read permissions and protected-file exclusions before reading content. Caller-supplied roots grant no permission. Do not follow a link outside admitted boundaries, fetch remote resources, inspect secrets, or execute YAML tags, Markdown, selectors, rule bundles, or Atom instructions as code.\n- Enforce selected resource limits. Exhaustion must yield incomplete or error, not a pass. Isolate a malformed candidate so independently checkable candidates remain reportable.\n- Do not write, rename, remove, or repair source files, Projections, Settings, caches, or Journal files. The caller or executor owns any admitted persistence of returned Run evidence.\n- Preserve exact invocation definition and input bindings. Report a changed source instead of silently validating mixed Revisions.\n\n## Details",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-E-633",
      "source_version": 14,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-633",
        "version": 14,
        "summary": "Verify private carrier storage changes\n\n## Scope\n\nDefine the required, falsifiable cases for CA-R-1941, CA-D-630, and O215/O216/O217. Use independently authored expected requests and before/after ledgers. No tests are claimed to have run.\n\n## Claim\n\nThe private variant passes only if its explicitly admitted storage result and preservation frontier are independently verified. Missing or contradictory evidence is unresolved or a failure. It never supports a pass or an effect that did not occur.\n\n## Details\n\n### Fixtures and accepted cases\n\nPrepare a bounded temporary root with a file, an empty folder, a nested folder with a complete explicit inventory, an unrelated sibling, an occupied destination, symlinked source, ancestor, and destination, an escaping locator, and a deliberately substituted entry. Supply independent identity, type, content, mode, parent, and permission evidence, plus the exact expected map. Do not derive expected output from the helper.\n\n- Rename a file and an explicitly inventoried folder within the same parent. Require the exact requested new binding, source absence, preserved contents, modes and inventory, and unchanged unrelated entries.\n- Move a file and an explicitly inventoried folder to the exact bound destination. Require source absence, the exact destination, and preservation evidence. Any basename change must be explicit in the approved binding. An inferred rename or merge does not pass.\n- Remove one explicitly approved non-Atom file and one independently confirmed empty non-Atom folder. Require observed absence and unchanged unrelated, protected, and history carriers. No child-removal effect is admitted.\n\n### Exclusive-window fixtures\n\nSupply the exact staged location and absence change, independently resolved private bindings, the complete affected frontier, and a genuine recorded selected Session/Action. Bind the Operator's reviewed change and recorded outside-edits-paused confirmation through the existing trusted authorization binding. Do not use a caller flag, JSON- or hash-derived approval, or an arbitrary approving callback.\n\nRun the accepted cases above within the confirmed exclusive window and collect independent before/after evidence. Raw-helper successes and tests that only verify refusal do not establish positive receiving acceptance.\n\nChange the bound evidence before final revalidation. Require refusal without a Carrier effect. Refuse missing, stale, mismatched, or fabricated review or window confirmation before effects. Require no project-wide Engine write lock or replacement. Other Engine writers are not excluded. A writer that ignores the confirmed window is outside this model. Do not claim that a last-moment check prevents that race.\n\n### Refusal and uncertainty cases\n\n1. Reject an unknown private variant, public physical path target, malformed binding, missing permission, unresolved roots, root or ancestor target, escape, missing or ambiguous source, wrong kind, and stale source, parent, or destination state. Require no effects.\n2. Reject every symlink or substitution case, destination collision, occupied distinct destination, source-subtree or invalid-overlap destination, overwrite proposal, and merge proposal. Include changes after preview. Do not report a refusal as success.\n3. Add, remove, or substitute a folder entry after its approved inventory. Reject the changed frontier; do not expand it. Reject nonempty-folder removal even if the caller supplies a recursive flag or wildcard. Unknown fields fail.\n4. For removal, reject current or archived Atom carriers, required history, protected sources, and malformed or uncertain classification. The absence of a recognizable Atom ID alone does not establish non-Atom eligibility.\n5. Supply an internal carrier move from an admitted Atom lifecycle context. Verify only the private storage contribution. The helper does not choose lifecycle metadata or claim that the Atom transition completed. Reject missing or stale lifecycle or history context. Compare every referrer's bytes before and after. Neither rename nor move may invoke O040 or rewrite references.\n6. Treat an already satisfied, unchanged rename or move request as a no-op only with current evidence. A missing expected-present source is a failure, not proof of a prior effect. For removal, treat a bound, already-absent cleanup state as a no-op only when that exact absence was expected and permission and eligibility remain valid.\n7. Inject effect, readback, and verification failures. Preserve attributable, known partial effects. Unknown effects require `effect_uncertain`. Nonempty errors cannot indicate success. An exception-free, unverified result cannot return empty errors. A no-op must prove that the requested state is unchanged.\n\n### Acceptance and disposition\n\nCompare the exact independent before, proposed, and after ledgers; resolved bindings; and actual effect and error evidence. Any widened set, hidden reference or lifecycle decision, lost preservation evidence, or false completion rejects the realization. Retain unresolved evidence and known effects, including a failed verification after an effect. Unknown effects require `effect_uncertain` and no automatic retry. Reuse only the approved exclusive-window boundary. Do not infer automatic rollback, a cleanup restoration promise, retry, resume, replay, or a stronger concurrent-publication guarantee.\n\nThese are Rules and isolated test-fixture requirements only. They do not establish live cleanup or production activation. This source specifies future functional checks, not packet acceptance.",
        "prose_claim": null,
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    }
  ]
}
````
