---
atom_family: SPEC
atom_id: AN-S-3182
container:
  component: C61
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3082
state:
  status: draft
  version: 12
  updated_at: '2026-11-25T09:28:03.300533+00:00'
---

## Summary

Resolve authored source relationships

## Guarantee

Given a Project root and its Python import roots, capture and resolve static
Python imports without executing the analyzed Modules. Each import occurrence
records its source location and either its resolved target or its resolution
status.

When the framework-local parsers are installed, resolve JavaScript,
TypeScript, and Svelte imports without running Project source or config.
Report files as unsupported when the parsers are unavailable.

Link a direct `<package>__tests` directory to the named owner when that owner
resolves in the Project.

When the graph build CLI receives the attested Structure, it can resolve Test Packages
to the declared Components they exercise. Report Code Access denials,
uncertain imports, and declared or undeclared owner bypasses from the
captured import sites and declared Package ownership.
Kernel owns publication of the accepted graph.

The ownership check follows named, statically resolved symbols to their
defining Package. Report a forwarding import when the named provider
belongs to a different Package. Allow an entry to expose its own
implementation. The static check requires the reviewed parsers for
each web source it checks.

Compare ordered outputs and side effects from aligned, complete flow
traces in Lean. Report the first difference. Mark incomplete evidence
unresolved. Keep the search prompt with the Lean checker.

Compile a formal workflow from a Tier 1 Solution. Reject overlapping
guards for the same event in one state and states with no path to a
final state. Render every valid transition in Mermaid. Check a complete
recorded flow against the same workflow in Lean.

Report witnessed state access and silent paths for supported code.
Return source evidence and mark incomplete analysis unresolved.

## Claim

### Formal Claim

```python cli
declare_cli_contract(
    interface='build_graph',
    action='import_graph_build_snapshot',
    runner='managed_python',
    module='IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.realization_graph_cli',
    input_fields=('root', 'config'),
    optional_paired_inputs=('structure', 'control_root'),
    output_fields=('nodes', 'occurrences', 'edges', 'test_edges', 'read_issues',
                   'state_effect_findings', 'code_access_findings'),
    checks={'output_format': {'encoding': 'json'}},
)
```
