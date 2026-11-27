import fs from 'node:fs';
import {createRequire} from 'node:module';
const require = createRequire(new URL('../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/package.json', import.meta.url));
const ts: typeof import('../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript') =
  require('typescript');

type Node = Parameters<typeof ts.isIdentifier>[0];
type SourceFile = ReturnType<typeof ts.createSourceFile>;
type Statement = SourceFile['statements'][number];
type ImportDeclaration = ReturnType<typeof ts.factory.createImportDeclaration>;
type VariableStatement = ReturnType<typeof ts.factory.createVariableStatement>;
type VariableDeclaration = ReturnType<typeof ts.factory.createVariableDeclaration>;
type CallExpression = ReturnType<typeof ts.factory.createCallExpression>;
type CompilerOptions = Parameters<typeof ts.createProgram>[1];
type Occurrence = [id: string, source: string, target: string | null, written: string, line: number,
  column: number, status: string, typeOnly: boolean];
type Edge = {to: string; written: string; line: number; column: number};
type Rule = 'web_module_evaluation' | 'typescript_runtime_import';
type Status = 'confirmed' | 'unresolved';
type Finding = [file: string, line: number, column: number, rule: Rule, status: Status, detail: string];

const input: { sources: Record<string, string>; occurrences: Occurrence[]; config: string | null; nested: string[] } =
  JSON.parse(fs.readFileSync(0, 'utf8'));
const out: Finding[] = [];
const trees = new Map<string, SourceFile>(), links = new Map<string, Edge[]>();
const clean = (value: string | null) => value?.replace(/^module:/, '');
function add(file: string, node: Node, rule: Rule, status: Status, detail: string) {
  const p = trees.get(file)!.getLineAndCharacterOfPosition(node.getStart());
  out.push([file, p.line + 1, p.character, rule, status, detail]);
}
function kind(file: string) {
  return file.endsWith('.tsx') ? ts.ScriptKind.TSX : file.endsWith('.jsx') ? ts.ScriptKind.JSX
    : /\.[cm]?js$/.test(file) ? ts.ScriptKind.JS : ts.ScriptKind.TS;
}
for (const [file, text] of Object.entries(input.sources)) {
  trees.set(file, ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true, kind(file)));
}
for (const [, source, target, written, line, column, status] of input.occurrences) {
  const from = clean(source), to = clean(target);
  if (status !== 'internal' || from === undefined || to === undefined || !trees.has(from) || !trees.has(to)) continue;
  const list = links.get(from) || [];
  list.push({to, written, line, column}); links.set(from, list);
}

let opts: CompilerOptions | null = null;
if (input.config !== null) {
  const parsed = ts.parseConfigFileTextToJson('tsconfig.json', input.config);
  const raw = parsed.config;
  if (!parsed.error && raw && !raw.extends && !raw.references && raw.compilerOptions) {
    const converted = ts.convertCompilerOptionsFromJson(raw.compilerOptions, '/');
    if (!converted.errors.length && raw.compilerOptions.verbatimModuleSyntax === true
        && !raw.compilerOptions.plugins && !raw.compilerOptions.customTransformers) opts = converted.options;
  }
}
const emittedCache = new Map<string, ReturnType<typeof ts.transpileModule>>();
function importText(node: ImportDeclaration) {
  return (node.moduleSpecifier as Node & {text?: string}).text;
}
function runtimeImport(file: string, node: Node) {
  if (!/\.[cm]?tsx?$/.test(file) || !ts.isImportDeclaration(node)) return null;
  if (node.importClause?.isTypeOnly) return 'erased declaration-level type import';
  if (!opts || input.nested.includes(file)) return null;
  const tree = trees.get(file)!;
  const spec = importText(node);
  const duplicates = tree.statements.filter(n => ts.isImportDeclaration(n) && importText(n) === spec);
  if (duplicates.length !== 1) return null;
  let result = emittedCache.get(file);
  if (!result) {
    result = ts.transpileModule(tree.text, {compilerOptions: opts, fileName: file, reportDiagnostics: true});
    emittedCache.set(file, result);
  }
  if (result.diagnostics?.some(d => d.category === ts.DiagnosticCategory.Error)) return null;
  const emitted = ts.createSourceFile('output.js', result.outputText, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  let found = false;
  function visit(n: Node) {
    if ((ts.isImportDeclaration(n) && importText(n) === spec)
      || (ts.isCallExpression(n) && ts.isIdentifier(n.expression) && n.expression.text === 'require'
        && n.arguments.length === 1 && ts.isStringLiteral(n.arguments[0]) && n.arguments[0].text === spec)) found = true;
    ts.forEachChild(n, visit);
  }
  visit(emitted);
  return found ? 'compiler emit preserves module evaluation' : 'compiler emit erases import';
}
function countIdentifier(tree: SourceFile, name: string) {
  let count = 0;
  const todo: Node[] = [tree];
  while (todo.length) {
    const n = todo.pop()!;
    if (ts.isIdentifier(n) && n.text === name) count++;
    ts.forEachChild(n, child => { todo.push(child); });
  }
  return count;
}
function effect(file: string, statement: Statement) {
  if (!ts.isExpressionStatement(statement)) return;
  const e = statement.expression, tree = trees.get(file)!;
  const consoleOutput = ts.isCallExpression(e) && ts.isPropertyAccessExpression(e.expression)
    && ts.isIdentifier(e.expression.expression) && e.expression.expression.text === 'console'
    && ['log', 'info', 'warn', 'error'].includes(e.expression.name.text)
    && countIdentifier(tree, 'console') === 1;
  const envWrite = ts.isBinaryExpression(e) && e.operatorToken.kind === ts.SyntaxKind.EqualsToken
    && ts.isPropertyAccessExpression(e.left) && ts.isPropertyAccessExpression(e.left.expression)
    && ts.isIdentifier(e.left.expression.expression) && e.left.expression.expression.text === 'process'
    && e.left.expression.name.text === 'env' && countIdentifier(tree, 'process') === 1;
  if (consoleOutput || envWrite) {
    add(file, statement, 'web_module_evaluation', 'confirmed',
      consoleOutput ? 'top-level console output' : 'top-level process.env write');
  } else if (ts.isCallExpression(e) || ts.isNewExpression(e) || ts.isAwaitExpression(e)
      || (ts.isBinaryExpression(e) && e.operatorToken.kind >= ts.SyntaxKind.FirstAssignment
        && e.operatorToken.kind <= ts.SyntaxKind.LastAssignment) || ts.isPostfixUnaryExpression(e)) {
    add(file, statement, 'web_module_evaluation', 'unresolved', 'top-level expression may have an effect');
  }
}
for (const [file, tree] of trees) {
  for (const node of tree.statements) {
    effect(file, node);
    if (/\.[cm]?tsx?$/.test(file) && ts.isImportDeclaration(node)) {
      const evidence = runtimeImport(file, node);
      add(file, node, 'typescript_runtime_import', evidence ? 'confirmed' : 'unresolved',
        evidence || 'effective TypeScript emit is not established');
    }
  }
}
function reaches(start: string, target: string) {
  const seen = new Set<string>(), todo = [start];
  while (todo.length) {
    const current = todo.pop()!;
    if (current === target) return true;
    if (seen.has(current)) continue;
    seen.add(current);
    for (const edge of links.get(current) || []) todo.push(edge.to);
  }
  return false;
}
function provenEsmRead(file: string, node: ImportDeclaration, target: string) {
  if (!file.endsWith('.mjs') || !target.endsWith('.mjs')) return false;
  const a = trees.get(file)!, b = trees.get(target)!;
  if ((links.get(file) || []).length !== 1 || (links.get(target) || []).length !== 1
      || links.get(target)![0].to !== file) return false;
  const clause = node.importClause;
  if (!clause?.namedBindings || !ts.isNamedImports(clause.namedBindings)
      || clause.name || clause.namedBindings.elements.length !== 1) return false;
  const binding = clause.namedBindings.elements[0];
  if (binding.isTypeOnly) return false;
  const local = binding.name.text, exported = (binding.propertyName || binding.name).text;
  const valid = (tree: SourceFile, expected: (statement: Statement) => boolean) => tree.statements.length === 2
    && tree.statements.filter(ts.isImportDeclaration).length === 1
    && tree.statements.some(expected);
  const decl = (statement: Statement, test: (declaration: VariableDeclaration, statement: VariableStatement) => boolean) =>
    ts.isVariableStatement(statement)
    && (statement.declarationList.flags & ts.NodeFlags.Const) !== 0
    && statement.declarationList.declarations.length === 1
    && test(statement.declarationList.declarations[0], statement);
  return valid(a, s => decl(s, d => ts.isIdentifier(d.name)
      && d.initializer !== undefined && ts.isIdentifier(d.initializer) && d.initializer.text === local))
    && valid(b, s => decl(s, (d, st) => ts.isIdentifier(d.name) && d.name.text === exported
      && st.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword) === true
      && d.initializer !== undefined && (ts.isStringLiteral(d.initializer) || ts.isNumericLiteral(d.initializer))));
}
function cjsShape(file: string, edge: Edge) {
  const tree = trees.get(file)!;
  if (!file.endsWith('.cjs') || tree.statements.length !== 2) return null;
  const [first, second] = tree.statements;
  if (!ts.isVariableStatement(first) || !(first.declarationList.flags & ts.NodeFlags.Const)
      || first.declarationList.declarations.length !== 1) return null;
  const decl = first.declarationList.declarations[0], call = decl.initializer;
  if (!ts.isIdentifier(decl.name) || !call || !ts.isCallExpression(call)
      || !ts.isIdentifier(call.expression) || call.expression.text !== 'require'
      || call.arguments.length !== 1 || !ts.isStringLiteral(call.arguments[0])
      || call.arguments[0].text !== edge.written) return null;
  if (!ts.isExpressionStatement(second) || !ts.isBinaryExpression(second.expression)) return null;
  const assign = second.expression, left = assign.left;
  if (assign.operatorToken.kind !== ts.SyntaxKind.EqualsToken || !ts.isPropertyAccessExpression(left)
      || !ts.isIdentifier(left.expression) || left.expression.text !== 'exports'
      || ['require', 'exports', 'module'].includes(decl.name.text)) return null;
  return {dep: decl.name.text, name: left.name.text, value: assign.right, statement: second};
}
function provenCjsRead(file: string, edge: Edge) {
  if ((links.get(file) || []).length !== 1 || (links.get(edge.to) || []).length !== 1) return null;
  const back = links.get(edge.to)![0];
  if (back.to !== file) return null;
  const reader = cjsShape(file, edge), target = cjsShape(edge.to, back);
  if (!reader || !target || Object.hasOwn(Object.prototype, target.name)) return null;
  const expr = reader.value;
  if (!ts.isPropertyAccessExpression(expr) || expr.questionDotToken
      || !ts.isPropertyAccessExpression(expr.expression) || expr.expression.questionDotToken
      || !ts.isIdentifier(expr.expression.expression) || expr.expression.expression.text !== reader.dep
      || expr.expression.name.text !== target.name || expr.name.text === '__proto__') return null;
  const obj = target.value;
  if (!ts.isObjectLiteralExpression(obj) || obj.properties.length !== 1) return null;
  const prop = obj.properties[0];
  if (!ts.isPropertyAssignment(prop) || !ts.isIdentifier(prop.name) || prop.name.text !== expr.name.text
      || !(ts.isStringLiteral(prop.initializer) || ts.isNumericLiteral(prop.initializer)
        || [ts.SyntaxKind.TrueKeyword, ts.SyntaxKind.FalseKeyword, ts.SyntaxKind.NullKeyword].includes(prop.initializer.kind))) return null;
  return reader.statement;
}
for (const [file, edges] of links) {
  for (const edge of edges) {
    if (!reaches(edge.to, file)) continue;
    const tree = trees.get(file)!;
    const node = tree.statements.find((n): n is ImportDeclaration => {
      const p = tree.getLineAndCharacterOfPosition(n.getStart(tree));
      return p.line + 1 === edge.line && ts.isImportDeclaration(n) && importText(n) === edge.written;
    });
    if (!node) {
      let requireSite: CallExpression | null = null;
      function findRequire(n: Node) {
        const p = tree.getLineAndCharacterOfPosition(n.getStart(tree));
        if (ts.isCallExpression(n) && ts.isIdentifier(n.expression) && n.expression.text === 'require'
            && n.arguments.length === 1 && ts.isStringLiteral(n.arguments[0])
            && n.arguments[0].text === edge.written && p.line + 1 === edge.line) requireSite = n;
        ts.forEachChild(n, findRequire);
      }
      findRequire(tree);
      if (requireSite) {
        const witness = provenCjsRead(file, edge);
        add(file, witness || requireSite, 'web_module_evaluation', witness ? 'confirmed' : 'unresolved',
          witness ? `entering ${edge.to} reads an undefined partial CommonJS export and throws`
            : 'structural CommonJS cycle; loader and binding read require review');
      }
      continue;
    }
    const evidence = runtimeImport(file, node);
    if (evidence?.startsWith('erased') || evidence === 'compiler emit erases import') continue;
    const proven = provenEsmRead(file, node, edge.to);
    add(file, node, 'web_module_evaluation', proven ? 'confirmed' : 'unresolved',
      proven ? 'cyclic ESM binding read depends on entry module and can access an uninitialized binding'
        : 'structural import cycle; evaluation order and binding reads require review');
  }
}
process.stdout.write(JSON.stringify(out));
