import type * as Acorn from '../../../../../../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/acorn';
const fs = require('fs');
const acorn: typeof Acorn = require('../../../../../../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/acorn/dist/acorn.js');
const text = fs.readFileSync(process.argv[2], 'utf8');
const tree = acorn.parse(text, {ecmaVersion: 'latest', sourceType: 'module'});
function walk(node: unknown, predicate: (node: Acorn.AnyNode) => boolean, found: Acorn.AnyNode[] = []): Acorn.AnyNode[] {
  if (!node || typeof node !== 'object') return found;
  if (predicate(node as Acorn.AnyNode)) found.push(node as Acorn.AnyNode);
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) for (const child of value) walk(child, predicate, found);
    else if (value && typeof value === 'object') walk(value, predicate, found);
  }
  return found;
}
function code(node: Acorn.Node) { return text.slice(node.start, node.end).replace(/\s+/g, ''); }
function func(name: string): Acorn.FunctionDeclaration {
  const nodes = walk(tree, n => n.type === 'FunctionDeclaration' && n.id!.name === name);
  if (nodes.length !== 1) throw Error('expected one function ' + name);
  return nodes[0] as Acorn.FunctionDeclaration;
}
function call(node: Acorn.Node, name: string) {
  return walk(node, n => n.type === 'CallExpression' && n.callee.type === 'Identifier' && n.callee.name === name);
}
function requireText(node: Acorn.Node, fragment: string) {
  if (!code(node).includes(fragment.replace(/\s+/g, ''))) throw Error('unsupported structure: ' + fragment);
}
function guardFact(validate: Acorn.FunctionDeclaration) {
  const loops = walk(validate, n => n.type === 'ForOfStatement' && code(n.right) === 'Object.entries(state.on)');
  if (loops.length !== 1) throw Error('expected event loop');
  const body = ((loops[0] as Acorn.ForOfStatement).body as Acorn.BlockStatement).body;
  if (![4, 5].includes(body.length) || body[3].type !== 'ForOfStatement') throw Error('unsupported event validation');
  const checks = ((body[3] as Acorn.ForOfStatement).body as Acorn.BlockStatement).body;
  if (checks.length !== 2 || checks[0].type !== 'IfStatement' ||
      code(checks[1]) !== 'validateTransition(transition,config.states);') throw Error('unsupported transition validation');
  if (body.length === 4) {
    if (call(validate, 'guardsOverlap').length) throw Error('unexpected overlap check');
    return false;
  }
  const branch = body[4];
  expectAst(branch, patterns.pair, 'overlap branch');
  requireText(branch, 'transitions.entries()');
  requireText(branch, 'transitions.slice(index + 1)');
  requireText(branch, 'if (guardsOverlap(branch.guard.params, other.guard.params))');
  requireText(branch, 'fail(`state ${name}, event ${event}: overlapping guards for targets ${branch.target} and ${other.target}`)');
  const overlap = func('guardsOverlap');
  expectAst(overlap, patterns.overlap, 'guardsOverlap');
  expectVariable('compatible', patterns.compatible);
  expectVariable('jsonEqual', patterns.equal);
  if (overlap.body.body.length !== 1 || overlap.body.body[0].type !== 'ReturnStatement') throw Error('unsupported overlap helper');
  requireText(overlap, "['kind', 'target', 'outcome'].every(key => !Object.hasOwn(a, key) || !Object.hasOwn(b, key) || a[key] === b[key])");
  requireText(overlap, 'compatible(a.detail ?? {}, b.detail ?? {})');
  const helpers = walk(tree, n => n.type === 'VariableDeclarator' && (n.id as Acorn.Identifier).name === 'compatible');
  if (helpers.length !== 1) throw Error('expected compatible helper');
  requireText(helpers[0], 'Object.keys(a).every(key => !Object.hasOwn(b, key) || jsonEqual(a[key], b[key]))');
  if (call(validate, 'guardsOverlap').length !== 1) throw Error('unexpected overlap calls');
  return true;
}
function finishFact(compile: Acorn.FunctionDeclaration) {
  const calls = call(compile, 'requirePathToFinal');
  if (calls.length > 1) throw Error('unexpected final-path calls');
  const body = compile.body.body;
  patterns.compile.forEach((pattern, i) => expectAst(body[i], pattern, 'compile graph ' + i));
  const prefix = 'VariableDeclaration,VariableDeclaration,VariableDeclaration,VariableDeclaration,VariableDeclaration,ForOfStatement,IfStatement,';
  const expected = prefix + (calls.length ? 'ExpressionStatement,' : '') + 'ReturnStatement';
  if (body.map(n => n.type).join(',') !== expected) throw Error('unsupported compiler shape');
  const render = body.findIndex(n => n.type === 'ReturnStatement' && code(n.argument!) === 'render(config,states)');
  if (render < 0 || render !== body.length - 1) throw Error('unsupported compile return');
  if (!calls.length) {
    if (body[render - 1].type !== 'IfStatement' || call(body[render - 1], 'fail').length !== 1) throw Error('unsupported reachability validation');
    requireText(body[render - 1], 'reached.size !== names.length');
    return false;
  }
  if (body[render - 1].type !== 'ExpressionStatement' || code(body[render - 1]) !== 'requirePathToFinal(states);') throw Error('unsupported final-path placement');
  const helper = func('requirePathToFinal');
  expectAst(helper, patterns.finish, 'requirePathToFinal');
  const shape = helper.body.body.map(n => n.type).join(',');
  if (shape !== 'VariableDeclaration,VariableDeclaration,WhileStatement,VariableDeclaration,IfStatement') throw Error('unsupported final-path helper');
  for (const fragment of ['states.filter(state => state.final).map(state => state.name)',
    'while (changed)', 'changed = false', '!canFinish.has(state.name)',
    'state.transitions.some(t => canFinish.has(t.target))', 'canFinish.add(state.name)',
    'changed = true', 'states.filter(state => !canFinish.has(state.name))',
    'if (dead.length) fail(`states with no path to a final state: ${dead.join(\', \')}`)']) requireText(helper, fragment);
  return true;
}
function semantic(node: unknown): unknown {
  if (Array.isArray(node)) return node.map(semantic);
  if (!node || typeof node !== 'object') return node;
  return Object.fromEntries(Object.entries(node)
    .filter(([key]) => !['start', 'end', 'raw'].includes(key))
    .map(([key, value]) => [key, semantic(value)]));
}
const patterns = {"pair":"for (const [index, branch] of transitions.entries()) {\n        for (const other of transitions.slice(index + 1)) {\n          if (guardsOverlap(branch.guard.params, other.guard.params)) {\n            fail(`state ${name}, event ${event}: overlapping guards for targets ${branch.target} and ${other.target}`);\n          }\n        }\n      }","overlap":"function guardsOverlap(a, b) {\n  return ['kind', 'target', 'outcome'].every(key =>\n    !Object.hasOwn(a, key) || !Object.hasOwn(b, key) || a[key] === b[key]\n  ) && compatible(a.detail ?? {}, b.detail ?? {});\n}","finish":"function requirePathToFinal(states) {\n  const canFinish = new Set(states.filter(state => state.final).map(state => state.name));\n  let changed = true;\n  while (changed) {\n    changed = false;\n    for (const state of states) if (!canFinish.has(state.name) && state.transitions.some(t => canFinish.has(t.target))) {\n      canFinish.add(state.name); changed = true;\n    }\n  }\n  const dead = states.filter(state => !canFinish.has(state.name)).map(state => state.name);\n  if (dead.length) fail(`states with no path to a final state: ${dead.join(', ')}`);\n}","compatible":"const compatible = (a, b) => Object.keys(a).every(key => !Object.hasOwn(b, key) || jsonEqual(a[key], b[key]));","equal":"const jsonEqual = (a, b) => {\n  if (a === b) return true;\n  if (!a || !b || typeof a !== 'object' || typeof b !== 'object' || Array.isArray(a) !== Array.isArray(b)) return false;\n  const keys = Object.keys(a);\n  return keys.length === Object.keys(b).length && keys.every(key => Object.hasOwn(b, key) && jsonEqual(a[key], b[key]));\n};","compile":["const names = validate(config);","const machine = createMachine(config);","const states = names.map(name => {\n    const node = machine.states[name];\n    return { name, final: node.type === 'final', transitions: [...node.transitions].flatMap(([event, branches]) => branches.map(branch => ({ event, target: branch.target[0].key, expect: branch.guard.params }))) };\n  });","const byName = new Map(states.map(state => [state.name, state]));","const reached = new Set([config.initial]), queue = [config.initial];","for (const name of queue) for (const transition of byName.get(name).transitions) if (!reached.has(transition.target)) { reached.add(transition.target); queue.push(transition.target); }","if (reached.size !== names.length) fail(`unreachable states: ${names.filter(name => !reached.has(name)).join(', ')}`);"]};
function expectAst(actual: Acorn.Node, pattern: string, label: string) {
  const expected = acorn.parse(pattern, {ecmaVersion: 'latest'}).body[0];
  if (JSON.stringify(semantic(actual)) !== JSON.stringify(semantic(expected)))
    throw Error('unsupported executable AST: ' + label);
}
function variable(name: string) {
  const nodes = tree.body.flatMap(node => node.type === 'VariableDeclaration' ? node.declarations : [])
    .filter(node => (node.id as Acorn.Identifier).name === name);
  if (nodes.length !== 1) throw Error('unsupported executable AST: ' + name);
  return nodes[0];
}
function expectVariable(name: string, pattern: string) {
  const expected = (acorn.parse(pattern, {ecmaVersion: 'latest'}).body[0] as Acorn.VariableDeclaration).declarations[0];
  if (JSON.stringify(semantic(variable(name))) !== JSON.stringify(semantic(expected)))
    throw Error('unsupported executable AST: ' + name);
}
try {
  const bound = new Set(['validate', 'validateTransition', 'compile', 'guardsOverlap', 'compatible', 'jsonEqual', 'requirePathToFinal', 'fail']);
  if (walk(tree, n => (n.type === 'AssignmentExpression' || n.type === 'UpdateExpression') &&
      ((n as Acorn.AssignmentExpression).left || (n as Acorn.UpdateExpression).argument).type === 'Identifier' && bound.has((((n as Acorn.AssignmentExpression).left || (n as Acorn.UpdateExpression).argument) as Acorn.Identifier).name)).length)
    throw Error('unsupported executable AST: reassigned bound name');
  const validate = func('validate'), compile = func('compile');
  const validateTypes = validate.body.body.map(n => n.type).join(',');
  const expected = 'ExpressionStatement,ExpressionStatement,ExpressionStatement,IfStatement,VariableDeclaration,IfStatement,IfStatement,VariableDeclaration,ForOfStatement,IfStatement,ReturnStatement';
  if (validateTypes !== expected) throw Error('unsupported validator shape');
  const fails = walk(tree, n => n.type === 'VariableDeclarator' && (n.id as Acorn.Identifier).name === 'fail');
  if (fails.length !== 1 || code(fails[0]) !== 'fail=message=>{thrownewError(message);}') throw Error('unsupported failure helper');
  requireText(validate, 'validateTransition(transition, config.states)');
  requireText(compile, 'const names = validate(config)');
  requireText(compile, 'if (reached.size !== names.length)');
  console.log(JSON.stringify({overlap: guardFact(validate), finish: finishFact(compile)}));
} catch (error) { console.error((error as Error).message); process.exit(1); }
