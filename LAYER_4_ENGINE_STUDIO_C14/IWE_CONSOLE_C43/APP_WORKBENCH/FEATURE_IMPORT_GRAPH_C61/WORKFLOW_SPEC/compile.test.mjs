import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
const run = config => spawnSync(process.execPath, ['compile.mjs'], {input: JSON.stringify(config), encoding:'utf8'});
const base = () => ({id:'flow', initial:'start', states:{start:{on:{NEXT:[{target:'done',guard:{type:'matchesTrace',params:{kind:'output',outcome:'success'}}},{target:'start',guard:{type:'matchesTrace',params:{kind:'effect',outcome:'retry'}}}]}},done:{type:'final'}}});
test('resolves and renders every guarded branch', () => {
  const result = run(base()); assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  assert.deepEqual(output.model.states[0].transitions.map(t => t.target), ['done','start']);
  assert.match(output.mermaid, /NEXT \/ output \/ success/);
  assert.match(output.mermaid, /NEXT \/ effect \/ retry/);
  assert.match(output.mermaid, /done --> \[\*\]/);
});
test('rejects unsupported constructs and invalid graph', () => {
  for (const mutate of [
    c => c.states.start.entry = 'action',
    c => c.states.start.on.NEXT[0].target = 'missing',
    c => c.states.extra = {type:'final'},
    c => c.states.start.on.NEXT[0].guard.type = 'arbitrary',
    c => c.states.done = {on:{}},
  ]) { const c = base(); mutate(c); const result = run(c); assert.notEqual(result.status, 0); assert.match(result.stderr, /workflow compilation failed/); }
});
test('rejects overlapping guards with state, event and target context', () => {
  for (const [a, b] of [
    [{kind:'output'}, {kind:'output', outcome:'success'}],
    [{kind:'output', target:null}, {kind:'output'}],
    [{kind:'output', detail:{a:1}}, {kind:'output', detail:{a:1, b:2}}],
    [{kind:'output', detail:{a:{x:1, y:2}}}, {kind:'output', detail:{a:{y:2, x:1}}}],
  ]) {
    const c = base(); c.states.start.on.NEXT = [a, b].map((params, i) => ({target:i ? 'start' : 'done', guard:{type:'matchesTrace', params}}));
    const result = run(c); assert.notEqual(result.status, 0); assert.match(result.stderr, /state start, event NEXT: overlapping guards for targets done and start/);
  }
});
test('allows disjoint guards and a loop with an exit', () => {
  for (const [a, b] of [
    [{kind:'output', target:null}, {kind:'output', target:'x'}],
    [{kind:'output', detail:{a:1}}, {kind:'output', detail:{a:2}}],
    [{kind:'output', detail:{a:{x:1}}}, {kind:'output', detail:{a:{x:1, y:2}}}],
  ]) {
    const c = base(); c.states.start.on.NEXT = [a, b].map((params, i) => ({target:i ? 'start' : 'done', guard:{type:'matchesTrace', params}}));
    const result = run(c); assert.equal(result.status, 0, result.stderr);
  }
});
test('rejects reachable dead ends and closed cycles', () => {
  for (const on of [{}, {LOOP:{target:'stuck', guard:{type:'matchesTrace', params:{kind:'effect'}}}}]) {
    const c = base(); c.states.start.on.NEXT[1].target = 'stuck'; c.states.stuck = {on};
    const result = run(c); assert.notEqual(result.status, 0); assert.match(result.stderr, /no path to a final state: stuck/);
  }
});
