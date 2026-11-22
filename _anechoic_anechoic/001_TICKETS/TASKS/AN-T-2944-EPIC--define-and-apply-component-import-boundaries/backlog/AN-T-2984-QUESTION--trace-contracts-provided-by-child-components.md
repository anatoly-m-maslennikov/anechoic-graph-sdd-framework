---
atom_family: TKT
atom_id: AN-T-2984
container:
  atom: AN-T-2944
priority: 2
context:
  template: question
state:
  status: backlog
  version: 1
  updated_at: '2026-11-22T10:27:51.914982+00:00'
---
## Summary

Trace Contracts provided by child Components

## Situation

Engine Studio (C14), Agentic (C22), Workbench (C43), and Model (C51)
compose capabilities supplied by child Components. Their own directories
have no direct executable Module. Workbench checks Component Contracts
against exact pins in the first Package below the owning Component.
It stops at a child Component boundary.

The Workbench app directory has a Spec Binding for existing Specs.
Its child Packages contain Backend and frontend code. The current graph
indexes the child code Packages and omits the app directory as a Package.

## Decision needed

Where should an exact Component Contract pin live when child Components
jointly provide the guarantee? Specify the Realization endpoint that
Workbench should report for the parent's Contract.

## Acceptance

Exercise one parent guarantee through its declared interface. Resolve the
exact parent Contract revision to the actual realization and show the
binding and relevant child evidence in Workbench.

## References

AN-T-2944, AN-T-2947, AN-T-2948, AN-S-3014, and AN-S-3179.
