# Find similar component flows

Use `flow_overlap_candidates` for actions with multiple triggers and
`flow_similar_actions` for distinct actions with the same observed output and effect shape.
Use `component_flows` and `flow_events` to find shared suffixes. Use the Component's Contract
and I/O and state declarations to check the behavior. State writes are effects, including
repeated writes.

For each candidate, cite source locations or runtime observations for the events and control
paths. Align inputs and initial state explicitly. List any gaps, uncertain branches, ordering
assumptions, and proof obligations. A finite comparison covers the supplied traces.

Substitute the selected run ID to extract observable events in sequence order.

```sql
SELECT coalesce(to_json(list(struct_pack(kind := kind, name := name,
  target := target, outcome := outcome, detail := detail) ORDER BY sequence)), '[]'::JSON)
FROM flow_events
WHERE run_id = '<run_id>' AND kind IN ('output', 'effect');
```

Wrap both arrays in a JSON object and pass it on stdin to `lean --run FlowComparison.lean`.

```json
{"inputsAligned":true,"left":{"complete":true,"events":[{"kind":"effect","name":"value","target":"store","outcome":null,"detail":{"value":1}}]},"right":{"complete":true,"events":[{"kind":"effect","name":"value","target":"store","outcome":null,"detail":{"value":1}}]}}
```

All five event fields are required. `kind` and `name` are strings. `target` and `outcome`
are strings or null. `detail` is a JSON object. Normalize matching meanings consistently.
Keep each occurrence in causal or sequence order. Compare observable values.

`inputsAligned` asserts alignment of inputs and initial state. Use `complete: false` for traces
with `omitted_events`, `unattributed`, or other gaps. The output has `status` and `firstDifference`.
The difference gives the zero-based `index` and the event from each trace.
A missing event is null. `matched` applies to the supplied traces.
