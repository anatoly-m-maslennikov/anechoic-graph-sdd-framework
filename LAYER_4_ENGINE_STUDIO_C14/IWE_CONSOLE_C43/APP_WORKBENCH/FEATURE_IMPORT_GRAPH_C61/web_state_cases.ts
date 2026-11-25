import fs from 'node:fs';
import { createRequire } from 'node:module';
import type * as compiler from '../FEATURE_WORKBENCH_FRONTEND/node_modules/typescript';

const require = createRequire(new URL('../FEATURE_WORKBENCH_FRONTEND/package.json', import.meta.url));
const ts: typeof compiler = require('typescript');
const unknown = Symbol('unknown');

type Value = string | number | boolean | null | undefined | typeof unknown;
type StateTarget = ['local', '$owner'] | ['ambient', 'ENV'];
type EventKind = 'call' | 'read' | 'write' | 'return' | 'output';
type StateEvent = {kind: EventKind; target: StateTarget[0] | ''; name: string; line: number; forward?: boolean};
type Input = Record<string, boolean>;
type StateCase = {
  action: string;
  line: number;
  column?: number;
  inlineable?: boolean;
  input: Input | null;
  reachable: true; complete: boolean; declaredNoOp: false;
  events: StateEvent[];
};
type CallTargets = Map<string, string> | null;
type Sources = Record<string, string>;
type GraphPayload = {sources: Sources; call_sites: Record<string, [number, number, string][]>};
type Context = {
  tree: compiler.SourceFile;
  outer: Set<string>;
  objects: Set<string>;
  shadow: Set<string>;
  calls: CallTargets;
  body: compiler.ConciseBody | undefined;
  locals: Map<string, Value>;
  aliases: Map<string, StateTarget>;
  events: StateEvent[];
  complete: boolean;
  stopped: boolean;
};

function line(tree: compiler.SourceFile, node: compiler.Node) { return tree.getLineAndCharacterOfPosition(node.getStart(tree)).line + 1; }
function event(ctx: Context, node: compiler.Node, kind: EventKind, ...[target, name]: StateTarget | ['', '']) {
  ctx.events.push({kind, target, name, line: line(ctx.tree, node)});
}
function graphCall(ctx: Context, expr: compiler.Expression, forward: boolean) {
  const node = unwrap(expr);
  if (!ctx.complete || !ctx.calls || !ts.isCallExpression(node) || node.questionDotToken ||
      node.arguments.length) return false;
  const pos = ctx.tree.getLineAndCharacterOfPosition(node.getStart(ctx.tree));
  const target = ctx.calls.get(`${pos.line + 1}:${pos.character}`);
  if (!target) return false;
  ctx.events.push({kind: 'call', target: '', name: target, line: pos.line + 1, forward});
  return true;
}
function bad(ctx: Context): typeof unknown { ctx.complete = false; ctx.stopped = true; return unknown; }
function unwrap(node: compiler.Expression): compiler.Expression {
  while (ts.isParenthesizedExpression(node) || ts.isAsExpression(node) ||
      ts.isTypeAssertionExpression(node) || ts.isNonNullExpression(node)) node = node.expression;
  return node;
}
function stateTarget(ctx: Context, node: compiler.Expression): StateTarget | null {
  node = unwrap(node);
  if (ts.isIdentifier(node)) {
    if (ctx.locals.has(node.text)) return ctx.aliases.get(node.text) || null;
    return ctx.outer.has(node.text) ? ['local', '$owner'] : null;
  }
  if (ts.isPropertyAccessExpression(node) || ts.isElementAccessExpression(node)) {
    if (node.getText(ctx.tree).match(/^process\.env(?:\.[A-Za-z_$][\w$]*|\[['"][^'"]+['"]\])?$/) &&
        !ctx.shadow.has('process') && !ctx.locals.has('process') && !ctx.outer.has('process')) return ['ambient', 'ENV'];
    if (ts.isElementAccessExpression(node) && literal(node.argumentExpression) === unknown) return null;
    const base = unwrap(node.expression);
    if (!ts.isIdentifier(base) ||
        (!ctx.objects.has(base.text) && !ctx.aliases.has(base.text))) return null;
    return stateTarget(ctx, node.expression);
  }
  return null;
}
function stateRead(ctx: Context, node: compiler.Expression) {
  const target = stateTarget(ctx, node);
  if (!target) return false;
  event(ctx, node, 'read', ...target);
  return true;
}
function literal(node: compiler.Node): Value {
  if (node.kind === ts.SyntaxKind.TrueKeyword) return true;
  if (node.kind === ts.SyntaxKind.FalseKeyword) return false;
  if (node.kind === ts.SyntaxKind.NullKeyword) return null;
  if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) return node.text;
  if (ts.isNumericLiteral(node)) return Number(node.text);
  return unknown;
}
function evaluate(ctx: Context, expr: compiler.Expression): Value {
  const node = unwrap(expr);
  const value = literal(node);
  if (value !== unknown) return value;
  if (ts.isIdentifier(node)) {
    if (ctx.locals.has(node.text)) {
      const v = ctx.locals.get(node.text);
      if (v === unknown) bad(ctx);
      return v;
    }
    return stateRead(ctx, node) ? unknown : bad(ctx);
  }
  if (ts.isPropertyAccessExpression(node) ||
      (ts.isElementAccessExpression(node) && literal(node.argumentExpression) !== unknown)) {
    return stateRead(ctx, node) ? unknown : bad(ctx);
  }
  if (ts.isPrefixUnaryExpression(node) && node.operator === ts.SyntaxKind.ExclamationToken) {
    const v = evaluate(ctx, node.operand); return v === unknown ? unknown : !v;
  }
  if (ts.isBinaryExpression(node)) return binary(ctx, node);
  return bad(ctx);
}
function binary(ctx: Context, node: compiler.BinaryExpression): Value {
  const op = node.operatorToken.kind;
  if (op === ts.SyntaxKind.EqualsToken) {
    const value = evaluate(ctx, node.right), target = stateTarget(ctx, node.left);
    if (!ctx.complete) return unknown;
    if (ts.isIdentifier(node.left) && ctx.locals.has(node.left.text)) {
      ctx.locals.set(node.left.text, value); ctx.aliases.delete(node.left.text);
    } else if (ts.isIdentifier(node.left) && ctx.objects.has(node.left.text)) {
      bad(ctx);
    } else if (target) event(ctx, node.left, 'write', ...target);
    else bad(ctx);
    return value;
  }
  const a = evaluate(ctx, node.left);
  if ((op === ts.SyntaxKind.AmpersandAmpersandToken || op === ts.SyntaxKind.BarBarToken) && a === unknown) return bad(ctx);
  if (op === ts.SyntaxKind.AmpersandAmpersandToken && a !== unknown && !a) return a;
  if (op === ts.SyntaxKind.BarBarToken && a !== unknown && a) return a;
  const b = evaluate(ctx, node.right);
  if (a === unknown || b === unknown) return unknown;
  switch (op) {
    case ts.SyntaxKind.EqualsEqualsEqualsToken: return a === b;
    case ts.SyntaxKind.ExclamationEqualsEqualsToken: return a !== b;
    case ts.SyntaxKind.AmpersandAmpersandToken: return a && b;
    case ts.SyntaxKind.BarBarToken: return a || b;
    default: return bad(ctx);
  }
}
function statement(ctx: Context, node: compiler.Statement) {
  if (ctx.stopped) return;
  if (ts.isBlock(node)) {
    if (node !== ctx.body && bindings(node).size) { bad(ctx); return; }
    for (const child of node.statements) statement(ctx, child); return;
  }
  if (ts.isEmptyStatement(node)) return;
  if (ts.isReturnStatement(node)) {
    if (node.expression && !graphCall(ctx, node.expression, true)) {
      evaluate(ctx, node.expression); if (ctx.complete) event(ctx, node, ctx.calls ? 'return' : 'output', '', '');
    }
    ctx.stopped = true; return;
  }
  if (ts.isIfStatement(node)) {
    const condition = evaluate(ctx, node.expression);
    if (condition === unknown) { bad(ctx); return; }
    if (condition) statement(ctx, node.thenStatement);
    else if (node.elseStatement) statement(ctx, node.elseStatement);
    return;
  }
  if (ts.isVariableStatement(node)) {
    for (const decl of node.declarationList.declarations) {
      if (!ts.isIdentifier(decl.name)) { bad(ctx); continue; }
      const alias = decl.initializer && stateTarget(ctx, decl.initializer);
      const value = decl.initializer ? evaluate(ctx, decl.initializer) : undefined;
      ctx.locals.set(decl.name.text, value);
      if (alias && decl.initializer && ts.isIdentifier(decl.initializer) &&
          (ctx.objects.has(decl.initializer.text) || ctx.aliases.has(decl.initializer.text))) ctx.aliases.set(decl.name.text, alias);
    }
    return;
  }
  if (ts.isExpressionStatement(node)) { expressionStatement(ctx, node.expression); return; }
  bad(ctx);
}
function expressionStatement(ctx: Context, node: compiler.Expression) {
  node = unwrap(node);
  if (ts.isCallExpression(node) && node.expression.getText(ctx.tree) === 'console.log' &&
      !ctx.shadow.has('console') && !ctx.locals.has('console') && !ctx.outer.has('console')) {
    for (const arg of node.arguments) evaluate(ctx, arg);
    if (ctx.complete) event(ctx, node, 'output', '', ''); return;
  }
  if (graphCall(ctx, node, false)) return;
  if ((ts.isPostfixUnaryExpression(node) || ts.isPrefixUnaryExpression(node)) &&
      (node.operator === ts.SyntaxKind.PlusPlusToken || node.operator === ts.SyntaxKind.MinusMinusToken)) {
    const target = stateTarget(ctx, node.operand);
    if (!target) { bad(ctx); return; }
    event(ctx, node.operand, 'read', ...target); event(ctx, node.operand, 'write', ...target); return;
  }
  evaluate(ctx, node);
}
function bindings(node: compiler.Block) {
  const names = new Set<string>();
  for (const stmt of node.statements || []) {
    if (ts.isVariableStatement(stmt)) for (const decl of stmt.declarationList.declarations)
      if (ts.isIdentifier(decl.name) && !stmt.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) names.add(decl.name.text);
  }
  return names;
}
function runCase(tree: compiler.SourceFile, fn: compiler.FunctionLikeDeclaration, name: string, outer: Set<string>,
  objects: Set<string>, input: Input | null, shadow: Set<string>, calls: CallTargets): StateCase {
  const ctx: Context = {tree, outer, objects, shadow, calls, body: fn.body, locals: new Map(Object.entries(input || {})),
    aliases: new Map(), events: [], complete: input !== null, stopped: false};
  if (fn.body) {
    if (ts.isBlock(fn.body)) {
      for (const name of bindings(fn.body)) if (!ctx.locals.has(name)) ctx.locals.set(name, unknown);
      statement(ctx, fn.body);
    }
    else if (!graphCall(ctx, fn.body, true)) {
      evaluate(ctx, fn.body); if (ctx.complete) event(ctx, fn.body, calls ? 'return' : 'output', '', '');
    }
  } else bad(ctx);
  const position = tree.getLineAndCharacterOfPosition(fn.getStart(tree));
  return {action: name, line: line(tree, fn), ...(calls ? {column: position.character,
    inlineable: ctx.complete && fn.parameters.length === 0 && !ts.isMethodDeclaration(fn)} : {}), input: ctx.complete ? input : null,
    reachable: true, complete: ctx.complete, declaredNoOp: false, events: ctx.events};
}
function inputs(fn: compiler.FunctionLikeDeclaration): (Input | null)[] {
  if (fn.asteriskToken || fn.modifiers?.some(m => m.kind === ts.SyntaxKind.AsyncKeyword)) return [null];
  if (fn.parameters.length > 4) return [null];
  let rows: Input[] = [{}];
  for (const p of fn.parameters) {
    if (!ts.isIdentifier(p.name) || p.dotDotDotToken || p.initializer || p.questionToken ||
        p.type?.kind !== ts.SyntaxKind.BooleanKeyword) return [null];
    const name = p.name.text;
    rows = rows.flatMap(row => [false, true].map(v => ({...row, [name]: v})));
  }
  return rows;
}
function staticInitializer(node: compiler.Expression | undefined): boolean {
  if (!node) return true;
  node = unwrap(node);
  if (literal(node) !== unknown) return true;
  if (ts.isArrayLiteralExpression(node)) return node.elements.every(staticInitializer);
  if (ts.isObjectLiteralExpression(node)) return node.properties.every(p =>
    ts.isPropertyAssignment(p) && !ts.isComputedPropertyName(p.name) && staticInitializer(p.initializer));
  return false;
}
function moduleCase(tree: compiler.SourceFile): StateCase {
  const row: StateCase = {action: '<module>', line: 1, input: {}, reachable: true, complete: true, declaredNoOp: false, events: []};
  for (const stmt of tree.statements) {
    if (ts.isFunctionDeclaration(stmt) || ts.isInterfaceDeclaration(stmt) || ts.isTypeAliasDeclaration(stmt) || ts.isEmptyStatement(stmt)) continue;
    if (!ts.isVariableStatement(stmt) || stmt.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) { row.complete = false; break; }
    for (const decl of stmt.declarationList.declarations) {
      if (!ts.isIdentifier(decl.name) || !staticInitializer(decl.initializer)) { row.complete = false; break; }
      const mutable = !(stmt.declarationList.flags & ts.NodeFlags.Const) ||
        (decl.initializer && (ts.isObjectLiteralExpression(decl.initializer) || ts.isArrayLiteralExpression(decl.initializer)));
      if (mutable) row.events.push({kind: 'write', target: 'local', name: '$owner', line: line(tree, decl)});
    }
    if (!row.complete) break;
  }
  if (!row.complete) row.input = null;
  return row;
}
function scan(path: string, text: string, calls: CallTargets): StateCase[] {
  const kind = /\.tsx$/i.test(path) ? ts.ScriptKind.TSX : /\.[cm]?tsx?$/i.test(path) ? ts.ScriptKind.TS : ts.ScriptKind.JSX;
  const tree = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, true, kind) as
    compiler.SourceFile & {parseDiagnostics: readonly compiler.Diagnostic[]};
  if (tree.parseDiagnostics.length) return [{action: '<parse_error>', line: 1, input: null, reachable: true, complete: false, declaredNoOp: false, events: []}];
  const rows = [moduleCase(tree)], shadow = new Set<string>();
  function findShadow(node: compiler.Node) {
    if ((ts.isVariableDeclaration(node) || ts.isParameter(node) || ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node) || ts.isImportClause(node) || ts.isImportSpecifier(node) || ts.isNamespaceImport(node)) && node.name && ts.isIdentifier(node.name) && ['process', 'console'].includes(node.name.text)) shadow.add(node.name.text);
    ts.forEachChild(node, findShadow);
  }
  findShadow(tree);
  function visit(node: compiler.Node, outer: Set<string>, objects: Set<string>, nested: boolean) {
    if (ts.isFunctionDeclaration(node) || ts.isArrowFunction(node) || ts.isFunctionExpression(node)) {
      const name = ts.isFunctionDeclaration(node) ? node.name?.text :
        ts.isVariableDeclaration(node.parent) && ts.isIdentifier(node.parent.name) ? node.parent.name.text : undefined;
      if (name) for (const input of nested ? [null] : inputs(node)) rows.push(runCase(tree, node, name, outer, objects, input, shadow, calls));
    }
    let next = outer, nextObjects = objects;
    if (ts.isSourceFile(node) || (ts.isBlock(node) && ts.isFunctionLike(node.parent))) {
      next = new Set(outer);
      nextObjects = new Set(objects);
      for (const stmt of node.statements) if (ts.isVariableStatement(stmt) && !stmt.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword))
        for (const decl of stmt.declarationList.declarations) {
          if (!ts.isIdentifier(decl.name)) continue;
          const name = decl.name.text, initializer = decl.initializer && unwrap(decl.initializer);
          const object = initializer && (ts.isObjectLiteralExpression(initializer) || ts.isArrayLiteralExpression(initializer)) && staticInitializer(initializer);
          next.delete(name);
          nextObjects.delete(name);
          if (!(stmt.declarationList.flags & ts.NodeFlags.Const) || object) next.add(name);
          if (object && (stmt.declarationList.flags & ts.NodeFlags.Const)) nextObjects.add(name);
        }
      if (ts.isBlock(node) && ts.isFunctionLike(node.parent)) for (const p of node.parent.parameters)
        if (ts.isIdentifier(p.name)) next.add(p.name.text);
    }
    ts.forEachChild(node, child => visit(child, next, nextObjects, nested || ts.isFunctionLike(node)));
  }
  visit(tree, new Set(), new Set(), false); return rows;
}
try {
  const payload: unknown = JSON.parse(fs.readFileSync(0, 'utf8'));
  const graph = process.argv.includes('--graph'), graphPayload = payload as GraphPayload;
  const sources = graph ? graphPayload.sources : payload as Sources;
  const result = Object.fromEntries(Object.entries(sources).map(([path, text]) => {
    const calls = graph ? new Map((graphPayload.call_sites[path] || []).map(([line, column, target]) => [`${line}:${column}`, target])) : null;
    return [path, scan(path, text, calls)];
  }));
  process.stdout.write(JSON.stringify(result));
} catch (error) {
  process.stderr.write(String(error instanceof Error ? error.stack || error : error));
  process.exitCode = 1;
}
