---
atom_family: TKT
atom_id: AN-T-2033
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T01:57:22.674635+00:00'
---
## Summary

How should image builds query lifecycle placement declarations

## Question

Which query source should a clean image build use to select lifecycle placement Declarations by Role and main Subject before the Workbench image exists?

## Details

The compiler selects the staged Current Delivery Formal Claims by Role and Topic without pinned selection IDs. It discovers the source files directly during the build. The runtime reads the compiled asset. A fresh offline image build has no running project query_run to select those declarations from.

Tracked in CA-P-3017.