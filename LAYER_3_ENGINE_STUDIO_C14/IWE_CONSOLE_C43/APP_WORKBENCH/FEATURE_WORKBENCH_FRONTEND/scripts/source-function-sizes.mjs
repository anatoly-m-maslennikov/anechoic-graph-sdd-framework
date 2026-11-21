import ts from 'typescript';
import { parse } from 'svelte/compiler';
import { readFileSync } from 'node:fs';

function record(lineStarts, start, end, name, result) {
  const line = ts.computeLineAndCharacterOfPosition(lineStarts, start).line + 1;
  const last = ts.computeLineAndCharacterOfPosition(lineStarts, end - 1).line + 1;
  result.push([line, name || '<anonymous>', last - line + 1, start]);
}

function javascript(source, offset, lineStarts, path, result) {
  const tree = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);
  if (tree.parseDiagnostics.length) {
    throw new Error(`${path}: ${ts.flattenDiagnosticMessageText(tree.parseDiagnostics[0].messageText, ' ')}`);
  }
  function visit(node) {
    if (ts.isFunctionLike(node) && node.body) {
      const name = ts.isConstructorDeclaration(node) ? 'constructor' :
        node.name?.getText(tree) || node.parent?.name?.getText(tree) || '<anonymous>';
      record(lineStarts, offset + node.getStart(tree), offset + node.end, name, result);
    }
    ts.forEachChild(node, visit);
  }
  visit(tree);
}

function svelte(source, lineStarts, path, result) {
  let tree;
  try { tree = parse(source, { modern: true }); }
  catch (error) { throw new Error(`${path}: ${error.message}`); }
  for (const script of [tree.instance, tree.module]) {
    if (script) javascript(source.slice(script.content.start, script.content.end), script.content.start, lineStarts, `${path}.ts`, result);
  }
  function visit(node, parent) {
    if (!node || typeof node !== 'object') return;
    if (['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'].includes(node.type)) {
      record(lineStarts, node.start, node.end, node.id?.name || parent?.key?.name || parent?.id?.name, result);
    }
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) value.forEach(child => visit(child, node));
      else if (value && typeof value === 'object') visit(value, node);
    }
  }
  visit(tree.fragment);
}

const input = JSON.parse(readFileSync(0, 'utf8'));
const output = input.map(({ path, source }) => {
  const result = [];
  const lineStarts = ts.computeLineStarts(source);
  if (path.endsWith('.svelte')) svelte(source, lineStarts, path, result);
  else javascript(source, 0, lineStarts, path, result);
  return result.sort((a, b) => a[3] - b[3]).map(([line, name, size]) => [line, name, size]);
});
process.stdout.write(JSON.stringify(output));
