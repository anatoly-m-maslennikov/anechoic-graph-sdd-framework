
export type ChatEntry = { id: string; role: string; text: string };
export type NativeRequest = { id: string | number;
  method: string; params: Record<string, any> };

export function record(value: unknown): value is Record<string, any> {
  return value !== null && typeof value === 'object' &&
    !Array.isArray(value); }

function contentText(value: unknown): string {
  if (typeof value === 'string') return value;
  if (!Array.isArray(value)) return '';
  return value.map((part) => record(part) && typeof part.text === 'string' ?
    part.text : '').filter(Boolean).join('\n');
}

export function historyEntries(thread: unknown): ChatEntry[] {
  if (!record(thread) || !Array.isArray(thread.turns)) return [];
  return thread.turns.flatMap((turn) => (Array.isArray(
    turn.items) ? turn.items : []).flatMap(
    (item: Record<string, any>) => {
      if (item.type !== 'userMessage' &&
        item.type !== 'agentMessage') return [];
      const text = contentText(item.type === 'userMessage' ?
        item.content : item.text);
      return text ? [{ id: String(item.id), role:
        item.type === 'userMessage' ? 'You' : 'Codex', text }] : [];
    },
  ));
}

export function interaction(packet: unknown): NativeRequest | null {
  return record(packet) && (typeof packet.id === 'string' ||
    typeof packet.id === 'number') && typeof packet.method === 'string'
    ? { id: packet.id, method: packet.method, params:
      record(packet.params) ? packet.params : {} } : null;
}

export function applyNativeEvent(entries:
  ChatEntry[], packet: unknown): ChatEntry[] {
  if (!record(packet) || !record(packet.params)) return entries;
  const params = packet.params;
  let id = ''; let text = ''; let role = 'Codex'; let append = false;
  if (packet.method === 'item/agentMessage/delta' &&
    typeof params.delta === 'string') {
    id = params.itemId; text = params.delta; append = true;
  } else if (packet.method === 'item/completed' &&
    params.item?.type === 'agentMessage') {
    id = params.item.id; text = contentText(params.item.text);
  } else if (['item/started', 'item/completed'].includes(
    packet.method) && params.item?.type === 'mcpToolCall') {
    const item = params.item; id = `tool-${item.id}`; role = 'Activity';
    const status = item.status ||
      (packet.method === 'item/completed' ? 'completed' : 'working');
    text = `${item.server || 'MCP'} · ${item.tool || 'Tool'} — ${status}`;
  }
  if (typeof id !== 'string' || !id || !text) return entries;
  const previous = entries.find((entry) => entry.id === id);
  const next = { id, role, text: append &&
    previous ? previous.text + text : text };
  return previous ? entries.map((entry) =>
    entry.id === id ? next : entry) : [...entries, next];
}

export function sseFrames(buffer: string): {
  events: Record<string, any>[]; rest: string} {
  const frames = buffer.replace(/\r\n/g, '\n').split('\n\n');
  const rest = frames.pop() || '';
  return { rest, events: frames.flatMap((frame) => {
    const data = frame.split('\n').filter((line) => line.startsWith(
      'data:')).map((line) => line.slice(5).trimStart()).join('\n');
    if (!data) return [];
    const value = JSON.parse(data);
    if (!record(value)) throw new Error('Invalid Codex event');
    return [value];
  }) };
}

export function inputAnswers(questions: Array<{
  id: string}>, answers: Record<string, string>) {
  return { answers: Object.fromEntries(questions.map((question) =>
    [question.id, { answers: [answers[question.id] || ''] }])) };
}
