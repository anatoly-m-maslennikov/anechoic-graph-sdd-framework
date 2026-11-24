import fs from 'node:fs';
import {createRequire} from 'node:module';
const require = createRequire(new URL('../IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/package.json', import.meta.url));
const ts = require('typescript');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = [], trees = new Map(), links = new Map();
const clean = value => value?.replace(/^module:/, '');
function add(file, node, rule, status, detail) {
  const p = trees.get(file).getLineAndCharacterOfPosition(node.getStart());
  out.push([file, p.line + 1, p.character, rule, status, detail]);
}
function kind(file) {
  return file.endsWith('.tsx') ? ts.ScriptKind.TSX : file.endsWith('.jsx') ? ts.ScriptKind.JSX
    : /\.[cm]?js$/.test(file) ? ts.ScriptKind.JS : ts.ScriptKind.TS;
}
for (const [file, text] of Object.entries(input.sources)) {
  trees.set(file, ts.createSourceFile(file, text, ts.ScriptTarget.Latest, true, kind(file)));
}
for (const [, source, target, written, line, column, status] of input.occurrences) {
  const from = clean(source), to = clean(target);
  if (status !== 'internal' || !trees.has(from) || !trees.has(to)) continue;
  const list = links.get(from) || [];
  list.push({to, written, line, column}); links.set(from, list);
}

let opts = null;
if (input.config !== null) {
  const parsed = ts.parseConfigFileTextToJson('tsconfig.json', input.config);
  const raw = parsed.config;
  if (!parsed.error && raw && !raw.extends && !raw.references && raw.compilerOptions) {
    const converted = ts.convertCompilerOptionsFromJson(raw.compilerOptions, '/');
    if (!converted.errors.length && raw.compilerOptions.verbatimModuleSyntax === true
        && !raw.compilerOptions.plugins && !raw.compilerOptions.customTransformers) opts = converted.options;
  }
}
const emittedCache = new Map();
function runtimeImport(file, node) {
  if (!/\.[cm]?tsx?$/.test(file) || !ts.isImportDeclaration(node)) return null;
  if (node.importClause?.isTypeOnly) return 'erased declaration-level type import';
  if (!opts || input.nested.includes(file)) return null;
  const source = trees.get(file).text;
  const duplicates = trees.get(file).statements.filter(n => ts.isImportDeclaration(n)
    && n.moduleSpecifier.text === node.moduleSpecifier.text);
  if (duplicates.length !== 1) return null;
  if (!emittedCache.has(file)) emittedCache.set(file, ts.transpileModule(source,
    {compilerOptions: opts, fileName: file, reportDiagnostics: true}));
  const result = emittedCache.get(file);
  if (result.diagnostics?.some(d => d.category === ts.DiagnosticCategory.Error)) return null;
  const emitted = ts.createSourceFile('output.js', result.outputText, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  const spec = node.moduleSpecifier.text;
  let found = false;
  function visit(n) {
    if ((ts.isImportDeclaration(n) && n.moduleSpecifier.text === spec)
      || (ts.isCallExpression(n) && ts.isIdentifier(n.expression) && n.expression.text === 'require'
        && n.arguments.length === 1 && ts.isStringLiteral(n.arguments[0]) && n.arguments[0].text === spec)) found = true;
    ts.forEachChild(n, visit);
  }
  visit(emitted);
  return found ? 'compiler emit preserves module evaluation' : 'compiler emit erases import';
}
function countIdentifier(tree, name) {
  let count = 0, todo = [tree];
  while (todo.length) {
    const n = todo.pop();
    if (ts.isIdentifier(n) && n.text === name) count++;
    ts.forEachChild(n, child => { todo.push(child); });
  }
  return count;
}
function effect(file, statement) {
  if (!ts.isExpressionStatement(statement)) return;
  const e = statement.expression, tree = trees.get(file);
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
function reaches(start, target) {
  const seen = new Set(), todo = [start];
  while (todo.length) {
    const current = todo.pop();
    if (current === target) return true;
    if (seen.has(current)) continue;
    seen.add(current);
    for (const edge of links.get(current) || []) todo.push(edge.to);
  }
  return false;
}
function provenEsmRead(file, node, target) {
  if (!file.endsWith('.mjs') || !target.endsWith('.mjs')) return false;
  const a = trees.get(file), b = trees.get(target);
  if ((links.get(file) || []).length !== 1 || (links.get(target) || []).length !== 1
      || links.get(target)[0].to !== file) return false;
  const clause = node.importClause;
  if (!clause?.namedBindings || !ts.isNamedImports(clause.namedBindings)
      || clause.name || clause.namedBindings.elements.length !== 1) return false;
  const binding = clause.namedBindings.elements[0];
  if (binding.isTypeOnly) return false;
  const local = binding.name.text, exported = (binding.propertyName || binding.name).text;
  const valid = (tree, expected) => tree.statements.length === 2
    && tree.statements.filter(ts.isImportDeclaration).length === 1
    && tree.statements.some(expected);
  const decl = (statement, test) => ts.isVariableStatement(statement)
    && (statement.declarationList.flags & ts.NodeFlags.Const) !== 0
    && statement.declarationList.declarations.length === 1
    && test(statement.declarationList.declarations[0], statement);
  return valid(a, s => decl(s, d => ts.isIdentifier(d.name)
      && d.initializer && ts.isIdentifier(d.initializer) && d.initializer.text === local))
    && valid(b, s => decl(s, (d, st) => ts.isIdentifier(d.name) && d.name.text === exported
      && st.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword)
      && d.initializer && (ts.isStringLiteral(d.initializer) || ts.isNumericLiteral(d.initializer))));
}
function cjsShape(file, edge) {
  const tree = trees.get(file);
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
function provenCjsRead(file, edge) {
  if ((links.get(file) || []).length !== 1 || (links.get(edge.to) || []).length !== 1) return null;
  const back = links.get(edge.to)[0];
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
    const tree = trees.get(file);
    const node = tree.statements.find(n => {
      const p = tree.getLineAndCharacterOfPosition(n.getStart(tree));
      return p.line + 1 === edge.line && ts.isImportDeclaration(n) && n.moduleSpecifier.text === edge.written;
    });
    if (!node) {
      let requireSite = null;
      function findRequire(n) {
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
