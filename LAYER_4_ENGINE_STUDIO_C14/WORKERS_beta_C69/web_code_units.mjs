import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(new URL('../IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/package.json', import.meta.url));
const ts = require('typescript');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const sources = input.sources || {};
const imports = input.imports || {};
const root = '/__anechoic_virtual__/';
const absolute = p => path.posix.normalize(root + p);
const names = new Map(Object.keys(sources).map(p => [absolute(p), p]));
function scriptKind(name) {
  if (name.endsWith('.tsx')) return ts.ScriptKind.TSX;
  if (name.endsWith('.jsx')) return ts.ScriptKind.JSX;
  return /\.[cm]?js$/.test(name) ? ts.ScriptKind.JS : ts.ScriptKind.TS;
}
const trees = new Map([...names].map(([file, name]) => [file, ts.createSourceFile(file, sources[name], ts.ScriptTarget.Latest, true, scriptKind(name))]));
const options = {allowJs: true, noLib: true, module: ts.ModuleKind.ESNext,
  moduleDetection: ts.ModuleDetectionKind.Force, target: ts.ScriptTarget.Latest};
const host = {
  getSourceFile: file => trees.get(path.posix.normalize(file)),
  getDefaultLibFileName: () => '', writeFile() {},
  getCurrentDirectory: () => root, getDirectories: () => [],
  fileExists: file => trees.has(path.posix.normalize(file)),
  readFile: file => trees.get(path.posix.normalize(file))?.text,
  getCanonicalFileName: file => file, useCaseSensitiveFileNames: () => true,
  getNewLine: () => '\n',
  resolveModuleNames(specifiers, containingFile) {
    const source = names.get(path.posix.normalize(containingFile));
    return specifiers.map(spec => {
      const targets = new Set((imports[source] || []).filter(row => row[1] === spec).map(row => row[2]).filter(target => names.has(absolute(target))));
      if (targets.size !== 1) return undefined;
      const target = absolute([...targets][0]);
      const extension = /\.tsx$/.test(target) ? ts.Extension.Tsx : /\.[cm]?jsx?$/.test(target) ? ts.Extension.Js : ts.Extension.Ts;
      return {resolvedFileName: target, extension, isExternalLibraryImport: false};
    });
  }
};
const program = ts.createProgram([...trees.keys()], options, host);
const checker = program.getTypeChecker();
const units = [], calls = [], nodes = new Map(), symbolUnits = new Map(), callableUnits = new Set(), written = new Set();
function pos(tree, node) {
  const p = tree.getLineAndCharacterOfPosition(node.getStart(tree));
  return [p.line + 1, p.character];
}
function nameOf(node) {
  if (node.name && (ts.isIdentifier(node.name) || ts.isStringLiteral(node.name) || ts.isNumericLiteral(node.name))) return node.name.text;
  if ((ts.isArrowFunction(node) || ts.isFunctionExpression(node) || ts.isClassExpression(node)) && ts.isVariableDeclaration(node.parent) && ts.isIdentifier(node.parent.name)) return node.parent.name.text;
  return null;
}
function symbolOf(node) {
  const loc = node.name || (ts.isVariableDeclaration(node.parent) ? node.parent.name : undefined);
  return loc && checker.getSymbolAtLocation(loc);
}
function record(tree, file, node, parents) {
  let kind = null;
  if (ts.isClassDeclaration(node) || ts.isClassExpression(node)) kind = 'class';
  else if (ts.isMethodDeclaration(node) && node.body) kind = 'method';
  else if ((ts.isFunctionDeclaration(node) && node.body) || ts.isFunctionExpression(node) || ts.isArrowFunction(node)) kind = 'function';
  const name = kind && nameOf(node);
  let next = parents;
  if (name) {
    const [line, column] = pos(tree, node);
    const key = `code_unit:${file}:${line}:${column}`;
    units.push([key, `module:${file}`, kind, [...parents.map(p => p.name), name].join('.'), line, column]);
    nodes.set(node, key);
    if (kind !== 'class') callableUnits.add(key);
    const sym = symbolOf(node);
    if (sym) {
      const list = symbolUnits.get(sym) || [];
      list.push(key); symbolUnits.set(sym, list);
    }
    next = [...parents, {name, key}];
  }
  ts.forEachChild(node, child => record(tree, file, child, next));
}
for (const [file, tree] of trees) record(tree, names.get(file), tree, []);

function markWrites(node) {
  let target;
  if (ts.isBinaryExpression(node) && node.operatorToken.kind >= ts.SyntaxKind.FirstAssignment && node.operatorToken.kind <= ts.SyntaxKind.LastAssignment) target = node.left;
  else if ((ts.isPrefixUnaryExpression(node) || ts.isPostfixUnaryExpression(node)) && (node.operator === ts.SyntaxKind.PlusPlusToken || node.operator === ts.SyntaxKind.MinusMinusToken)) target = node.operand;
  if (target) { const s = checker.getSymbolAtLocation(target); if (s) written.add(s); }
  ts.forEachChild(node, markWrites);
}
for (const tree of trees.values()) markWrites(tree);
function binding(expr) {
  let symbol = checker.getSymbolAtLocation(expr);
  if (!symbol || written.has(symbol)) return null;
  if (symbol.flags & ts.SymbolFlags.Alias) {
    if (checker.getTypeOnlyAliasDeclaration(symbol)) return null;
    symbol = checker.getAliasedSymbol(symbol);
  }
  return symbol && !written.has(symbol) ? symbol : null;
}
function resolvedSymbol(expr) {
  if (expr.questionDotToken) return null;
  if (ts.isIdentifier(expr)) return binding(expr);
  if (!ts.isPropertyAccessExpression(expr)) return null;
  const target = binding(expr.name);
  const decl = target?.valueDeclaration;
  if (!decl || !ts.isMethodDeclaration(decl)) {
    const receiver = binding(expr.expression);
    return receiver?.flags & ts.SymbolFlags.ValueModule ? target : null;
  }
  const receiver = binding(expr.expression);
  const directClass = receiver?.valueDeclaration === decl.parent;
  const isStatic = ts.getModifiers(decl)?.some(item => item.kind === ts.SyntaxKind.StaticKeyword);
  return directClass && isStatic && !ts.getDecorators(decl)?.length && !ts.getDecorators(decl.parent)?.length
    ? target : null;
}
function scan(tree, node, owner) {
  owner = nodes.get(node) || owner;
  if (ts.isCallExpression(node) && !node.questionDotToken) {
    const symbol = resolvedSymbol(node.expression);
    const targets = symbol && symbolUnits.get(symbol);
    if (callableUnits.has(owner) && targets?.length === 1 && callableUnits.has(targets[0])) {
      const [line, column] = pos(tree, node);
      calls.push([owner, targets[0], line, column]);
    }
  }
  if (ts.isFunctionLike(node)) {
    if (node.body) scan(tree, node.body, nodes.get(node));
  } else {
    ts.forEachChild(node, child => scan(tree, child, owner));
  }
}
for (const tree of trees.values()) scan(tree, tree, null);
process.stdout.write(JSON.stringify([units, calls]));
