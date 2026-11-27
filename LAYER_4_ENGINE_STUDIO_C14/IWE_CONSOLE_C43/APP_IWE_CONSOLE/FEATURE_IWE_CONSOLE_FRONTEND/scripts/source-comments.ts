import ts from 'typescript';
import { Input } from 'postcss';
// @ts-expect-error PostCSS does not publish types for its tokenizer.
import tokenizeCss from 'postcss/lib/tokenize';
import { parse } from 'svelte/compiler';

import { readFileSync } from 'node:fs';

type Range = [number, number, 'js' | 'css' | 'manual' | 'markup'];
type CssToken = [string, string, number, number];
type SourceFile = ts.SourceFile & { parseDiagnostics: readonly ts.Diagnostic[] };

function removable(text: string): boolean {
  if (/^\/\*!/.test(text)) return false;
  if (/^\/\*\*/.test(text) && /@[a-z][\w-]*/i.test(text)) return false;
  const body = text.replace(/^(?:\/\/|\/\*+|<!--)\s*/, '');
  if (/^editorconfig-checker-disable-line\b/.test(body)) {
    return false;
  }
  return !/^(?:@ts-(?:check|nocheck|ignore|expect-error)\b|(?:eslint|prettier|biome|istanbul|c8|v8|webpack|vite|rollup|svelte|stylelint|noinspection)(?:[-:\s]|$)|[#@]\s*(?:sourceMappingURL|sourceURL|__PURE__|__NO_SIDE_EFFECTS__)\b|\[if\b|<!\[endif\]|#include\b)/i.test(body);
}

function js(source: string, offset: number, result: Range[], filename = 'file.ts') {
  const tree = ts.createSourceFile(filename, source, ts.ScriptTarget.Latest, true) as SourceFile;
  if (tree.parseDiagnostics.length) throw new Error(`${filename}: ${ts.flattenDiagnosticMessageText(tree.parseDiagnostics[0].messageText, ' ')}`);
  const tokens: [number, number][] = [];
  function visit(node: ts.Node) {
    if (ts.isJSDoc(node)) return;
    const children = node.getChildren(tree);
    if (!children.length) {
      if (node.kind !== ts.SyntaxKind.EndOfFileToken) tokens.push([node.getStart(tree), node.end]);
    } else for (const child of children) visit(child);
  }
  visit(tree);
  tokens.sort((a, b) => a[0] - b[0] || b[1] - a[1]);
  let end = 0;
  for (const [start, finish] of [...tokens, [source.length, source.length]]) {
    if (start > end) {
      const gap = source.slice(end, start);
      const comments = /\/\*[\s\S]*?\*\/|\/\/[^\r\n\u2028\u2029]*/g;
      for (const match of gap.matchAll(comments)) {
        if (removable(match[0])) result.push([offset + end + match.index, offset + end + match.index + match[0].length, 'js']);
      }
    }
    end = Math.max(end, finish);
  }
}

function cssTokens(source: string): CssToken[] {
  const tokens = tokenizeCss(new Input(source)) as { endOfFile(): boolean; nextToken(): CssToken };
  const result: CssToken[] = [];
  while (!tokens.endOfFile()) result.push(tokens.nextToken() as CssToken);
  return result;
}

function css(source: string, offset: number, result: Range[]) {
  const tokens = cssTokens(source);
  const signature = (items: CssToken[]) => JSON.stringify(items.filter(([kind]) => kind !== 'comment')
    .map(([kind, text]) => [kind, text]));
  const original = signature(tokens);
  const bom = source.startsWith('\uFEFF') ? 1 : 0;
  let updated = source;
  for (const [kind, text, first, last] of [...tokens].reverse()) {
    if (kind !== 'comment' || !removable(text)) continue;
    const start = first + bom;
    const end = last + 1 + bom;
    const adjacent = start > 0 && end < updated.length &&
      !/\s/.test(updated[start - 1]) && !/\s/.test(updated[end]);
    const candidate = updated.slice(0, start) + updated.slice(end);
    const safe = !adjacent || signature(cssTokens(candidate)) === original;
    if (safe) updated = candidate;
    result.push([offset + start, offset + end, safe ? 'css' : 'manual']);
  }
}

function html(source: string, result: Range[]) {
  let pos = 0;
  while (pos < source.length) {
    const start = source.indexOf('<', pos);
    if (start < 0) break;
    if (source.startsWith('<!--', start)) {
      const close = source.indexOf('-->', start + 4);
      if (close < 0) throw new Error('Unterminated HTML comment');
      const end = close + 3;
      if (removable(source.slice(start, end))) result.push([start, end, 'markup']);
      pos = end;
      continue;
    }
    if (!/^<(?:[!?]|\/?[a-z])/i.test(source.slice(start))) {
      pos = start + 1;
      continue;
    }
    let end = start + 1, quote = '';
    for (; end < source.length; end++) {
      const c = source[end];
      if (quote) { if (c === quote) quote = ''; }
      else if (c === '"' || c === "'") quote = c;
      else if (c === '>') break;
    }
    if (end === source.length) break;
    const tag = source.slice(start, end + 1);
    const name = /^<\s*(script|style|textarea|title)\b/i.exec(tag)?.[1]?.toLowerCase();
    pos = end + 1;
    if (!name) continue;
    const closing = new RegExp(`</\\s*${name}\\s*>`, 'ig');
    closing.lastIndex = pos;
    const match = closing.exec(source);
    if (!match) throw new Error(`Unterminated HTML ${name}`);
    const contents = source.slice(pos, match.index);
    if (name === 'style') css(contents, pos, result);
    if (name === 'script' && !/\btype\s*=\s*['"](?:application\/json|application\/ld\+json|importmap|speculationrules)['"]/i.test(tag)) js(contents, pos, result, 'embedded.js');
    pos = closing.lastIndex;
  }
}

function svelte(source: string, result: Range[]) {
  const tree = parse(source, { modern: true });
  const seen = new Set<object>();
  function visit(value: unknown): void {
    if (!value || typeof value !== 'object' || seen.has(value)) return;
    seen.add(value);
    const node = value as Record<string, unknown>;
    if ((node.type === 'Comment' || node.type === 'Line' || node.type === 'Block') && typeof node.start === 'number' && Number.isInteger(node.start) && typeof node.end === 'number' && Number.isInteger(node.end)) {
      const text = source.slice(node.start, node.end);
      if (/^(?:<!--|\/\*|\/\/)/.test(text) && removable(text)) result.push([node.start, node.end, node.type === 'Comment' ? 'markup' : 'js']);
    }
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) value.forEach(visit);
      else if (typeof value === 'object') visit(value);
    }
  }
  visit(tree.fragment);
  for (const script of [tree.instance, tree.module]) {
    if (script) {
      const content = script.content as typeof script.content & { start: number; end: number };
      js(source.slice(content.start, content.end), content.start, result, 'embedded.ts');
    }
  }
  if (tree.css) {
    const { start, end } = tree.css.content;
    css(source.slice(start, end), start, result);
  }
}

const input = JSON.parse(readFileSync(0, 'utf8')) as { path: string; source: string }[];
const output = input.map(({ path, source }) => {
  const result: Range[] = [];
  if (/\.svelte$/i.test(path)) svelte(source, result);
  else if (/\.html$/i.test(path)) html(source, result);
  else if (/\.css$/i.test(path)) css(source, 0, result);
  else js(source, 0, result, path);
  return [...new Map(result.map(range => [range.slice(0, 2).join(':'), range])).values()]
    .sort((a, b) => a[0] - b[0])
    .map(([start, end, kind]) => {
      const comment = source.slice(start, end);
      const newlines = kind === 'js' ? (comment.match(/\r\n|[\r\n\u2028\u2029]/g) || []).join('') : '';
      const separatesTokens = kind === 'js' && start > 0 && end < source.length &&
        !/\s/.test(source[start - 1]) && !/\s/.test(source[end]);
      const replacement = kind === 'manual' ? null : newlines || (separatesTokens ? ' ' : '');
      const lineEnd = kind === 'js' && /^[ \t]*(?:[\r\n\u2028\u2029]|$)/.test(source.slice(end));
      const editStart = lineEnd ? start - source.slice(0, start).match(/[ \t]*$/)![0].length : start;
      return [[...source.slice(0, editStart)].length, [...source.slice(0, end)].length, replacement];
    });
});
process.stdout.write(JSON.stringify(output));
