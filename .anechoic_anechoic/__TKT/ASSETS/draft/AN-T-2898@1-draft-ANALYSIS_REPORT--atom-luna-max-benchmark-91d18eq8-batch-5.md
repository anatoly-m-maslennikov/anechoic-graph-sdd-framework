---
identity:
  atom_id: AN-T-2898
context:
  container:
    component: C00
  tier: 3
  template: Analysis Report
state:
  status: draft
  version: 1
  updated_at: '2026-11-13T17:40:53.457411+00:00'
---
## Summary

Atom Luna max benchmark 91d18eq8 batch 5

## Details

```json
{
  "model": "gpt-6-luna",
  "effort": "max",
  "role_evidence": {
    "query_id": "e540adf1dcd64253bbbb8e7f19911ad7",
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
      "source_ref": "CA-M-542",
      "source_version": 2,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-542",
        "version": 2,
        "summary": "Prefer familiar technologies and interfaces",
        "prose_claim": "Use technologies and interfaces that AI Agents already know. Use a custom technology or interface only when its value justifies the additional learning and maintenance.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-O-10016",
      "source_version": 2,
      "role": "Operations",
      "candidate": {
        "ref": "CA-O-10016",
        "version": 2,
        "summary": "Create an Atom Draft",
        "prose_claim": "This Workflow's Purpose is Runtime. Its scheme follows [CA-R-1570](../../CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1570-CORE_META_MODEL-RULE--keep-workflow-graphs-separate-from-step-bindings.md).\n\n#### Input\n\nThe [Read Workflow input](./CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft/CA-O-10014-PROJECT_CONFIGURATION-STEP--read-workflow-input.md) invocation-port contract accepts either `newAtom` properties or an exact `sourceCurrent` selector with requested property changes.\n\nThe `projectContext` input port binds the Project and applicable Model.\n\n#### Output\n\nThe Workflow returns `savedDraft`, `requested_input`, intermediate results, warnings, or a failure result.\n\n#### Step handoffs\n\n| Step | Receives | Produces |\n| --- | --- | --- |\n| [Read Workflow input](./CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft/CA-O-10014-PROJECT_CONFIGURATION-STEP--read-workflow-input.md) | invocation dictionary and `projectContext` | accumulated `parameters` |\n| [Check Draft input](./CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft/CA-O-10012-PROJECT_CONFIGURATION-STEP--check-draft-input.md) | accumulated `parameters` and `projectContext` | logical `parameters`, `requested_input`, and warnings |\n| [Request Draft input](./CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft/CA-O-10015-PROJECT_CONFIGURATION-STEP--request-draft-input.md) | `parameters`, `requested_input`, warnings, and `projectContext` | supplied corrections, warnings, and intermediate results |\n| [Create the requested Atom Draft](./CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft/CA-O-10013-PROJECT_CONFIGURATION-STEP--create-the-requested-atom-draft.md) | validated caller-bound `parameters`, warnings, and `projectContext` | `savedDraft`, warnings, or a failure result |\n\n#### Logical switches\n\n| Condition | Behavior |\n| --- | --- |\n| Entry | Run Read Workflow input, then Check Draft input. |\n| Check Draft input returns empty `requested_input` | Run Create the requested Atom Draft. |\n| Check Draft input returns nonempty `requested_input` | Run Request Draft input and keep this Workflow incomplete while it waits. |\n| Request Draft input supplies corrections | Run Check Draft input again; that Step defines how to merge corrections. |\n| Create the requested Atom Draft returns `savedDraft` | Complete successfully. |\n| A failure result is returned | Stop and report the explicit failure. |\n\nIf an Action requests more input, return its short explanation and requested input dictionary, then keep the Workflow pending. Resume with the supplied dictionary. Allow cancellation while waiting; cancellation does not interrupt an Action.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-E-684",
      "source_version": 10,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-684",
        "version": 10,
        "summary": "Verify native Workbench workspace, View, and query-log behavior",
        "prose_claim": "Use the real native Codex plugin UI and MCP surfaces. A browser page does not prove native UI behavior. Verify that the host-provided native session opens its isolated Workspace with at least one View for the explicit Project. Verify one read-only Workspace or View operation through the shared backend.\n\nVerify that the native UI, standalone browser, and MCP produce the same Workspace and View effects. Verify that two Codex chats have separate Workspaces and unsaved SQL. Confirm that no standalone chat, synthetic native session, magic Workflow, code runner, scheduler, or retry behavior is required.\n\nIn a disposable protocol host and disposable valid Project, verify that `workspace_open` alone exposes `ui://anechoic/workbench.html`. Verify that the compatibility probe remains separately linked. Unknown resource URIs and unexpected inputs must fail. Verify that the resource is self-contained `text/html;profile=mcp-app` and has no external script or stylesheet references, Workbench HTTP request, browser opening, or second server.\n\nVerify that native bootstrap accepts only the `workspace_open` host tool input's non-empty `session_id`, explicit `project_root`, and initial structured result. Exercise either arrival order for the input and result. Require the exact supplied IDs and initial Workspace, and verify that no second `workspace_open` call occurs. If the input or result is absent, verify that the UI shows a binding error and makes no backend call. Verify that it does not use URL or localStorage identity fallback, a synthetic native session, or an alternative Workspace.\n\nThrough the native MCP transport, exercise every existing Workspace, View, and query-log operation. Each call must retain the exact `project_root`, use one `tools/call`, preserve `structuredContent`, reject `isError`, and reach the shared handler. Check transport binding and error propagation without repeating shared-operation acceptance cases. Native mode must not apply standalone URL, localStorage, or draft-migration behavior.\n\nIn a real new or resumed Codex chat with the installed local plugin and a disposable valid Project and Workspace, invoke the real `workspace_open` with the hook-supplied native session ID and trusted Project root. Verify that Codex renders the Workbench in-chat, that the shown Workspace ID equals the tool input session, and that a read-only Workspace or View operation crosses the bridge. Verify that the state is visible through ordinary MCP or standalone use of the same backend. Verify that no browser, second chat, or second MCP connection appears. Exercise fullscreen or move-to-panel only if the host offers it, and report the observed placement.\n\nA synthetic or disposable-host test proves protocol and application behavior only. It does not prove native Codex rendering, right-panel support, or complete native Workbench delivery. The read-only probe verifies standard MCP Apps compatibility only. It is not evidence that Workbench activation works.\n\nCall the read-only `workbench_ui_probe` through the existing MCP connection. Verify that its component renders inside Codex, displays the initial host tool result, and reports a successful separate `workbench_ui_ping` bridge call. Verify that the resource and tools work over real MCP transport, reject unexpected arguments and unknown resource URIs, and do not start Workbench. Verify inline and fullscreen declarations, current and offered mode display, Expand only when fullscreen is available, accepted, inline-retained, rejected, and unsupported results, the actual returned-mode display, and no unavailable request. If the real host does not render native UI, record delivery as incomplete and do not substitute a browser page. Observe move-to-panel only if offered; otherwise record right-panel delivery as unproven.\n\nUse a fixture whose directory basename differs from its declared Project name. Verify that HTTP and MCP `workspace_open` and `workspace_get` return the declared `project_name`, and that the native Workbench header displays it. Workspace documents must not gain a persisted Project-name field. If the native initial Workspace result lacks `project_name`, verify that the UI reports a binding error before further tool calls and does not fall back to the directory basename.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-469",
      "source_version": 11,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-469",
        "version": 11,
        "summary": "Use a minimal technical Workbench interface",
        "prose_claim": "Build a compact interface with a modern, minimal technical style. Use the available window width. Do not fix the Workspace in a centered column. Reduce repeated headings, chrome, and empty space. Keep controls readable, accessible, and usable at the selected zoom. Show Workbench and Project in the top header. Place Settings and the combined Bookmarks/Saved Tabs at the top-right. Place Tabs below the header. Show hotkey hints in or next to actions.\n\nKeep Settings hidden initially. Order its controls as Theme, Interface text zoom, Content text zoom, Interface zoom, and Density. Default to System theme and 100% for all three zooms. Default to Comfortable density, except use Compact density for the explicit `embedded=1` setting. Only the plugin opener adds `embedded=1`. Do not infer it from screen size or Workspace. A saved browser preference takes precedence over the defaults. Persist Interface text zoom and Content text zoom independently. Each uses 80%, 90%, 100%, 110%, 125%, 150%, or 200%. Interface text zoom affects chrome and headers. Content text zoom affects queries, cells, and full values. Persist whole-interface zoom and Density independently. Text zoom must not change layout or icon scale. When upgrading, apply the old single text-zoom value to both text-zoom settings.\n\nLabel the title input `Query editor`. Put its saved link on the same header row. Make the complete header the only keyboard-accessible Hide/Show editor control. Do not add a toolbar toggle. Open Saved must be a native dialog that is available only from the command palette. Give it autofocus and native paste. Enter opens the selected item without executing it. Escape and Cancel close the dialog. Keep the saved library combined, but distinguish Bookmark and Tab kinds. Retain historical `kind: view` as a compatibility identifier.\n\nUse the shared accessible component palette and the native `Cmd+P` command palette for existing actions and shortcuts. Include Settings, focus, Tabs, query, saved/open, editor, pages/grid, theme, zooms, and density. Provide keyboard navigation. Use the same handlers and availability. Do not add a framework, backend, extra action, or design system.\n\nShow each result column name before its SQL type. Render the type smaller and muted. Keep dark-grid states readable. Render every source newline in cells and full values with pre-wrap. CA-M-492 owns read-only grid, action, group, and cache detail. At 100%, target half the prior 80%-layout height. Do not use a breakpoint framework. Provide Format beside Query editor and in the palette. Use only the canonical formatter.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-E-639",
      "source_version": 18,
      "role": "Evaluation",
      "candidate": {
        "ref": "CA-E-639",
        "version": 18,
        "summary": "Require coherent change readiness before delivery",
        "prose_claim": "A PROGRAMMATIC change is ready for acceptance or delivery only when its known required affected-surface and dependency closure is reconciled as one coherent increment. Resolve known, mechanically checkable omissions in required consumers, contracts, schemas, configuration, dependencies, fixtures, and delivery carriers during preparation. Do not knowingly defer these omissions for downstream acceptance tests to find. An unresolved required obligation is a readiness gap, not a completed or ready result.",
        "details": "### Scope\n\nThis policy applies when preparing and claiming readiness for new or changed PROGRAMMATIC implementation, including descendant Scope Units, before an acceptance or delivery attempt.\n\n- Judge completeness against the applicable governing specification and the actual bounded affected surface. Do not require unrelated Project work, invent business rules, or silently expand the authorized change.\n- Include affected callers and adapters, parser/validator and registry bindings, configuration and dependency realization, test-world inputs, and delivery or packaging boundaries when the change affects them. A valid isolated component does not prove that affected consumers or the delivered realization are coherent.\n- Distinguish a valid verification world from the behavior being evaluated. Known missing fixture or support inputs, contradictory source pins, and an unprepared required execution environment are preparation defects. Do not report their absence as successful behavioral verification. Deliberately invalid targets and intentional red or exploratory tests remain valid when their purpose and expected outcome are explicit.\n- Repair a known shared cause at its canonical owner and reconcile the affected paths. Fixing only the latest symptom does not establish readiness while the cause remains on those paths. Preserve applicable safeguards; do not weaken them to obtain a green result.\n- This policy does not guarantee a defect-free first attempt and does not require every test to pass before any test may run. Unknown defects, exploratory failures, and genuine host or environment failures remain possible. Report them truthfully.\n- Readiness is not permission or completed execution. This policy adds no separate human approval, Journal-history or completeness prerequisite, live-Atom validation, release registry, or extra release workflow. Existing authority, effect, Evaluation-portfolio, and delivery boundaries remain in force.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-407",
      "source_version": 14,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-407",
        "version": 14,
        "summary": "Allocate deterministic transformations to functions",
        "prose_claim": "Use a side-effect-free function as the default unit of PROGRAMMATIC behavior. Implement one deterministic transformation as a function when its result depends only on its declared inputs and the responsibility needs no identity across calls.",
        "details": "### Applicable when\n\nApply this method when Tools, App backend services, or MCP components parse, classify, validate, plan, project, format, or otherwise transform explicit input into a result.\n\n### Procedure\n\n- Use a function unless the responsibility must own mutable state, an invariant across calls, a resource, a lifecycle, or a replaceable adapter.\n- Give the function a specific, intention-revealing verb phrase that states its one responsibility. Prefer clarity over brevity. Split a function whose accurate name requires multiple responsibilities.\n- State the function's input, result, and failure values explicitly.\n- Do not mutate inputs or shared state, perform I/O or logging export, or read the filesystem, process, clock, environment, network, persistence, or randomness.\n- Pass every required observation and setting as explicit input instead of obtaining it implicitly.\n- Group related functions in a specifically named module. Do not create a class only to provide a namespace.\n\n### Outcome\n\nBehavior is locally readable and reproducible from declared input. It has no observable side effects. It can be reused, checked, or extended without constructing component lifecycle state.\n\n### Failure or stop\n\nStop treating the unit as a deterministic transformation when it applies an external effect. A bounded one-shot effect may remain a function under CA-M-425. Allocate an object only when identity across calls, owned state, an invariant, a resource, a lifecycle, or adapter behavior is required.\n\n### Sources\n\n- [Python Functional Programming HOWTO](https://docs.python.org/3.14/howto/functional.html)\n- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)\n- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-415",
      "source_version": 14,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-415",
        "version": 14,
        "summary": "Select Python for applicable PROGRAMMATIC components",
        "prose_claim": "Use Python for applicable PROGRAMMATIC Tools, App backend services, and MCP components. This Method selects Python for that bounded scope. Configuration and Implementation materialize the selected runtime, dependencies, and exceptions. Delivery governs carrier placement and encoding. Operations defines reusable workflow behavior. Journal Records carry evidence required by the existing business-lifecycle contract. This Method does not govern Skills or establish a discipline-independent ANECHOIC meaning of Python.",
        "details": "### Scope\n\nApply this Method when a Tool, App backend service, or MCP component is added or materially changed, or when its Python realization, runtime dependency, or non-Python exception is proposed.\n\n### Procedure\n\n1. Apply the Python selection in this Method and read its current materialization before realizing a component.\n2. Use the standard library when it provides the required behavior with comparable clarity and reliability.\n3. Add or change a runtime, library, workflow tool, or non-Python exception only through an accepted Method that selects it for a bounded scope.\n4. Materialize every accepted selection in canonical Configuration and Implementation. Neither carrier is a second authority.\n5. Place and encode every materialization through its Delivery. Preserve actual execution evidence through its declared owner. Limit Journal writes to the existing business-lifecycle contract. Technical execution does not add hidden Journal effects.\n\n### Outcome\n\nEvery applicable component follows one Method-owned technology selection. Configuration and Implementation reproduce the selection. Delivery locates its carriers. The Journal records required business-lifecycle evidence without taking over selection authority.\n\n### Failure or stop\n\nStop admission or release when no accepted Method owns a required selection, its materialization disagrees with that Method, or the Delivery or Operations boundary is absent. Do not infer a platform-support claim from local execution.\n\n### Sources\n\n- [Python 3.14 documentation](https://docs.python.org/3.14/)\n- [Python Packaging User Guide: `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)\n- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)",
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-468",
      "source_version": 8,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-468",
        "version": 8,
        "summary": "Use a simple SQL editor for Workbench",
        "prose_claim": "Use CodeMirror 6 SQL support and read-only `query_schema({})` metadata. The metadata contains `atoms` name, type, and optional values; `scope_units` name and type; and only `observed_at`, `operation`, `old_path`, and `new_path` from the technical `change_log`. Complete actual tables and declared dotted snake_case `content.*` columns. Use quoted identifiers when needed. Do not read saved SQL for suggestions or expose space-based Content names.\n\nEach Tab holds one query. Preserve quotes, comments, and CTEs. Distinguish delimiters inside them. Under CA-R-2728, send the complete query for Run or Check. CodeMirror provides editing, highlighting, and completion. Cmd+Enter runs the query. Shift+Cmd+Enter checks it. Run & Save saves a snapshot of the complete text only after a successful Run. Completion must not execute SQL, save, or change results. For a single-quoted equality prefix on actual Header Status, offer the metadata value with correct escaping and a closing quote.\n\nFormat with DuckDB dialect `@dlh.io/dlh-sql-formatter` version 1.3.0 through a small token-aware adapter and the existing CodeMirror parser. Use two-space indentation, leading commas, uppercase SELECT, lowercase clauses, and a newline before the semicolon. Attach FROM and WHERE to the following expression unless a comment separates them. Preserve expressions, identifiers, strings, comments, CTEs, and nesting. Apply formatting through the normal editor change path. Accepted formatting must be idempotent. On failure, show an error and preserve the editor and results. Do not add a parser, formatter, or backend capability. Native execution verification remains future work and has not been run.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-D-709",
      "source_version": 1,
      "role": "Delivery",
      "candidate": {
        "ref": "CA-D-709",
        "version": 1,
        "summary": "Deliver shared diagnostic record carriers",
        "prose_claim": "PROGRAMMATIC operational diagnostics must use `=1` shared structured record representation at their declared diagnostic output boundary.\n\n- The delivered record schema represents the context required by CA-M-414 and applicable production fields under CA-D-396. It preserves ANECHOIC-GEN-REQU-315 severity and safety rules. It does not define another field meaning or severity vocabulary.\n- Carry canonical action or Event references unchanged when available. Keep absent references absent; do not invent them for an exporter.\n- Derive concise human renderings and exporter-specific encodings from the record. Do not maintain them as separate diagnostic facts or as schemas with competing meanings.\n- Place production records at the declared Logging Policy sink. The Project Journal is not an alternative diagnostic output Carrier.",
        "details": null,
        "semantics": null,
        "operation": null
      },
      "flags": []
    },
    {
      "source_ref": "CA-M-399",
      "source_version": 20,
      "role": "Method",
      "candidate": {
        "ref": "CA-M-399",
        "version": 20,
        "summary": "Separate Workflow lifecycle records from technical diagnostics",
        "prose_claim": "Send technical diagnostics to structured stdout and stderr streams. Record actual business Workflow lifecycle events through the declared Journal owner. Do not turn a technical warning into a business event.",
        "details": "### Scope\n\nApply this Method to new or changed PROGRAMMATIC implementation, including Tools, Apps, MCP adapters, and their public operation boundaries.\n\n### Procedure\n\n1. Emit technical diagnostics through the shared logger. Include the actual Project prefix and sanitized context. The Docker runtime captures these streams under its bounded retention and back-pressure configuration. Use stderr when stdout carries MCP or Tool protocol or result data.\n\n   For the Project Atom Lifecycle backend, emit a stdout INFO event when each step starts and when it ends as done or failed. Include the step and elapsed time in the end event. Keep input values and carrier contents out of the log.\n\n2. Apply CA-M-396 severity rules. Use WARNING for input and Project artifact issues. Reserve ERROR for actual blocking runtime failures. A response error or failed business Workflow does not by itself require ERROR-level logging.\n\n3. For a business Workflow that is actually admitted and started, record its observed started, failed, and completed lifecycle transitions, as applicable, through its executor and the shared Journal owner. A technical cause may explain an actual business failure. Do not copy technical log records or stack traces into the Journal.\n\n4. If preflight rejects a request and no business Workflow has been admitted or started, do not fabricate a Workflow, Run, started or failed event, or completion event. Direct read-only Tool calls gain no hidden Journal effects from logging or generic error handling.\n\n5. Keep business records truthful and independent of Git and technical-log retention. Journal incompleteness is not an admission gate. Preserve existing historical Journal bytes. Do not rewrite old technical entries as part of this Method.",
        "semantics": null,
        "operation": null
      },
      "flags": []
    }
  ]
}
```
