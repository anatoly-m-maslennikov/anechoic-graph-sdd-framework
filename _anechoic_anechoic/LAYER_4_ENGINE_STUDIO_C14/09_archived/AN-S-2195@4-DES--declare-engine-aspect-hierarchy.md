---
atom_family: SPEC
atom_id: AN-S-2195
container:
  component: C14
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-27T14:43:25.838139+00:00"
---

## Summary

Declare Engine Aspect hierarchy

## Claim scope

Engineering, UX, Documentation and Product topics used by the ANECHOIC Engine.

## Claim

### Prose Claim

ANECHOIC's Project Structure contains the following project-local Aspect hierarchy. Aspects is its grouping container; the other named nodes are concrete instances of Aspect. Each indentation is direct containment, not narrowing or automatic policy inheritance. An address begins with `PROJECT STRUCTURE//ANECHOIC  <+  Aspects` and continues with ` <+ ` and the names along that branch.

Frontend Engineering covers frontend construction. Libraries and Frameworks covers library, framework and build-tool choices; Component Authoring covers Svelte components and TypeScript; Code Style covers source organization, formatting and responsibility boundaries. Visual Design, query authoring and interface contracts retain their distinct topics.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Project Structure",
    structure_paths=(
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Documentation <+ Traceability',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Change Readiness',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Packaging',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Reproducibility',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ API',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring <+ Python Code',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Controlled English',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Prompt Authoring',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Code Style',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Component Authoring',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Libraries and Frameworks',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Configuration',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Data Validation',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Output Publication',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Serialization',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Code Hot Reload',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Effect Authorization',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Outcome Reporting',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Recovery',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Resource Limits',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability <+ Logging',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Directory Layout',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Traceability <+ Provenance',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Coverage',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing <+ Canary Testing',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis <+ Python Code',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Data <+ Golden Corpora',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Design',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Product',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Discovery and Navigation',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Entry',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Guidance',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Accessibility',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Decision',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Result and Status Presentation',
    ),
    aspect_memberships=(
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Documentation',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Documentation <+ Traceability',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Change Readiness',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Packaging',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Reproducibility',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ API',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring <+ Python Code',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Controlled English',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Prompt Authoring',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Code Style',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Component Authoring',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Libraries and Frameworks',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Configuration',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Data Validation',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Output Publication',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Serialization',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Code Hot Reload',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Effect Authorization',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Outcome Reporting',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Recovery',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Resource Limits',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability <+ Logging',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Directory Layout',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Traceability',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Traceability <+ Provenance',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Coverage',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing <+ Canary Testing',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis <+ Python Code',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Data',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Data <+ Golden Corpora',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Design',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Product',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Discovery and Navigation',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Entry',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Guidance',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Accessibility',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Decision',
        'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Result and Status Presentation',
    ),
)
```
