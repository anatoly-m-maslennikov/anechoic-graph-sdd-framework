import fs from 'node:fs';
import { createRequire } from 'node:module';
import ts from 'typescript';
const { parse } = createRequire(import.meta.url)('svelte/compiler');

function findRequireAnchor(tree) {
let requireAnchor = null;
const hasCreateRequire = tree.statements.some(s => ts.isImportDeclaration(s) && s.moduleSpecifier.text === 'node:module' &&
  s.importClause?.namedBindings && ts.isNamedImports(s.importClause.namedBindings) &&
  s.importClause.namedBindings.elements.some(e => e.name.text === 'createRequire' && !e.propertyName));
for (const statement of tree.statements) if (ts.isVariableStatement(statement)) {
  for (const declaration of statement.declarationList.declarations) {
    if (!ts.isIdentifier(declaration.name) || declaration.name.text !== 'require') continue;
    requireAnchor = '<unknown-anchor>';
    const init = declaration.initializer;
    if (!hasCreateRequire || !(statement.declarationList.flags & ts.NodeFlags.Const) || !init || !ts.isCallExpression(init) || !ts.isIdentifier(init.expression) || init.expression.text !== 'createRequire' || init.arguments.length !== 1) continue;
    const url = init.arguments[0];
    if (!ts.isNewExpression(url) || !ts.isIdentifier(url.expression) || url.expression.text !== 'URL' || url.arguments?.length !== 2 || !ts.isStringLiteral(url.arguments[0])) continue;
    if (url.arguments[1].getText(tree) === 'import.meta.url') requireAnchor = url.arguments[0].text;
  }
}
  return requireAnchor;
}

function position(tree, node, text, offset) {
  const absolute = offset + node.getStart(tree);
  const prefix = text.slice(0, absolute);
  return [prefix.split('\n').length, absolute - (prefix.lastIndexOf('\n') + 1)];
}

function symbolMetadata(tree, text, offset) {
  const forwarded = [], namedUses = [], bindings = new Map();
  for (const node of tree.statements) {
    if (!ts.isImportDeclaration(node) || !node.importClause) continue;
    const [line, column] = position(tree, node, text, offset);
    const clause = node.importClause;
    const add = (local, imported) => {
      namedUses.push([imported, line, column]);
      if (bindings.has(local)) bindings.set(local, null);
      else bindings.set(local, { imported, line, column });
    };
    if (clause.name) add(clause.name.text, 'default');
    if (clause.namedBindings && ts.isNamedImports(clause.namedBindings)) {
      for (const item of clause.namedBindings.elements) add(item.name.text, (item.propertyName || item.name).text);
    }
  }
  for (const node of tree.statements) {
    if (!ts.isExportDeclaration(node) || !node.exportClause || !ts.isNamedExports(node.exportClause)) continue;
    const [line, column] = position(tree, node, text, offset);
    for (const item of node.exportClause.elements) {
      const imported = (item.propertyName || item.name).text;
      if (node.moduleSpecifier) {
        namedUses.push([imported, line, column]);
        forwarded.push([item.name.text, imported, line, column]);
      } else {
        const origin = bindings.get(imported);
        if (origin) forwarded.push([item.name.text, origin.imported, origin.line, origin.column]);
      }
    }
  }
  return { forwarded, namedUses };
}

const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const results = {};
for (const { path, text, language } of input) {
  const sites = [], forwarded = [], namedUses = [];
  function scan(content, offset) {
    const kind = path.endsWith('.tsx') ? ts.ScriptKind.TSX : path.endsWith('.jsx') ? ts.ScriptKind.JSX : language === 'javascript' ? ts.ScriptKind.JS : ts.ScriptKind.TS;
    const tree = ts.createSourceFile(path, content, ts.ScriptTarget.Latest, true, kind);
    if (tree.parseDiagnostics.length) throw Error(ts.flattenDiagnosticMessageText(tree.parseDiagnostics[0].messageText, ' '));
    const requireAnchor = findRequireAnchor(tree);
    const symbols = symbolMetadata(tree, text, offset);
    forwarded.push(...symbols.forwarded); namedUses.push(...symbols.namedUses);
    function visit(node) {
      let arg, typeOnly = false, viteLoad = false, anchor = null;
      if (ts.isImportDeclaration(node)) {
        arg = node.moduleSpecifier;
        const clause = node.importClause;
        typeOnly = !!clause && (clause.isTypeOnly || (!clause.name && clause.namedBindings && ts.isNamedImports(clause.namedBindings) && clause.namedBindings.elements.length > 0 && clause.namedBindings.elements.every(e => e.isTypeOnly)));
      } else if (ts.isExportDeclaration(node) && node.moduleSpecifier) {
        arg = node.moduleSpecifier;
        typeOnly = node.isTypeOnly || (!!node.exportClause && ts.isNamedExports(node.exportClause) && node.exportClause.elements.length > 0 && node.exportClause.elements.every(e => e.isTypeOnly));
      } else if (ts.isImportEqualsDeclaration(node) && ts.isExternalModuleReference(node.moduleReference)) {
        arg = node.moduleReference.expression; typeOnly = node.isTypeOnly;
      } else if (ts.isCallExpression(node) && (node.expression.kind === ts.SyntaxKind.ImportKeyword || (ts.isIdentifier(node.expression) && node.expression.text === 'require'))) {
        arg = node.arguments[0] || node;
        if (ts.isIdentifier(node.expression) && node.expression.text === 'require') {
          anchor = requireAnchor;
          for (let parent = node.parent; parent && parent !== tree; parent = parent.parent) if (ts.isFunctionLike(parent)) anchor = '<unknown-anchor>';
        }
      }
      if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression) && node.expression.name.text === 'ssrLoadModule') {
        arg = node.arguments[0] || node; viteLoad = true;
      }
      if (arg) {
        const literal = ts.isStringLiteral(arg) || ts.isNoSubstitutionTemplateLiteral(arg);
        const [line, column] = position(tree, node, text, offset);
        sites.push({ module: literal ? arg.text : '<dynamic>', line, column, type_only: !!typeOnly, level: viteLoad ? 1 : 0, anchor });
      }
      ts.forEachChild(node, visit);
    }
    visit(tree);
  }
  try {
    if (language === 'svelte') {
      const ast = parse(text, { filename: path });
      for (const block of [ast.module, ast.instance]) if (block) {
        const start = block.content.start;
        scan(text.slice(start, block.content.end), start);
      }
    } else scan(text, 0);
    results[path] = { status: 'parsed', sites, forwarded, named_uses: namedUses };
  } catch (error) { results[path] = { status: 'parse_error', error: String(error) }; }
}
process.stdout.write(JSON.stringify(results));
