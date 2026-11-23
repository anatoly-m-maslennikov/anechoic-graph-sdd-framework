# Find mixed levels of abstraction in a function

Use the [shared evidence prompt](review_evidence.prompt.md).

Identify what the function promises to do. Look for code that coordinates that work
and also implements a lower-level mechanism inline.

Cite the coordinating statement and the implementation block. Explain which change
to the lower-level mechanism would force the coordinating function to change.
Return this as a review candidate.
