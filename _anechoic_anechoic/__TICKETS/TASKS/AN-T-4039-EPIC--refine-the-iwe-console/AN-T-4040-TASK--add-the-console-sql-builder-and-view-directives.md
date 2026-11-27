---
atom_family: TKT
atom_id: AN-T-4040
container:
  atom: AN-T-4039
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T22:18:31Z"
---
## Summary

Add the Console SQL builder and View directives

## Work

Each regular Console tab displays a SQL query result. Accept a trailing
`VIEW TABLE`, `VIEW DOC` or `VIEW DOCUMENT`, or `VIEW GRAPH` directive.
Table is the default. Graph is vertical by default and accepts a
horizontal layout. Submit the SQL query through the existing API.

Place the SQL builder above each result. Component, Tier, Template,
and Limit controls edit the SQL shown in the editor. Limit changes
the `LIMIT` clause. Keep the query and its View choice together when
the Console saves or restores a tab.

## Acceptance

Verify that existing SQL opens as a Table and that the builder changes
the displayed SQL and reruns the edited query. For Document and Graph,
show an error if multiple columns could supply Atom IDs. Ask the user
to select a single reference column.
