import fs from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';

const require = createRequire(new URL('../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/package.json', import.meta.url));
const ts: typeof import('../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript') =
  require('typescript');

type Node = Parameters<typeof ts.isIdentifier>[0];
type SourceFile = ReturnType<typeof ts.createSourceFile>;
type Symbol = Parameters<typeof checker.getAliasedSymbol>[0];
type VariableDeclaration = ReturnType<typeof ts.factory.createVariableDeclaration>;
type Identifier = ReturnType<typeof ts.factory.createIdentifier>;
type PropertyAccess = ReturnType<typeof ts.factory.createPropertyAccessExpression>;
type Alias = VariableDeclaration & {name: Identifier; initializer: Identifier};
type Binding = {owner: string | null; name: string};
type ImportSite = [line: number, specifier: string, owner: string | null];

const {sources = {}, imports = {}}: {sources?: Record<string, string>; imports?: Record<string, ImportSite[]>} =
  JSON.parse(fs.readFileSync(0, 'utf8'));
const root = '/__anechoic_virtual__/';
const absolute = (p: string) => path.posix.normalize(root + p);
const names = new Map(Object.keys(sources).map(p => [absolute(p), p]));
function scriptKind(name: string) {
  if (name.endsWith('.tsx')) return ts.ScriptKind.TSX;
  if (name.endsWith('.jsx')) return ts.ScriptKind.JSX;
  return /\.[cm]?js$/.test(name) ? ts.ScriptKind.JS : ts.ScriptKind.TS;
}
const trees = new Map([...names].map(([file, name]) => [file, ts.createSourceFile(file, sources[name], ts.ScriptTarget.Latest, true, scriptKind(name))]));
const host: NonNullable<Parameters<typeof ts.createProgram>[2]> = {
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
const exported = new Set<string>(), bindings = new Map<Symbol, Binding>();
const aliases: Alias[] = [], written = new Set<Symbol>(), writes: [SourceFile, string, PropertyAccess][] = [];
function position(tree: SourceFile, node: Node): [number, number] {
  const p = tree.getLineAndCharacterOfPosition(node.getStart(tree));
  return [p.line + 1, p.character];
}
function isConst(node: Node): node is VariableDeclaration {
  return ts.isVariableDeclaration(node) && ts.isVariableDeclarationList(node.parent) &&
    !!(node.parent.flags & ts.NodeFlags.Const);
}
function gatherExports(tree: SourceFile, file: string) {
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
function gatherImports(tree: SourceFile, file: string) {
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
function assigned(node: Node) {
  if (ts.isBinaryExpression(node) && node.operatorToken.kind >= ts.SyntaxKind.FirstAssignment && node.operatorToken.kind <= ts.SyntaxKind.LastAssignment) return node.left;
  if ((ts.isPrefixUnaryExpression(node) || ts.isPostfixUnaryExpression(node)) && (node.operator === ts.SyntaxKind.PlusPlusToken || node.operator === ts.SyntaxKind.MinusMinusToken)) return node.operand;
  if (ts.isDeleteExpression(node)) return node.expression;
  return null;
}
function isAlias(node: Node): node is Alias {
  return isConst(node) && ts.isIdentifier(node.name) && node.initializer !== undefined && ts.isIdentifier(node.initializer);
}
function gatherNodes(tree: SourceFile, file: string, node: Node) {
  if (isAlias(node)) aliases.push(node);
  const target = assigned(node);
  if (target && ts.isIdentifier(target)) {
    const symbol = checker.getSymbolAtLocation(target);
    if (symbol) written.add(symbol);
  }
  if (target && ts.isPropertyAccessExpression(target) && !target.questionDotToken && ts.isIdentifier(target.expression)) writes.push([tree, file, target]);
  ts.forEachChild(node, child => gatherNodes(tree, file, child));
}
function resolveAlias(decl: Alias, seen = new Set<Symbol>()): Binding | null | undefined {
  const symbol = checker.getSymbolAtLocation(decl.name);
  if (!symbol || written.has(symbol) || seen.has(symbol)) return null;
  if (bindings.has(symbol)) return bindings.get(symbol);
  seen.add(symbol);
  const source = checker.getSymbolAtLocation(decl.initializer);
  if (!source || written.has(source)) return null;
  if (bindings.has(source)) return bindings.get(source);
  const next = source.valueDeclaration;
  return next && isAlias(next) ? resolveAlias(next, seen) : null;
}
for (const [file, tree] of trees) gatherExports(tree, names.get(file)!);
for (const [file, tree] of trees) gatherImports(tree, names.get(file)!);
for (const [file, tree] of trees) gatherNodes(tree, names.get(file)!, tree);
for (const declaration of aliases) {
  const resolved = resolveAlias(declaration);
  const symbol = checker.getSymbolAtLocation(declaration.name);
  if (resolved && symbol) bindings.set(symbol, resolved);
}
const result: [string, number, number, string | null, string][] = [];
for (const [tree, file, target] of writes) {
  const symbol = checker.getSymbolAtLocation(target.expression);
  const binding = symbol && !written.has(symbol) && bindings.get(symbol);
  if (binding) result.push([file, ...position(tree, target), binding.owner, binding.name]);
}
process.stdout.write(JSON.stringify(result));
