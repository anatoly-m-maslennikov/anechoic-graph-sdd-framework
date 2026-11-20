---
identity:
  atom_id: AN-T-2741
context:
  container:
    atom: AN-T-2483
  tier: 3
  template: task
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:47:16.618914+00:00'
---
## Summary

Build and verify GENERATED_MODEL

## Work

1. Use the Current RMEDO adopted in CA-P-3059.
2. Implement FORMAL_MODEL_GENERATOR and build the GENERATED_MODEL package. Apply CA-R-3091, CA-R-3136, CA-M-1017 and CA-M-1020.
3. Implement the MODEL_VALIDATION library and its separate checks module. Apply CA-R-3147 and CA-R-3137. Keep named check source in the governing Declarations.
4. Verify the generated package and validation API with CA-E-828. Tool and App adoption is tracked by CA-P-3022 and CA-P-3061.

## Specification

CA-R-3091, CA-R-3136, CA-R-3147, CA-R-3137, CA-R-3131, CA-M-1017, CA-M-1020, CA-E-828.

## Progress

Fifteen Role-qualified Form Claims now use distinct Python class names.

CA-P-3059 published the three Scope Units. FORMAL_MODEL_GENERATOR now owns source selection and class assembly. It loads the assembled dataclasses during the build to check Python inheritance. MODEL_VALIDATION now owns field validation and the reviewed named check binder.

Node, Atom, Scope Unit and Package have native Python Drafts in CA-R-2462@5-draft, CA-R-2508@7-draft, CA-R-2523@5-draft and CA-R-2525@4-draft. Their generated classes load with the declared inheritance. The Atom Draft formalizes Header and Content and project-wide ID/Version uniqueness.

The shared instance validator checks nested Properties, inherited outgoing Relation constraints, and named checks. The Package Draft requires one container, and the Project Package's Current Declaration overrides that bound to zero. Both cases passed using the actual Declarations.

Selected Declarations now supply Relation and uniqueness rules to the shared validator. The validator checks the proposed Atom ID and Version against a supplied population across all Status Groups. It also supports Active-only uniqueness for Properties with one value per key. A focused test exercises source selection, class generation, rule binding, and duplicate rejection together.

The generator registers Relations and inverse aliases before checking Entity constraints. It resolves inherited Properties through Python classes. The live Relation set contains 36 native Declarations and 14 inverse aliases. The live Entity build generated 94 classes from 244 Current Declarations, and MODEL_VALIDATION bound all 244 Declarations.

Lifecycle uses MODEL_VALIDATION for the Work Report target Relation from CA-R-3053 and the generated Plan Form from CA-R-3155. A disposable Project test saved a valid Direct Update and rejected an extra target and the wrong target Form before saving. Release asset compilation included the native constraint. Full Atom instance validation still requires binding the Header and Content Property Declarations to generated fields.

The generator builds Atom Header Identity and State dataclasses from their Current Property Declarations. Lifecycle checks these groups before saving and accepts the existing Carrier aliases. A Direct Update test rejects an undeclared Identity Property before writing. The remaining Header groups and Content still need generated fields.

The generator now also builds Destination and File from CA-R-2715 through CA-R-2718. File Name and Path inherit their string format from the File Declaration. Lifecycle rejected an integer destination Path in a Direct Update test and preserved the original Carrier bytes.

Lifecycle checks added or changed Header Relation entries against CA-R-2709 and the Current direct Relation registry. A relation entry takes a nonempty list of Project base Atom IDs. An empty mapping clears the optional group. Unchanged legacy entries are preserved during migration. Context, Content, and full instance Relation validation remain open.

The generated Model now checks Role, Form, optional Label, Plan sequence and confidence values, and Concern priority on authored Lifecycle writes. A Direct Update rejected confidence above 100 before saving. Container, Topics, Tier, and complete Context group validation still use the existing checks or need further binding.

Lifecycle now checks the declared Container, Topics and Tier fields, the supported native Content contracts, and project-wide ID/Version uniqueness. Authored Relation entries are checked against Current Relation Declarations for the source and target kinds. The shared validator applies inherited Relation constraints and checks endpoint pairs.

Verified the four CA-E-828 cases against the generator and Lifecycle entry points. The generator reports each malformed Claim set to stderr and preserves the last generated package. The Lifecycle batch applies its first valid write, reports the invalid second target to stderr, and leaves the third target untouched. The generated package matches the Current Declarations, and the local release asset compiler includes the new checks.

Relation Declarations now establish direct endpoint eligibility. Entity Declarations supply additional conditions. CA-R-2766 admits SPECIALIZES between Atom instances. CA-R-2508 owns the Claim specialization rules.

Lifecycle validates the Container and Main Subject links alongside authored Header Relation entries. Container resolves to a Current Atom or declared Scope Unit, including the root and bootstrap Scope Units. Main Subject resolves against the compiled Model Declarations and Project Scope Units. A Scope Unit Declaration must name a Scope Unit instance. Unknown newly authored Model Subjects and Scope Units fail before writing. Historical Model Subjects and Project Structure Topics outside those indexed forms retain their existing behavior.

The generated Atom now has typed Header and Content fields. Lifecycle validates the composed fields for a new Atom, for an edited Topic, and for grouped Carriers on other edits, promotion, status and archive writes. It applies the declared role- and form-specific Markdown constraints and maps only declared headings to Content Properties. Historical flat Headers still use the compatibility path. An empty legacy Relations map is read as an omitted optional group.

Current Aspects and Named Selections resolve by exact project-qualified address through the internal query API and selected defining Claims. A disposable Workbench Project resolved Visual Design from CA-R-2775 and Extension Sources from CA-R-2277. New unbound Subjects are rejected, including the historical Structure TOML Projection whose live instance was not found.

CA-E-828 passed for the generator and shared validation library. Tool and App adoption remains in CA-P-3022 and CA-P-3061. That work includes the historical flat Header compatibility path, remaining Workflow and Action Subject bindings, and container image verification.
