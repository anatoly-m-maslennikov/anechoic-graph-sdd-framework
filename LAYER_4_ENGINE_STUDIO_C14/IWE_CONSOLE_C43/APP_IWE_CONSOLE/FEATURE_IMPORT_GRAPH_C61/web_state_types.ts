export type StateTarget = ['local', '$owner'] | ['ambient', 'ENV'];
export type EventKind = 'call' | 'read' | 'write' | 'return' | 'output';
export type StateEvent = {kind: EventKind; target: StateTarget[0] | '';
  name: string; line: number; forward?: boolean};
export type Input = Record<string, boolean>;
export type StateCase = {
  action: string;
  line: number;
  column?: number;
  inlineable?: boolean;
  input: Input | null;
  reachable: true; complete: boolean; declaredNoOp: false;
  events: StateEvent[];
};
export type CallTargets = Map<string, string> | null;
export type Sources = Record<string, string>;
export type GraphPayload = {sources: Sources; call_sites: Record<string,
  [number, number, string][]>};
