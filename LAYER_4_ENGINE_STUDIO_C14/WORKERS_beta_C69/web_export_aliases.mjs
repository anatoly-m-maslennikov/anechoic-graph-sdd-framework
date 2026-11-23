import fs from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';

const require = createRequire(new URL('../IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/package.json', import.meta.url));
const ts = require('typescript');
const {sources = {}, imports = {}} = JSON.parse(fs.readFileSync(0, 'utf8'));
const root = '/__anechoic_virtual__/';
const absolute = p => path.posix.normalize(root + p);
const names = new Map(Object.keys(sources).map(p => [absolute(p), p]));
function scriptKind(name) {
  if (name.endsWith('.tsx')) return ts.ScriptKind.TSX;
  if (name.endsWith('.jsx')) return ts.ScriptKind.JSX;
  return /\.[cm]?js$/.test(name) ? ts.ScriptKind.JS : ts.ScriptKind.TS;
}
const trees = new Map([...names].map(([file, name]) => [file, ts.createSourceFile(file, sources[name], ts.ScriptTarget.Latest, true, scriptKind(name))]));
const host = {
  getSourceFile: file => trees.get(path.posix.normalize(file)),
  getDefaultLibFileName: () => '', writeFile() {},
  getCurrentDirectory: () => root, getDirectories: () => [],
  fileExists: file => trees.has(path.posix.normalize(file)),
  readFile: file => trees.get(path.posix.normalize(file))?.text,
  getCanonicalFileName: file => file, useCaseSensitiveFileNames: () => true,
  getNewLine: () => '\n',
};
const program = ts.createProgram([...trees.keys()], {allowJs: true, noLib: true,
  module: ts.ModuleKind.ESNext, moduleDetection: ts.ModuleDetectionKind.Force,
  target: ts.ScriptTarget.Latest}, host);
const checker = program.getTypeChecker();
const exported = new Set(), bindings = new Map(), aliases = [], written = new Set(), writes = [];
function position(tree, node) {
  const p = tree.getLineAndCharacterOfPosition(node.getStart(tree));
  return [p.line + 1, p.character];
}
function isConst(node) {
  return ts.isVariableDeclaration(node) && ts.isVariableDeclarationList(node.parent) &&
    !!(node.parent.flags & ts.NodeFlags.Const);
}
function gatherExports(tree, file) {
  for (const statement of tree.statements) {
    if (!ts.isVariableStatement(statement) || !ts.getModifiers(statement)?.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) continue;
    for (const declaration of statement.declarationList.declarations) {
      if (isConst(declaration) && ts.isIdentifier(declaration.name) && declaration.initializer &&
          (ts.isObjectLiteralExpression(declaration.initializer) || ts.isArrayLiteralExpression(declaration.initializer))) {
        exported.add(`${file}\0${declaration.name.text}`);
      }
    }
  }
}
function gatherImports(tree, file) {
  for (const statement of tree.statements) {
    if (!ts.isImportDeclaration(statement) || !ts.isStringLiteral(statement.moduleSpecifier)) continue;
    const clause = statement.importClause, named = clause?.namedBindings;
    if (!clause || clause.isTypeOnly || !named || !ts.isNamedImports(named)) continue;
    const line = position(tree, statement)[0], specifier = statement.moduleSpecifier.text;
    const matched = (imports[file] || []).filter(row => row[0] === line && row[1] === specifier);
    for (const item of named.elements) {
      if (item.isTypeOnly) continue;
      const symbol = checker.getSymbolAtLocation(item.name);
      const name = (item.propertyName || item.name).text;
      if (!symbol || !matched.length) continue;
      const owner = matched.length === 1 ? matched[0][2] : null;
      bindings.set(symbol, {owner: owner && exported.has(`${owner}\0${name}`) ? owner : null, name});
    }
  }
}
function assigned(node) {
  if (ts.isBinaryExpression(node) && node.operatorToken.kind >= ts.SyntaxKind.FirstAssignment && node.operatorToken.kind <= ts.SyntaxKind.LastAssignment) return node.left;
  if ((ts.isPrefixUnaryExpression(node) || ts.isPostfixUnaryExpression(node)) && (node.operator === ts.SyntaxKind.PlusPlusToken || node.operator === ts.SyntaxKind.MinusMinusToken)) return node.operand;
  if (ts.isDeleteExpression(node)) return node.expression;
  return null;
}
function gatherNodes(tree, file, node) {
  if (isConst(node) && ts.isIdentifier(node.name) && node.initializer && ts.isIdentifier(node.initializer)) aliases.push(node);
  const target = assigned(node);
  if (target && ts.isIdentifier(target)) {
    const symbol = checker.getSymbolAtLocation(target);
    if (symbol) written.add(symbol);
  }
  if (target && ts.isPropertyAccessExpression(target) && !target.questionDotToken && ts.isIdentifier(target.expression)) writes.push([tree, file, target]);
  ts.forEachChild(node, child => gatherNodes(tree, file, child));
}
function resolveAlias(decl, seen = new Set()) {
  const symbol = checker.getSymbolAtLocation(decl.name);
  if (!symbol || written.has(symbol) || seen.has(symbol)) return null;
  if (bindings.has(symbol)) return bindings.get(symbol);
  seen.add(symbol);
  const source = checker.getSymbolAtLocation(decl.initializer);
  if (!source || written.has(source)) return null;
  if (bindings.has(source)) return bindings.get(source);
  const next = source.valueDeclaration;
  return next && isConst(next) && ts.isIdentifier(next.name) && next.initializer && ts.isIdentifier(next.initializer) ? resolveAlias(next, seen) : null;
}
for (const [file, tree] of trees) gatherExports(tree, names.get(file));
for (const [file, tree] of trees) gatherImports(tree, names.get(file));
for (const [file, tree] of trees) gatherNodes(tree, names.get(file), tree);
for (const declaration of aliases) {
  const resolved = resolveAlias(declaration);
  if (resolved) bindings.set(checker.getSymbolAtLocation(declaration.name), resolved);
}
const result = [];
for (const [tree, file, target] of writes) {
  const symbol = checker.getSymbolAtLocation(target.expression);
  const binding = !written.has(symbol) && bindings.get(symbol);
  if (binding) result.push([file, ...position(tree, target), binding.owner, binding.name]);
}
process.stdout.write(JSON.stringify(result));
