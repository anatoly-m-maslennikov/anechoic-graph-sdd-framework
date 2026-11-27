# Spec Engine eDSL coverage

## Component layout

- Layer 1 Source Adapters reads pinned Spec carriers through the file Adapter.
- Layer 2 Formal Model compiles the Model manifests and validates instances.
- Layer 2 Project Structure compiles the Project, Component, and Component Seed hierarchy.
- Layer 2 Formal Specification checks Component Boundaries, Contracts, and Solutions.
  Its layers are Diagnostics, Spec Reading, Generation, and Verification.

## Component Manifest and Solution

The parent owns the Tier 1 Component Manifest. Its Header container identifies
the parent. The sections are Summary, Purpose, Component Identity, Component
Boundaries, and Component Contract, in that order. Identity uses the static
`ComponentManifest` constructor. Boundaries use a literal Python mapping.
The Contract section contains the supported Contract fences directly.

The Component owns the Tier 0 Solution. Its `ANSWERS` relation pins the
Manifest revision. Pass the Manifest and Solution pins to
`verify_formal_chain`. Historical three-carrier chains retain their entry
points while existing sources migrate.

The Manifest's boundaries define its frame. The embedded Contract states the
public obligations. CLI executables and internal entry points belong to the
frame or the Solution. Child calls in the Solution use the child's exact
Manifest pin, public Action, and required outcome or guarantees. The child
delegation checks read that Manifest alone and report any unsupported facts.

## Verification profiles

Lean translation validation checks that the generated declarations preserve
the admitted claims. Each comparison entry point supports specific obligations.

| Profile | Manifest Contract and Solution fences | Comparison | Action selection |
| --- | --- | --- | --- |
| Trace | `python trace`, `python` | `verify_formal_chain` checks declared bindings, effects, order and outcomes. | Action name, or all Actions in the profile |
| HTTP | `python contract` with `declare_http_contract`, `python` | `verify_formal_chain` checks the HTTP binding and declared response observations. | Action name, or all Actions in the profile |
| CLI | `python cli`, `python` | `verify_formal_chain` or `check_cli_spec` checks the invocation, declared results, exit codes and trace obligations. | Use the Action to select an operation. |
| Tool API | `python contract` with `declare_tool_api_contract`, `python` | `verify_formal_chain` or `check_tool_api_spec` checks the Tool API request and response obligations. | Optional Solution Action |
| Shape | `python shape` for both | `verify_formal_chain` compares declared record and subtype shapes. | One shape per claim |
| Group | `python group` for both | `check_group_spec` also needs independently selected children. | One group per claim |
| Carrier framing | `python framing` for both | The translator emits framing definitions for dedicated Lean checks. | One framing claim per role |

For a mixed Contract, choose an Action supported by the comparison entry point.
For mixed framing and workflow claims, select `framing` for the bounded byte
comparison or select the workflow by its Action name.
The Workbench workflow CLI uses `--action` to render or replay one workflow.

For a Group comparison, `structure_children` supplies the direct child IDs.
To check the role assignments too, supply `role_providers` selected separately
from the Group claims. Each role supplies `component_id`, the exact declared
`name`, and a `manifest` pin with SHA-256. The check confirms the parent and
child identities and compares each selected role with both Group claims.
`role_provider_coverage` reports incomplete or omitted selections.

HTTP Manifest route maps use endpoint keys such as `"GET /reports"` and
operation names as values. Author new HTTP Contract bindings with `endpoint`
and `route_name`. Existing `route` and `operation` spellings remain readable.
Class shapes are declared in `boundaries.io.class_shapes`.

Use `to` and `expect` in new Solution transitions. Use `same_values` in a
Contract outcome when two named event fields must agree. The concrete
`value_types` clause declares the types of named fields. `nonempty_string`
requires a string with a character Python classifies as non-whitespace.
`nonempty_array` requires at least one item. The concrete
`compare_trace_values` check reports missing fields and malformed event
rows as unresolved. This check uses observations from an execution.

The C45 `query_run` Contract exports its wire schemas as OpenAPI 3.1.
Distinct schemas for the same status appear in `oneOf`. The governed tests
exercise the registry, query delivery, and typed errors through the isolated
Tool API. See `test_generated_http.py` for the pinned test-only command and
`test_openapi_compatibility.py` for compatibility against the approved
`c45_query_run.openapi.json` snapshot from `AN-S-3059@60-draft`. Set
`OASDIFF` to the oasdiff 1.41.0 executable for the compatibility check.
To review a new revision, update the candidate pin. Keep the baseline
snapshot until its replacement is approved.

C45's private `POST /tools` callers and provider ship in the same Studio
image. The MCP process tests cover their interaction. Pact is reserved for
an independently evolving caller of this wire contract.

A declared performance budget stays unresolved until runtime measurements
establish the result under the declared workload and resource limits.
