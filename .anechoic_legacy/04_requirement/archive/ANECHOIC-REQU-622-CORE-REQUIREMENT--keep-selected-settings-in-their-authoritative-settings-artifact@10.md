---
version: 10
updated_at: "2026-09-09 23:04:14 +0400"
llm_session_ids:
  - "codex:019f591f-04f6-70f2-8de7-828b7cccc69d"
relations:
  depends_on:
    - ANECHOIC-META-REQU-675
    - ANECHOIC-META-REQU-619
    - CA-R-1402
  child_of:
    - "CA-M-002"
    - "CA-R-1421"
cce_version: "cce_1"
cce_form: "obligation"
subjects:
  governs:
    continuant:
      - "Project/settings authority"
  depends_on:
    continuant:
      - "Project"
      - "Framework Instance Settings"
      - "Project Settings"
      - "Artifact"
      - "Atom"
      - "ANECHOIC Framework Instance"
atom_id: ANECHOIC-REQU-622
---
# Keep selected settings in their authoritative Settings Artifact

the ANECHOIC Framework Instance serving anechoic **must** consume Project Settings **and** Framework Instance Settings according to Core Meta-Model authority under ANECHOIC-META-REQU-675, **without** redefining their purpose, locations, **or** selected values in Project Atoms.
