import type * as TypeScript from
  '../../../../../../../../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript';
const ts: typeof TypeScript =
  require('../../../../../../../../IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/node_modules/typescript/lib/typescript.js');
const fs = require('fs');
const source = ts.createSourceFile('test.ts', fs.readFileSync(process.argv[2],
  'utf8'), ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
if ((source as TypeScript.SourceFile & { parseDiagnostics:
  readonly TypeScript.Diagnostic[] }).parseDiagnostics.length)
    throw Error('TypeScript parse failed');
const tests: TypeScript.CallExpression[] = [];
function visit(node: TypeScript.Node): void {
  if (ts.isCallExpression(node) && node.expression.getText(source) ===
    'test' &&
      node.arguments[0]?.getText(source).includes(process.argv[3]))
        tests.push(node);
  ts.forEachChild(node, visit);
}
visit(source);
if (tests.length !== 1 || !ts.isArrowFunction(tests[0].arguments[1]) ||
  !ts.isBlock(tests[0].arguments[1].body))
    throw Error('Unsupported or ambiguous test selection');
const body = tests[0].arguments[1].body;
const printer = ts.createPrinter({ removeComments: true });
const canon = (node: TypeScript.Node) =>
  printer.printNode(ts.EmitHint.Unspecified, node, source);
const statement = (text: string) => {
  const file = ts.createSourceFile('pattern.ts', text, ts.ScriptTarget.Latest,
    true, ts.ScriptKind.TS);
  return printer.printNode(ts.EmitHint.Unspecified, file.statements[0], file);
};
const editorInit =
  statement(("page.getByRole('textbox', { name: 'Query edit" +
    "or' });"));
const editors = body.statements.flatMap(s => ts.isVariableStatement(s) &&
  (s.declarationList.flags & ts.NodeFlags.Const) ?
    s.declarationList.declarations.filter(d =>
  ts.isIdentifier(d.name) && d.initializer && `${canon(d.initializer)};` ===
    editorInit).map(d => (d.name as TypeScript.Identifier).text) : []);
if (editors.length !== 1) throw Error('Unsupported or ambiguous editor');
const editor = editors[0];
if (body.statements.some(s => ts.isIfStatement(s) ||
  ts.isSwitchStatement(s) || ts.isIterationStatement(s, false) ||
    ts.isTryStatement(s) || ts.isReturnStatement(s) ||
      ts.isThrowStatement(s))) throw Error('Unsupported test control flow');
const inputs: {i: number; value: string; name: string}[] = [], checks: {i:
  number; value: string}[] = [], dispatches: {i: number; name: string}[] = [];
function callOf(s: TypeScript.Statement) {
  return ts.isExpressionStatement(s) && ts.isAwaitExpression(s.expression) &&
    ts.isCallExpression(s.expression.expression) ? s.expression.expression :
      null; }
function literal(n: TypeScript.Node | undefined) { return n &&
  (ts.isStringLiteral(n) || ts.isNoSubstitutionTemplateLiteral(n)) ? n.text :
    null; }
body.statements.forEach((s, i) => {
  const call = callOf(s);
  if (!call) return;
  const name = call.expression.getText(source);
  if (name === 'page.keyboard.insertText' || name === 'replaceSql') {
    const value = literal(call.arguments[name === 'replaceSql' ? 1 : 0]);
    if (value === null || (name === 'replaceSql' &&
      call.arguments[0]?.getText(source) !==
        'page')) throw Error('Unsupported dynamic input');
    inputs.push({i, value, name});
  }
  if (name === `expect(${editor}).toHaveText`) {
    const value = literal(call.arguments[0]);
    if (value === null) throw Error('Unsupported dynamic editor check');
    checks.push({i, value});
  }
  if (canon(s) ===
    statement(("await page.getByRole('button', { name: 'Run C" +
      "md+Enter' }).click();")) ||
      name === 'runWithTerminalDiagnostics') dispatches.push({i, name});
});
let candidates = 0;
function count(node: TypeScript.Node): void {
  if (ts.isCallExpression(node)) {
    const name = node.expression.getText(source);
    if ((name.startsWith(`${editor}.`) && name !== `${editor}.click`) ||
        (name.startsWith('page.keyboard.') && name !==
          'page.keyboard.insertText'))
            throw Error('Unsupported editor operation');
    if (['page.keyboard.insertText', 'replaceSql',
      'runWithTerminalDiagnostics',
        `expect(${editor}).toHaveText`].includes(name) ||
        (name.endsWith('.click') &&
          name.includes('Run Cmd+Enter'))) candidates++;
  }
  ts.forEachChild(node, count);
}
count(body);
if (inputs.length !== 1 || dispatches.length !== 1 || candidates !==
  inputs.length + checks.length + dispatches.length || inputs[0].i >=
    dispatches[0].i)
      throw Error('Unsupported or ambiguous input, check, or dispatch flow');
if (inputs[0].name === 'page.keyboard.insertText' && !body.statements.slice(0,
  inputs[0].i).some(s => canon(s) ===
    statement(`await ${editor}.click();`)))
      throw Error('Unsupported keyboard input target');
if (inputs[0].name === 'replaceSql') {
  const imports = source.statements.filter(s => ts.isImportDeclaration(s) &&
    literal(s.moduleSpecifier) === './workbench-fixture' &&
    s.importClause?.namedBindings && !s.importClause.isTypeOnly &&
      ts.isNamedImports(s.importClause.namedBindings) &&
    s.importClause.namedBindings.elements.some(e => e.name.text ===
      'replaceSql' && !e.propertyName && !e.isTypeOnly));
  let shadows = 0;
  function findShadows(node: TypeScript.Node): void {
    if ((ts.isVariableDeclaration(node) || ts.isParameter(node) ||
      ts.isFunctionDeclaration(node)) && node.name?.getText(source) ===
        'replaceSql') shadows++;
    ts.forEachChild(node, findShadows);
  }
  findShadows(body);
  if (imports.length !== 1 ||
    shadows) throw Error('Unsupported SQL input helper binding');
}
if (dispatches[0].name === 'runWithTerminalDiagnostics') {
  if (callOf(body.statements[dispatches[0].i])!.arguments[0]?.getText(source)
    !== 'page') throw Error('Unsupported dispatch target');
  const helpers = source.statements.filter((n):
    n is TypeScript.FunctionDeclaration => ts.isFunctionDeclaration(n) &&
      n.name?.text === 'runWithTerminalDiagnostics');
  const click =
    statement(("const [reply] = await Promise.all([terminal, " +
      "page.getByRole('button', { name: 'Run Cmd+Ent" +
      "er' }).click()]);"));
  if (helpers.length !== 1 || !helpers[0].body?.statements.some(n =>
    canon(n) === click)) throw Error('Unsupported query dispatch helper');
}
process.stdout.write(JSON.stringify({input: inputs[0], checks, dispatch:
  dispatches[0].i}));
