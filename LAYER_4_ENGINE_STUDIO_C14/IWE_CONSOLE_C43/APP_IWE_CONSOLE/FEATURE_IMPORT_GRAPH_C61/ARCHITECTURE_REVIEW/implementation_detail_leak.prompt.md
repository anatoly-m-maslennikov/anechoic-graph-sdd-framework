# Find implementation details that cross a boundary

Use the [shared evidence prompt](review_evidence.prompt.md).

Trace exported parameters, return values, and errors to their origin. Look for
implementation types, data formats, error codes, identifiers, or lifecycle requirements
that callers must understand.

Identify the first caller that relies on the detail. Cite the boundary crossing and
the caller's use. Check whether the active Contract exposes that detail explicitly.
