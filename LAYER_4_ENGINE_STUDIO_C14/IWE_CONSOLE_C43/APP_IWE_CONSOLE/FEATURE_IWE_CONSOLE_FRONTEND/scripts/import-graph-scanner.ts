import fs from 'node:fs';
import { createRequire } from 'node:module';
import ts from 'typescript';
const { parse } = createRequire(import.meta.url)(
  'svelte/compiler') as typeof import('svelte/compiler');

type SourceFile = ts.SourceFile & {
  parseDiagnostics: readonly ts.Diagnostic[] };
type NamedUse = [string, number, number];
type Forwarded = [string, string, number, number];
type Site = { module: string; line: number; column: number;
  type_only: boolean; level: number; anchor: string | null };
type ScanResult = { status: 'parsed'; sites: Site[]; forwarded: Forwarded[
  ]; named_uses: NamedUse[] } | { status: 'parse_error'; error: string };

function findRequireAnchor(tree: ts.SourceFile): string | null {
let requireAnchor = null;
const hasCreateRequire = tree.statements.some(s => ts.isImportDeclaration(s) &&
  ts.isStringLiteral(s.moduleSpecifier) &&
    s.moduleSpecifier.text === 'node:module' &&
  s.importClause?.namedBindings && ts.isNamedImports(
    s.importClause.namedBindings) &&
  s.importClause.namedBindings.elements.some(e =>
    e.name.text === 'createRequire' && !e.propertyName));
for (const statement of tree.statements) if (
  ts.isVariableStatement(statement)) {
  for (const declaration of statement.declarationList.declarations) {
    if (!ts.isIdentifier(declaration.name) ||
      declaration.name.text !== 'require') continue;
    requireAnchor = '<unknown-anchor>';
    const init = declaration.initializer;
    if (!hasCreateRequire || !(
      statement.declarationList.flags & ts.NodeFlags.Const) ||
      !init || !ts.isCallExpression(init) ||
      !ts.isIdentifier(init.expression) ||
        init.expression.text !== 'createRequire' ||
        init.arguments.length !== 1) continue;
    const url = init.arguments[0];
    if (!ts.isNewExpression(url) || !ts.isIdentifier(
      url.expression) || url.expression.text !== 'URL' ||
      url.arguments?.length !== 2 ||
        !ts.isStringLiteral(url.arguments[0])) continue;
    if (url.arguments[1].getText(
      tree) === 'import.meta.url') requireAnchor = url.arguments[0].text;
  }
}
  return requireAnchor;
}

function position(tree: ts.SourceFile, node: ts.Node,
  text: string, offset: number): [number, number] {
  const absolute = offset + node.getStart(tree);
  const prefix = text.slice(0, absolute);
  return [prefix.split('\n').length,
    absolute - (prefix.lastIndexOf('\n') + 1)];
}

function symbolMetadata(tree: ts.SourceFile, text: string, offset: number) {
  const forwarded: Forwarded[] = [], namedUses: NamedUse[] = [];
  const bindings = new Map<string, { imported:
    string; line: number; column: number } | null>();
  for (const node of tree.statements) {
    if (!ts.isImportDeclaration(node) || !node.importClause) continue;
    const [line, column] = position(tree, node, text, offset);
    const clause = node.importClause;
    const add = (local: string, imported: string) => {
      namedUses.push([imported, line, column]);
      if (bindings.has(local)) bindings.set(local, null);
      else bindings.set(local, { imported, line, column });
    };
    if (clause.name) add(clause.name.text, 'default');
    if (clause.namedBindings && ts.isNamedImports(clause.namedBindings)) {
      for (const item of clause.namedBindings.elements) add(
        item.name.text, (item.propertyName || item.name).text);
    }
  }
  for (const node of tree.statements) {
    if (!ts.isExportDeclaration(node) || !node.exportClause ||
      !ts.isNamedExports(node.exportClause)) continue;
    const [line, column] = position(tree, node, text, offset);
    for (const item of node.exportClause.elements) {
      const imported = (item.propertyName || item.name).text;
      if (node.moduleSpecifier) {
        namedUses.push([imported, line, column]);
        forwarded.push([item.name.text, imported, line, column]);
      } else {
        const origin = bindings.get(imported);
        if (origin) forwarded.push([item.name.text,
          origin.imported, origin.line, origin.column]);
      }
    }
  }
  return { forwarded, namedUses };
}

function typeOnlyImport(clause: ts.ImportClause | undefined): boolean {
  if (!clause) return false;
  if (clause.isTypeOnly) return true;
  const bindings = clause.namedBindings;
  return !clause.name && !!bindings && ts.isNamedImports(bindings) &&
    bindings.elements.length > 0 &&
    bindings.elements.every(element => element.isTypeOnly);
}

function typeOnlyExport(node: ts.ExportDeclaration): boolean {
  const clause = node.exportClause;
  return node.isTypeOnly || (!!clause && ts.isNamedExports(clause) &&
    clause.elements.length > 0 &&
    clause.elements.every(element => element.isTypeOnly));
}

function scopedAnchor(
  node: ts.Node, tree: ts.SourceFile, anchor: string | null,
): string | null {
  for (let parent = node.parent; parent && parent !== tree;
    parent = parent.parent) {
    if (ts.isFunctionLike(parent)) return '<unknown-anchor>';
  }
  return anchor;
}

function collectSites(
  tree: ts.SourceFile, text: string, offset: number,
): Site[] {
  const sites: Site[] = [];
  const requireAnchor = findRequireAnchor(tree);
  function visit(node: ts.Node): void {
    let arg: ts.Node | undefined, typeOnly = false, viteLoad = false;
    let anchor: string | null = null;
    if (ts.isImportDeclaration(node)) {
      arg = node.moduleSpecifier;
      typeOnly = typeOnlyImport(node.importClause);
    } else if (ts.isExportDeclaration(node) && node.moduleSpecifier) {
      arg = node.moduleSpecifier;
      typeOnly = typeOnlyExport(node);
    } else if (ts.isImportEqualsDeclaration(node) &&
      ts.isExternalModuleReference(node.moduleReference)) {
      arg = node.moduleReference.expression;
      typeOnly = node.isTypeOnly;
    } else if (ts.isCallExpression(node)) {
      const expression = node.expression;
      const required = ts.isIdentifier(expression) &&
        expression.text === 'require';
      if (required || expression.kind === ts.SyntaxKind.ImportKeyword) {
        arg = node.arguments[0] || node;
      }
      if (required) anchor = scopedAnchor(node, tree, requireAnchor);
      if (ts.isPropertyAccessExpression(expression) &&
        expression.name.text === 'ssrLoadModule') {
        arg = node.arguments[0] || node;
        viteLoad = true;
      }
    }
    if (arg) {
      const module = ts.isStringLiteral(arg) ||
        ts.isNoSubstitutionTemplateLiteral(arg) ? arg.text : '<dynamic>';
      const [line, column] = position(tree, node, text, offset);
      sites.push({ module, line, column, type_only: !!typeOnly,
        level: viteLoad ? 1 : 0, anchor });
    }
    ts.forEachChild(node, visit);
  }
  visit(tree);
  return sites;
}

const input = JSON.parse(fs.readFileSync(0, 'utf8')) as {
  path: string; text: string; language: string }[];
const results: Record<string, ScanResult> = {};
for (const { path, text, language } of input) {
  const sites: Site[] = [], forwarded:
    Forwarded[] = [], namedUses: NamedUse[] = [];
  function scan(content: string, offset: number): void {
    const kind = path.endsWith('.tsx') ? ts.ScriptKind.TSX :
      path.endsWith('.jsx') ? ts.ScriptKind.JSX :
      language === 'javascript' ? ts.ScriptKind.JS : ts.ScriptKind.TS;
    const tree = ts.createSourceFile(
      path, content, ts.ScriptTarget.Latest, true, kind,
    ) as SourceFile;
    if (tree.parseDiagnostics.length) throw Error(
      ts.flattenDiagnosticMessageText(tree.parseDiagnostics[0].messageText,
        ' '));
    const symbols = symbolMetadata(tree, text, offset);
    forwarded.push(...symbols.forwarded);
    namedUses.push(...symbols.namedUses);
    for (const site of collectSites(tree, text, offset)) sites.push(site);
  }
  try {
    if (language === 'svelte') {
      const ast = parse(text, { filename: path });
      for (const block of [ast.module, ast.instance]) if (block) {
        const content = block.content as typeof block.content & {
          start: number; end: number };
        const start = content.start;
        scan(text.slice(start, content.end), start);
      }
    } else scan(text, 0);
    results[path] = { status: 'parsed', sites,
      forwarded, named_uses: namedUses };
  } catch (error) { results[path] = { status:
    'parse_error', error: String(error) }; }
}
process.stdout.write(JSON.stringify(results));
