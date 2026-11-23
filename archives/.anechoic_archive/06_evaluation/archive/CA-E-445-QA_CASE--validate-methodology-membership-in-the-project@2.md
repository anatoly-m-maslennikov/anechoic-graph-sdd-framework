---
atom_id: CA-E-445
cce_version: cce_1
cce_form: evaluation
subjects:
  governs: "Project/methodology ownership validation"
  depends_on:
    - "Project"
    - "Scope Unit"
    - "Structural Level"
    - "Methodology Source"
    - "Atom"
    - "Atom/Local Tier: Principle"
    - "Atom/Content Role: Requirement/Type: Goal"
version: 2
updated_at: "2026-09-16 23:48:40 +0000"
relations:
  evaluation_for:
    - ANECHOIC-REQU-706
    - ANECHOIC-REQU-031
    - ANECHOIC-META-REQU-679
    - CA-R-718
    - CA-D-325
llm_session_ids:
  - codex:01a02650-eff7-7453-8c37-0699b36773c6
---
# Validate Methodology membership in the Project

## Claim checked

the Methodology Scope Units belong to the anechoic Project Scope Unit tree **and** remain governed by its active Project Principles.

## Test case

resolve the current Project Scope Unit tree from authoritative ownership declarations **and** locate FRAMEWORK_METHODOLOGY, METHODOLOGY_SOURCES, **and** its source Scope Units. verify their ancestry to anechoic **and** their authority Directory Carriers. include their active Atoms in Principle-first alignment checks. **then** place a Methodology Scope Unit outside that tree, assign a negative Structural Level to a current anechoic Scope Unit, register a Bootstrap Scope Unit as part of the current anechoic structure, exempt Methodology from a Project Principle, **or** represent an Atom's different Claim Scope as an additional Scope Unit edge.

## Acceptance criteria

**every** current Methodology Scope Unit has a parent chain to anechoic **and** its Structural Level follows that chain. its source Carrier placement does **not** exempt it from Project authority. the ordinary Principle-first checks include its active Atoms. **all** invalid fixtures fail. the Core Meta-Model's optional support for Bootstrap Scope Units does **not** activate them for anechoic. the external Project Goal's Global Tier **`-1`** remains valid **and** is **not** a negative Scope Unit Structural Level. archived Bootstrap records remain historical evidence **without** becoming current Scope Units.

## Failure disposition

record a Concern identifying the incorrect owner, Structural Level, Carrier binding, Principle exemption, **or** invented Scope Unit edge.
