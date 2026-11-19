---
identity:
  atom_id: CA-P-3060
  ref_id: CA-P-3060
context:
  role: plan
  form: Plan
  label: Task
  tier: 3
  container:
    atom: CA-P-3022
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom
state:
  version: 1
  status: active
  updated_at: '2026-11-13T17:14:01.288598+00:00'
destination:
  file:
    name: CA-P-3060-TASK--remove-cfel-specifications-and-declaration-atoms.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/03_plan/CA-P-3022-TASK--migrate-cfel-claims-to-readable-python
---
## Summary

Remove CFEL specifications and Declaration Atoms

## Work

1. Move the surviving Subject notation from CA-R-2471, CA-R-1321, and CA-R-1931 to Subject authority. Preserve the current Topic spelling and resolution rules.
2. Give surviving Relation and Format Declarations, including CA-R-2247 and CA-R-2248, Model addresses outside the CFEL branch. Remap their Current and Draft Topic references to those addresses and verify resolution.
3. After the surviving Claims and build readers have moved to Python, activate the Python-only revision of CA-R-2721. Remove CFEL-only RMEDO and obsolete Declaration carriers from the Current and Draft source sets, including CA-R-2487, CA-R-2563, and language-only Operator, Construct, and Function Declarations.
4. Verify no live Declaration, Topic, or applicable Model rule depends on the retired CFEL branch.
5. Retire the legacy dependency Relation Declarations CA-R-1026, CA-R-1200 and CA-R-2422 and the associated ordering Atoms CA-M-239 and CA-E-404. Drop the remaining legacy Relation links. Use `topics.dependencies` for Subject dependencies. CA-R-2762 owns IS_BLOCKED_BY and its inverse alias BLOCKS.

## Progress

The source audit found 241 Current Atoms with a CFEL Topic in the checked Scope Unit sources. The legacy CFEL namespace also owns live Relations and Formats. The CA-R-2471 revision remains pending because Lifecycle reports a live Run conflict.

Earlier migration moved 148 links to Topic Dependencies. The remaining 723 legacy links were removed from 385 Current, Backlog and Draft carriers. The five legacy Atoms were archived. Nine Current or Draft Topic records now reference the declared Dependencies Property. Remaining mentions of the former Relation in Claims are part of the CFEL cleanup.

CA-R-1321@37 owns the shared Subject grammar. Fifteen examples passed with the existing parser. The generator selects the Python Model separately from the legacy Claim-language catalog. The latter remains available to transitional consumers, including Delivery Claims still using the Delivery operator and existing Topic references to AllowedValue. Remove its Atoms after those consumers and references migrate.

CA-R-3008@9 and CA-R-3006@15 assign Role/Form validity to the Model. Removed the local lists in place from thirteen Current Scope Delegations and dropped redundant Formal Claims from six Scope Delegation Drafts. The scope reader resolved the same 49 Scope Units and now exports zero local Role/Form pairs. Existing Main Subject addresses and subject boundaries were preserved.

Workbench query 33c77776a74a404e8a35a82a157f7aa4 found four Current CFEL Formal Claims in the checked Scope Unit sources: CA-R-2243, CA-R-2487, CA-R-2604 and CA-R-2768. The language catalog and surviving namespaced references still require the reader cutover under CA-P-3061 before retirement.

Remapped Relation and Format Topic addresses in 168 Current and 46 Draft carriers. Only Topic header values changed. The rebuilt Workbench schema and Relation registry matched all prior functional outputs. Generated Model bytes matched and the contract graph resolved all 36 Relations without inheritance diagnostics. Lifecycle release assets compiled from the remapped sources. Workbench query `4c0f03e2bde4472da332b2e30f22b075` confirmed the direct Relation and Format roots.

Cardinality now has one Declaration at `ANECHOIC_MODEL <+ Cardinality`.
CA-R-2243@14 is Archived. Fallback, tuple uniqueness, functional dependencies,
Property immutability, and Relation defaults retain their rules outside CFEL.
The authoritative-source scan now finds one Current CFEL Formal Claim
(CA-R-2487) and zero Draft CFEL Formal Claims. Nine superseded Drafts moved
to withdrawn history with their bytes preserved. Subagent and Main Agent
now use Python classes that inherit AI Agent.

CA-R-1321 and CA-R-2483 distinguish MODEL declarations from actual objects
in STRUCTURE. Use `//` for narrowing and `/` for containment. The Scope Unit
and Lifecycle readers resolve the full containment chain. A disposable
rehearsal converted all 76 selected Scope Unit source Topics and reproduced
the same 49 units, authority paths and delivery paths. Live Topic headers
still require the compatible runtime.

The checked Workbench schema and Relation registry had the same functional
output with CA-R-2487 excluded. Automatic review held its retirement
while the Graph fence path and dependent fixtures remain in use.
