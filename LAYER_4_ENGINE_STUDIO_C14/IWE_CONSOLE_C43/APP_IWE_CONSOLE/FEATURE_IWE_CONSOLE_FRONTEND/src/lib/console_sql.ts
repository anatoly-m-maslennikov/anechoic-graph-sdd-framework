export type ConsoleView = { kind: 'table' | 'document' | 'graph' | 'imports' | 'structure'; layout: 'vertical' | 'horizontal' };

const identifierCharacter = /[\w$\u0080-\uFFFF]/;

function dollarQuoteEnd(sql: string, start: number): number | undefined {
  if (identifierCharacter.test(sql[start - 1] ?? '')) return;
  const tag = sql.slice(start).match(/^\$(?:[a-z_\u0080-\uFFFF][\w\u0080-\uFFFF]*)?\$/i)?.[0];
  if (!tag) return;
  const end = sql.indexOf(tag, start + tag.length);
  if (end < 0) throw new Error('Unclosed dollar-quoted SQL string.');
  return end + tag.length;
}

// Replace comments with whitespace. Mask expressions with a non-space marker.
function topLevel(sql: string, rejectComments = false): string {
  const chars = sql.split('');
  let depth = 0, quote = '', escape = false, line = false, block = 0;
  for (let i = 0; i < sql.length; i++) {
    const c = sql[i], next = sql[i + 1];
    if (line) { chars[i] = ' '; if (c === '\n' || c === '\r') line = false; continue; }
    if (block) {
      chars[i] = ' ';
      if (c === '/' && next === '*') { chars[++i] = ' '; block++; }
      else if (c === '*' && next === '/') { chars[++i] = ' '; block--; }
      continue;
    }
    if (quote) {
      chars[i] = '#';
      if (escape && c === '\\' && next !== undefined) chars[++i] = '#';
      else if (c === quote) { if (next === quote) chars[++i] = '#'; else quote = ''; }
      continue;
    }
    if (rejectComments && ((c === '-' && next === '-') || (c === '/' && next === '*'))) throw new Error('Queries with comments must be edited directly.');
    if (c === '-' && next === '-') { chars[i] = chars[++i] = ' '; line = true; continue; }
    if (c === '/' && next === '*') { chars[i] = chars[++i] = ' '; block = 1; continue; }
    if (c === "'" || c === '"') {
      chars[i] = '#'; quote = c;
      escape = c === "'" && sql[i - 1]?.toLowerCase() === 'e' && !identifierCharacter.test(sql[i - 2] ?? '');
      continue;
    }
    const dollarEnd = c === '$' ? dollarQuoteEnd(sql, i) : undefined;
    if (dollarEnd !== undefined) { chars.fill('#', i, dollarEnd); i = dollarEnd - 1; continue; }
    if ('([{'.includes(c)) { depth++; chars[i] = '#'; continue; }
    if (')]}'.includes(c)) { depth--; chars[i] = '#'; if (depth < 0) throw new Error('Unbalanced SQL delimiters.'); continue; }
    if (depth) chars[i] = '#';
  }
  if (quote || block || depth) throw new Error('Unclosed SQL string, comment, or delimiter.');
  return chars.join('');
}

function directive(sql: string): RegExpMatchArray | null {
  return topLevel(sql).match(/(?<![\w$\u0080-\uFFFF])VIEW\s+(?:(TABLE|DOC(?:UMENT)?|STRUCTURE)|(GRAPH|IMPORTS)(?:\s+(VERTICAL|HORIZONTAL))?)\s*;?\s*$/i);
}
export function consoleView(sql: string): ConsoleView {
  let match: RegExpMatchArray | null;
  try { match = directive(sql); } catch { match = null; }
  const kind = (match?.[1] ?? match?.[2])?.toLowerCase();
  return { kind: kind === 'doc' || kind === 'document' ? 'document' : kind === 'graph' || kind === 'imports' || kind === 'structure' ? kind : 'table', layout: match?.[3]?.toLowerCase() === 'horizontal' ? 'horizontal' : 'vertical' };
}

function editLimit(before: string, mask: string, suffix: string, value: string): string {
  if (value && !/^\d+$/.test(value)) throw new Error('Limit must be a non-negative integer.');
  const limits = [...mask.matchAll(/\bLIMIT\b/gi)];
  if (limits.length > 1) throw new Error('Multiple LIMIT clauses cannot be edited safely.');
  const existing = limits[0]?.index;
  if (existing !== undefined) {
    if (!/^LIMIT\s+\d+\s*$/i.test(mask.slice(existing))) throw new Error('This LIMIT clause cannot be edited safely.');
    before = before.slice(0, existing).trimEnd();
  }
  return before + (value ? ` LIMIT ${value}` : '') + suffix;
}

function replaceFilter(head: string, mask: string, where: number, column: string, clause: string, value: string): string | false {
  if (!head.slice(where).toLowerCase().includes(`"${column}"`)) return false;
  const escaped = column.replaceAll('.', '\\.');
  const pattern = new RegExp(`\\b(WHERE|AND)\\s+"${escaped}"\\s*=\\s*(?:'([^']|'')*'|-?\\d+)(?=\\s*(?:AND\\b|$))`, 'gi');
  const matches = [...head.matchAll(pattern)].filter((match) => match.index! >= where &&
    mask.slice(match.index, match.index! + match[1].length).toLowerCase() === match[1].toLowerCase());
  if (matches.length !== 1 || /\bOR\b/i.test(mask.slice(where))) throw new Error(`The query uses ${column} in a complex condition. Edit it directly.`);
  const [found] = matches;
  const leading = head.slice(0, found.index).trimEnd();
  const rest = head.slice(found.index! + found[0].length);
  if (value) return `${leading} ${found[1]} ${clause}${rest}`;
  return leading + (found[1].toLowerCase() === 'where' ? rest.replace(/^\s+AND\s+/i, ' WHERE ') : rest);
}

export function editConsoleSql(sql: string, field: 'component' | 'tier' | 'template' | 'limit', value: string): string {
  const mask = topLevel(sql, true);
  const view = directive(sql);
  const end = view?.index ?? sql.length;
  const body = sql.slice(0, end);
  const bodyMask = mask.slice(0, end);
  if (!/^\s*SELECT\b/i.test(bodyMask) || /\b(UNION|INTERSECT|EXCEPT|JOIN|WITH)\b/i.test(bodyMask) || /;\s*\S/.test(bodyMask)) throw new Error('This query is too complex for the builder. Edit SQL directly.');
  const semicolon = bodyMask.lastIndexOf(';');
  const boundary = semicolon >= 0 ? semicolon : body.length;
  const suffix = body.slice(boundary) + (view ? ` ${sql.slice(end)}` : '');
  const before = body.slice(0, boundary).trimEnd();
  const cleanMask = bodyMask.slice(0, boundary);
  if (field === 'limit') return editLimit(before, cleanMask, suffix, value);
  const from = /\bFROM\s+atoms\b/i.exec(cleanMask);
  if (!from) throw new Error('Filter controls require a query from atoms.');
  const fromTail = cleanMask.slice(from.index + from[0].length).split(/\b(?:WHERE|GROUP|HAVING|ORDER|LIMIT|OFFSET|QUALIFY|WINDOW)\b/i)[0];
  if (fromTail.includes(',')) throw new Error('Queries with multiple sources must be edited directly.');
  const column = { component: 'header.container.component', tier: 'header.tier', template: 'header.context.template' }[field];
  if (field === 'tier' && value && !/^-?\d+$/.test(value)) throw new Error('Tier must be an integer.');
  const after = /\b(GROUP\s+BY|HAVING|ORDER\s+BY|LIMIT|OFFSET|QUALIFY|WINDOW)\b/i.exec(cleanMask);
  const at = after?.index ?? before.length;
  const head = before.slice(0, at).trimEnd(), tail = before.slice(at).trimStart();
  const where = /\bWHERE\b/i.exec(cleanMask.slice(0, at));
  const clause = `"${column}" = ${field === 'tier' ? value : `'${value.replaceAll("'", "''")}'`}`;
  const existing = where && replaceFilter(head, cleanMask.slice(0, at), where.index, column, clause, value);
  if (existing !== false && existing !== null) return existing + (tail ? ` ${tail}` : '') + suffix;
  if (!value) return sql;
  const condition = where ? head.slice(where.index + where[0].length).trim() : '';
  const grouped = where && /\bOR\b/i.test(cleanMask.slice(where.index, at)) ? `(${condition})` : condition;
  const edited = where ? `${head.slice(0, where.index)}WHERE ${grouped} AND ${clause}` : `${head} WHERE ${clause}`;
  return edited + (tail ? ` ${tail}` : '') + suffix;
}

export function setConsoleView(sql: string, kind: ConsoleView['kind']): string {
  const current = directive(sql);
  const body = (current ? sql.slice(0, current.index) : sql).trimEnd().replace(/;$/, '').trimEnd();
  return kind === 'table' ? body : `${body}\nVIEW ${kind.toUpperCase()}`;
}
