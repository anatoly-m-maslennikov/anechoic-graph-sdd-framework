import fs from 'node:fs';
import { inputs, moduleCase, runCase, staticInitializer, unwrap }
  from './web_state_interpreter.ts';
import { createRequire } from 'node:module';
import type *
  as compiler from '../FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript';
import type {
  StateCase, CallTargets, Sources, GraphPayload,
} from './web_state_types';

const require = createRequire(new URL(
  '../FEATURE_IWE_CONSOLE_FRONTEND/package.json', import.meta.url,
));
const ts: typeof compiler = require('typescript');
function visit(node: compiler.Node, outer: Set<string>, objects: Set<string>,
  nested: boolean,
  tree: compiler.SourceFile, rows: StateCase[], shadow: Set<string>,
    calls: CallTargets) {
  if (ts.isFunctionDeclaration(node) || ts.isArrowFunction(node)
    || ts.isFunctionExpression(node)) {
    const name = ts.isFunctionDeclaration(node) ? node.name?.text :
      ts.isVariableDeclaration(node.parent)
        && ts.isIdentifier(node.parent.name) ? node.parent.name.text
          : undefined;
    if (name) for (const input of nested ? [null]
      : inputs(node)) rows.push(runCase(tree, node, name, outer, objects,
        input, shadow, calls));
  }
  let next = outer, nextObjects = objects;
  if (ts.isSourceFile(node) || (ts.isBlock(node)
    && ts.isFunctionLike(node.parent))) {
    next = new Set(outer);
    nextObjects = new Set(objects);
    for (const stmt of node.statements) if (ts.isVariableStatement(stmt)
      && !stmt.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword))
      for (const decl of stmt.declarationList.declarations) {
        if (!ts.isIdentifier(decl.name)) continue;
        const name = decl.name.text, initializer = decl.initializer
          && unwrap(decl.initializer);
        const object = initializer
          && (ts.isObjectLiteralExpression(initializer)
            || ts.isArrayLiteralExpression(initializer))
              && staticInitializer(initializer);
        next.delete(name);
        nextObjects.delete(name);
        if (!(stmt.declarationList.flags & ts.NodeFlags.Const)
          || object) next.add(name);
        if (object
          && (stmt.declarationList.flags & ts.NodeFlags.Const))
        nextObjects.add(name);
      }
    if (ts.isBlock(node)
      && ts.isFunctionLike(node.parent))
    for (const p of node.parent.parameters)
      if (ts.isIdentifier(p.name)) next.add(p.name.text);
  }
  ts.forEachChild(node, child => visit(child, next, nextObjects, nested
    || ts.isFunctionLike(node), tree, rows, shadow, calls));
}

function scan(path: string, text: string, calls: CallTargets): StateCase[] {
  const kind = /\.tsx$/i.test(path) ? ts.ScriptKind.TSX
    : /\.[cm]?tsx?$/i.test(path) ? ts.ScriptKind.TS : ts.ScriptKind.JSX;
  const tree = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, true,
    kind) as
    compiler.SourceFile & {parseDiagnostics: readonly compiler.Diagnostic[]};
  if (tree.parseDiagnostics.length) return [{action: '<parse_error>', line: 1,
    input: null, reachable: true, complete: false, declaredNoOp: false,
      events: []}];
  const rows = [moduleCase(tree)], shadow = new Set<string>();
  function findShadow(node: compiler.Node) {
    if ((ts.isVariableDeclaration(node) || ts.isParameter(node)
      || ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node)
        || ts.isImportClause(node) || ts.isImportSpecifier(node)
          || ts.isNamespaceImport(node)) && node.name
            && ts.isIdentifier(node.name) && ['process',
              'console'].includes(node.name.text)) shadow.add(node.name.text);
    ts.forEachChild(node, findShadow);
  }
  findShadow(tree);
  visit(tree, new Set(), new Set(), false, tree, rows, shadow, calls);
    return rows;
}
try {
  const payload: unknown = JSON.parse(fs.readFileSync(0, 'utf8'));
  const graph = process.argv.includes('--graph'),
    graphPayload = payload as GraphPayload;
  const sources = graph ? graphPayload.sources : payload as Sources;
  const result = Object.fromEntries(Object.entries(sources).map(([path,
    text]) => {
    const calls = graph ? new Map((graphPayload.call_sites[path]
      || []).map(([line, column, target]) => [`${line}:${column}`, target]))
        : null;
    return [path, scan(path, text, calls)];
  }));
  process.stdout.write(JSON.stringify(result));
} catch (error) {
  process.stderr.write(String(error instanceof Error ? error.stack || error
    : error));
  process.exitCode = 1;
}
