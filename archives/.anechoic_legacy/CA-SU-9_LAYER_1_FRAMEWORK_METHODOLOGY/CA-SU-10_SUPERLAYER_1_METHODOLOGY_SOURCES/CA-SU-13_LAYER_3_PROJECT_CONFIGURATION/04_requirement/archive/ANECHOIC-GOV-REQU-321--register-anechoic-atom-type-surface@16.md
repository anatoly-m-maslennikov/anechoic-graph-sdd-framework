---
cce_version: cce_1
cce_form: requirement
subjects:
  governs:
    continuant:
      - Type
  depends_on:
    continuant:
      - Atom
      - Content Role
version: 16
updated_at: 2026-08-29 04:33:13 +0400
llm_session_ids:
  - codex:019f591f-04f6-70f2-8de7-828b7cccc69d
relations:
  replacement_of:
    - ANECHOIC-GOV-REQU-470--register-current-atom-type-surface
  child_of:
    - ANECHOIC-META-REQU-112--role-specific-atom-occupancy
    - ANECHOIC-META-REQU-740--separate-content-role-from-artifact-type
    - CA-R-1054
  resolution_of:
    - ANECHOIC-GOV-CONC-037--semantic-route-catalog-remains-incomplete
    - ANECHOIC-GOV-CONC-051--which-types-complete-the-semantic-route-catalog
---
# Register the ANECHOIC Type Surface for Atoms

GOVERNANCE **must** register **every** typed Atom with **`=1`** Content Role value **and** **`<=1`** Type value. Content Role states the Atom's primary semantic contribution, Type states the governed kind within that role, **and** Atom routing admits no additional subtype coordinate.
