# Architecture review evidence

Use this prompt with one search prompt. Review the selected Code Units and their direct
callers and callees. Use the Realization Graph, active Contracts, and Spec Bindings to
establish ownership.

For each candidate, give the file and line, Code Unit, source trace, Spec reference and
version, and the exact fact Lean would need to check. Return only candidates with a
concrete source location.

Use `review` for source-backed candidates and `unresolved` when evidence is missing.
Use `confirmed` only when a Lean check has verified a witness from the source.
