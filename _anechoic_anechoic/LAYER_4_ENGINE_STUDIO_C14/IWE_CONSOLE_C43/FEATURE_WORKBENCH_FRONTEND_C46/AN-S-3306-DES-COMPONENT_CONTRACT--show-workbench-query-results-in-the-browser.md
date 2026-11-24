---
atom_family: SPEC
atom_id: AN-S-3306
container:
  component: C46
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3060
state:
  status: active
  version: 2
  updated_at: '2026-11-22T22:21:57.767357+00:00'
---
## Summary

Show Workbench query results in the browser

## Guarantee

Open the Workspace of the selected Project before enabling SQL input.
Submit the current View's SQL to the Project HTTP API. Run displays the
returned columns and rows and preserves the SQL in the editor.

Check displays the verdict for the current SQL and preserves the previous
Run result. Changing SQL clears that Check verdict. Display an error
when the Project API refuses or fails a request.

## References

AN-S-2328, AN-S-2549, AN-S-3060, and AN-T-2947.
