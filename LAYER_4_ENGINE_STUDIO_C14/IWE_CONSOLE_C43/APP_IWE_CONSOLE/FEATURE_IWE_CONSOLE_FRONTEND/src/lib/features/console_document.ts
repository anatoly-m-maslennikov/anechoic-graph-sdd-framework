import type { Snippet } from 'svelte';

export type AtomDestination = 'modal' | 'pane' | 'tab';
export type AtomActionsSnippet = Snippet<[AtomDocumentData, (document:
  AtomDocumentData) => void]>;

export interface AtomDocumentData {
  ref_id: string;
  exact_ref: string;
  version: number | string;
  status: string;
  filename: string;
  body: string;
  template?: string | null;
  updated_at?: string | null;
  history: { ref_id: string; version: number | string; status:
    string; filename: string }[];
  relations: { type: string; ref_id: string; direction: string; derived:
    boolean }[];
  authored_relations?: { type: string; ref_id: string }[];
  contained: { ref_id: string; filename: string }[];
  archive_pending?: boolean;
  ticket_statuses?: string[];
}

export type AtomTextPart = { text: string; ref?: string };

export function atomTextParts(text: string): AtomTextPart[] {
  const pattern =
    /\b[A-Z][A-Z0-9]*-[A-Z][A-Z0-9]*-\d+(?:@\d+(?:-draft\b)?)?\b/g;
  const parts: AtomTextPart[] = [];
  let start = 0;
  for (const match of text.matchAll(pattern)) {
    if (match.index > start) parts.push({ text: text.slice(start,
      match.index) });
    parts.push({ text: match[0], ref: match[0] });
    start = match.index + match[0].length;
  }
  if (start < text.length) parts.push({ text: text.slice(start) });
  return parts;
}
