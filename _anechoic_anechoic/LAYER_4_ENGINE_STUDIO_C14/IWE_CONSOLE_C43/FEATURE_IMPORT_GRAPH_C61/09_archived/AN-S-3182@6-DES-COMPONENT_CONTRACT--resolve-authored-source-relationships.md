---
atom_family: SPEC
atom_id: AN-S-3182
container:
  component: C61
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: archived
  version: 6
  updated_at: '2026-11-22T17:21:23.736557+00:00'
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

The Graph build CLI returns the resolved rows and read issues as JSON.
When it receives the attested Structure, it can resolve Test Packages
to the declared Components they exercise. Report Code Access denials,
uncertain imports, and declared or undeclared owner bypasses from the
captured import sites and declared Package ownership.
Kernel owns publication of the accepted graph.

The ownership check follows named, statically resolved symbols to their
defining Package. Report a forwarding import when the named provider
belongs to a different Package. Allow an entry to expose its own
implementation. The static check requires the reviewed parsers for
each web source it checks.

## References

AN-S-3082 and AN-T-2947.
