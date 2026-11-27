import type { AtomDestination, AtomDocumentData } from './console_document';
import type { OperationCaller } from './transport';

export class ConsoleNavigation {
  modal = $state<string | null>(null);
  panes = $state<Record<string, string[]>>({});
  generation = $state(0);
  private editors = new Map<() => Promise<boolean>, () => boolean>();

  constructor(private caller: OperationCaller, private tab: () => string,
    private openTab: (ref: string) => Promise<void>,
      private showPane: () => void) {}

  register = (flush: () => Promise<boolean>, dirty: () => boolean) => {
    this.editors.set(flush, dirty);
    return () => { this.editors.delete(flush); };
  };

  hasChanges() { return [...this.editors.values()].some((dirty) => dirty()); }

  async canNavigate() {
    for (const [flush, dirty] of this.editors) if (
      dirty() && !await flush()) return false;
    return true;
  }

  call = (name: string, args: Record<string,
    unknown>) => this.caller.call(name, args);
  load = (ref: string) => this.caller.call<AtomDocumentData>(
    'iwe_console_atom_document', { ref_id: ref });

  dismiss = async () => { if (await this.canNavigate()) this.modal = null; };
  closePane = async () => { if (await this.canNavigate(
    )) this.panes = { ...this.panes, [this.tab()]: [] }; };

  open = async (ref: string, destination: AtomDestination) => {
    if (!await this.canNavigate()) return;
    if (destination === 'modal') { this.modal = ref; return; }
    if (destination === 'pane') {
      const tab = this.tab();
      this.panes = { ...this.panes, [tab]: [...new Set(
        [...(this.panes[tab] ?? []), ref])] };
      this.modal = null;
      this.showPane();
    } else await this.openTab(ref);
  };

  changed = async (ref: string) => {
    if (!await this.canNavigate()) return;
    this.generation += 1;
    this.modal = ref;
  };
}
