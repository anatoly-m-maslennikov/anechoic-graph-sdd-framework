import type * as TypeScript from
  '../../../../../../../../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript';
const fs = require('fs');
const compilerOverride = process.env.TYPESCRIPT_PATH;
const ts: typeof TypeScript = compilerOverride
  ? require(compilerOverride)
  :
    require('../../../../../../../../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript/lib/typescript.js');
const source = ts.createSourceFile('input.mjs',
  fs.readFileSync(process.argv[2], 'utf8'), ts.ScriptTarget.Latest, true,
    ts.ScriptKind.JS);
if ((source as TypeScript.SourceFile & { parseDiagnostics:
  readonly TypeScript.Diagnostic[] }).parseDiagnostics.length)
    throw Error('source parse failed');
const scan = source.statements.filter((n):
  n is TypeScript.FunctionDeclaration => ts.isFunctionDeclaration(n) &&
    n.name?.text === 'scan');
if (scan.length !== 1 || !scan[0].body) throw Error('unsupported scan');
const stmts = scan[0].body.statements;
const shadow = stmts.filter((n): n is TypeScript.FunctionDeclaration =>
  ts.isFunctionDeclaration(n) && n.name?.text === 'findShadow');
if (shadow.length !== 1 ||
  !shadow[0].body) throw Error('unsupported findShadow');
const tests =
  ("ts.isVariableDeclaration(node) || ts.isParame" +
    "ter(node) || ts.isFunctionDeclaration(node) |" +
    "| ts.isClassDeclaration(node) || ts.isImportC" +
    "lause(node) || ts.isImportSpecifier(node) || " +
    "ts.isNamespaceImport(node)");
function template(guard: string): TypeScript.Statement {
  return ts.createSourceFile('template.js',
    ("function findShadow(node) { if ((" +
      (tests) +
      ") && " +
      (guard) +
      "ts.isIdentifier(node.name) && ['process', 'co" +
      "nsole'].includes(node.name.text)) shadow.add(" +
      "node.name.text); ts.forEachChild(node, findSh" +
      "adow); }"), ts.ScriptTarget.Latest, true,
    ts.ScriptKind.JS).statements[0];
}
function shape(n: TypeScript.Node): unknown[] {
  const children: unknown[] = []; n.forEachChild(c => {
    children.push(shape(c)); });
  return [n.kind, ts.isIdentifier(n) || ts.isStringLiteral(n) ? n.text : '',
    children];
}
const actual = JSON.stringify(shape(shadow[0]));
const fixed = actual === JSON.stringify(shape(template('node.name && ')));
const before = actual === JSON.stringify(shape(template('')));
if (!fixed && !before) throw Error('unsupported findShadow AST');
const invocation = stmts.some(n => ts.isExpressionStatement(n) &&
  ts.isCallExpression(n.expression) &&
    n.expression.expression.getText(source) === 'findShadow' &&
      n.expression.arguments.length === 1 &&
        n.expression.arguments[0].getText(source) === 'tree');
const input = ts.createSourceFile('sample.ts',
  "import * as ns from 'module';", ts.ScriptTarget.Latest, true,
    ts.ScriptKind.TS);
const declaration = input.statements[0];
if (!ts.isImportDeclaration(declaration) ||
  !declaration.importClause) throw Error('unsupported input');
const clause = declaration.importClause;
if (!invocation || clause.name || (!clause.namedBindings ||
  !ts.isNamespaceImport(clause.namedBindings)))
    throw Error('unsupported call or input');
console.log(fixed ? 'guarded' : 'unguarded');
