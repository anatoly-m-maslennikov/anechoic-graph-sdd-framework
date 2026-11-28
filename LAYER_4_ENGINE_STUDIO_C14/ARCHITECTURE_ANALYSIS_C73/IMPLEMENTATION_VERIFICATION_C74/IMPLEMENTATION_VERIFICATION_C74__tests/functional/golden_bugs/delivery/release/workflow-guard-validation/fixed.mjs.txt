import { createMachine } from 'xstate';
import { toMermaidState } from '@statelyai/graph/mermaid';

const fail = message => { throw new Error(message); };
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const keys = (value, allowed, where) => {
  if (!object(value)) fail(`${where} must be an object`);
  for (const key of Object.keys(value)) if (!allowed.includes(key)) fail(`${where}: unsupported field ${key}`);
};
const safe = (value, where) => {
  if (typeof value !== 'string' || !/^[A-Za-z_][A-Za-z0-9_-]{0,63}$/.test(value) || ['__proto__', 'constructor', 'prototype'].includes(value)) fail(`${where}: invalid identifier`);
};

const jsonEqual = (a, b) => {
  if (a === b) return true;
  if (!a || !b || typeof a !== 'object' || typeof b !== 'object' || Array.isArray(a) !== Array.isArray(b)) return false;
  const keys = Object.keys(a);
  return keys.length === Object.keys(b).length && keys.every(key => Object.hasOwn(b, key) && jsonEqual(a[key], b[key]));
};
const compatible = (a, b) => Object.keys(a).every(key => !Object.hasOwn(b, key) || jsonEqual(a[key], b[key]));
function guardsOverlap(a, b) {
  return ['kind', 'target', 'outcome'].every(key =>
    !Object.hasOwn(a, key) || !Object.hasOwn(b, key) || a[key] === b[key]
  ) && compatible(a.detail ?? {}, b.detail ?? {});
}

function validateTransition(transition, states) {
  keys(transition, ['target', 'guard'], 'transition');
  safe(transition.target, 'target');
  if (!Object.hasOwn(states, transition.target)) fail(`target ${transition.target} does not exist`);
  keys(transition.guard, ['type', 'params'], 'guard');
  if (transition.guard.type !== 'matchesTrace') fail('guard must be matchesTrace');
  const p = transition.guard.params;
  keys(p, ['kind', 'target', 'outcome', 'detail'], 'guard.params');
  if (!['trigger', 'effect', 'output'].includes(p.kind)) fail('invalid trace kind');
  for (const field of ['target', 'outcome']) if (Object.hasOwn(p, field) && p[field] !== null && (typeof p[field] !== 'string' || p[field].length > 256)) fail(`${field} must be a string or null`);
  if (Object.hasOwn(p, 'detail') && !object(p.detail)) fail('detail must be an object');
}

function validate(config) {
  keys(config, ['id', 'initial', 'states'], 'config');
  safe(config.id, 'id'); safe(config.initial, 'initial');
  if (!object(config.states)) fail('states must be an object');
  const names = Object.keys(config.states);
  if (!names.length || names.length > 100) fail('states must contain 1 to 100 states');
  if (!Object.hasOwn(config.states, config.initial)) fail('initial state does not exist');
  let count = 0, finals = 0;
  for (const name of names) {
    safe(name, 'state');
    const state = config.states[name];
    keys(state, ['type', 'on'], `state ${name}`);
    if (state.type === 'final') {
      if (Object.hasOwn(state, 'on')) fail(`final state ${name} cannot have transitions`);
      finals++; continue;
    }
    if (Object.hasOwn(state, 'type')) fail(`state ${name}: unsupported type`);
    keys(state.on, Object.keys(state.on ?? {}), `state ${name}.on`);
    for (const [event, value] of Object.entries(state.on)) {
      safe(event, 'event');
      const transitions = Array.isArray(value) ? value : [value];
      if (!transitions.length) fail(`event ${event}: empty transitions`);
      for (const transition of transitions) {
        if (++count > 1000) fail('too many transitions');
        validateTransition(transition, config.states);
      }
      for (const [index, branch] of transitions.entries()) {
        for (const other of transitions.slice(index + 1)) {
          if (guardsOverlap(branch.guard.params, other.guard.params)) {
            fail(`state ${name}, event ${event}: overlapping guards for targets ${branch.target} and ${other.target}`);
          }
        }
      }
    }
  }
  if (!finals) fail('at least one final state is required');
  return names;
}

export function compile(config) {
  const names = validate(config);
  const machine = createMachine(config);
  const states = names.map(name => {
    const node = machine.states[name];
    return { name, final: node.type === 'final', transitions: [...node.transitions].flatMap(([event, branches]) => branches.map(branch => ({ event, target: branch.target[0].key, expect: branch.guard.params }))) };
  });
  const byName = new Map(states.map(state => [state.name, state]));
  const reached = new Set([config.initial]), queue = [config.initial];
  for (const name of queue) for (const transition of byName.get(name).transitions) if (!reached.has(transition.target)) { reached.add(transition.target); queue.push(transition.target); }
  if (reached.size !== names.length) fail(`unreachable states: ${names.filter(name => !reached.has(name)).join(', ')}`);
  requirePathToFinal(states);
  return render(config, states);
}

function requirePathToFinal(states) {
  const canFinish = new Set(states.filter(state => state.final).map(state => state.name));
  let changed = true;
  while (changed) {
    changed = false;
    for (const state of states) if (!canFinish.has(state.name) && state.transitions.some(t => canFinish.has(t.target))) {
      canFinish.add(state.name); changed = true;
    }
  }
  const dead = states.filter(state => !canFinish.has(state.name)).map(state => state.name);
  if (dead.length) fail(`states with no path to a final state: ${dead.join(', ')}`);
}

function render(config, states) {
  const nodes = states.map(({name}) => ({type:'node', id:name, parentId:null, initialNodeId:null, label:name, data:{}}));
  nodes.push({type:'node', id:'@start', parentId:null, initialNodeId:null, label:'[*]', data:{isStart:true}});
  nodes.push({type:'node', id:'@end', parentId:null, initialNodeId:null, label:'[*]', data:{isEnd:true}});
  const edges = [];
  const edge = (sourceId, targetId, label = '') => edges.push({type:'edge', id:`edge${edges.length}`, sourceId, targetId, label, data:{}});
  edge('@start', config.initial);
  for (const state of states) {
    if (state.final) edge(state.name, '@end');
    for (const t of state.transitions) {
      const p = t.expect;
      const label = [t.event, p.kind, p.target, p.outcome, p.detail && JSON.stringify(p.detail)]
        .filter(value => value != null && value !== '').join(' / ').replace(/[\r\n]+/g, ' ');
      edge(state.name, t.target, label);
    }
  }
  return {model:{initial:config.initial, states}, mermaid:toMermaidState({id:'', mode:'directed', initialNodeId:config.initial, nodes, edges, data:{diagramType:'stateDiagram'}})};
}
