---
identity:
  atom_id: AN-T-1794
context:
  container:
    component: C14
  tier: 4
  template: question
state:
  status: resolved
  version: 2
  updated_at: 2026-11-10 22:09:03 +0400
---

## Summary

Which identity should the Core Operator Declaration Draft use?

## Concern

CA-R-2953 is already a Current Workbench Requirement for read-only result sorting, filtering and grouping. A separate Core Draft uses the same Atom ID for the Operator Declaration Form. They define different contributions; the Core Draft is not a new Version of the Workbench Requirement.

## Details

Preserve the existing Workbench identity. The proposed treatment is to give the unrelated Core Draft an unused canonical ID in its owning source lane and repair only its actual references. Do not let a global Draft-preference lookup shadow the Engine Requirement.

Current: `.anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/04_requirement/CA-R-2953-WORKBENCH-SOLUTION--query-results-support-read-only-sorting-filtering-and-grouping.md`.

Unrelated Draft: `.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/draft/CA-R-2953@1-draft-CORE_META_MODEL-DECLARATION--declare-operator-declaration-as-a-requirement-form.md`.

Blast radius: this pair's identity and its actual consumers. The Core Draft is outside this Engine refinement pass, and neither source is renamed, promoted or retired by this Question. The scoped candidate inventory keeps the existing Workbench contribution.

## Resolution

The Operator approved the narrow Core Draft identity repair. The unrelated Operator Declaration Draft now uses CA-R-3023@1-draft; its Claim and other content are unchanged. Its Header, filename and carrier metadata identify the new Draft consistently. Current Workbench CA-R-2953 is unchanged.

No other Current or Draft Methodology references to the old Draft identity were found. Historical evidence above retains the original collision. This correction does not promote the Core Draft or adopt its Form.
