export {};
  type HostContext = { availableDisplayModes?: string[]; displayMode?: string };
  type Response = { mode?: string; isError?: boolean; hostContext?: HostContext };
  const status = document.querySelector<HTMLElement>('#status')!;
  const button = document.querySelector<HTMLButtonElement>('#ping')!;
  const expand = document.querySelector<HTMLButtonElement>('#expand')!;
  const presentation = document.querySelector<HTMLElement>('#presentation')!;
  const displayError = document.querySelector<HTMLElement>('#display-error')!;
  let hostContext: HostContext = {};
  let expanding = false;
  let nextId = 1;
  let projectRoot: unknown;
  const requests = new Map<number, { resolve: (value: Response) => void; reject: (error: Error) => void }>();
  function updatePresentation(context: HostContext = {}) {
    hostContext = { ...hostContext, ...context };
    const modes = hostContext.availableDisplayModes ?? [];
    presentation.textContent = `Presentation: ${hostContext.displayMode ?? 'unknown'}; available: ${modes.join(', ') || 'not declared'}`;
    expand.disabled = expanding || !modes.includes('fullscreen') || hostContext.displayMode === 'fullscreen';
  }
  function request(method: string, params: object): Promise<Response> {
    const id = nextId++;
    const promise = new Promise<Response>((resolve, reject) => requests.set(id, { resolve, reject }));
    window.parent.postMessage({ jsonrpc: '2.0', id, method, params }, '*');
    return promise;
  }
  window.addEventListener('message', event => {
    if (event.source !== window.parent || event.data?.jsonrpc !== '2.0') return;
    const message = event.data;
    if (message.method === 'ui/notifications/host-context-changed') {
      updatePresentation(message.params);
      return;
    }
    if (message.method === 'ui/notifications/tool-input') {
      projectRoot = message.params?.arguments?.project_root;
      return;
    }
    if (message.method === 'ui/notifications/tool-result') {
      document.querySelector<HTMLElement>('#result')!.textContent = message.params?.structuredContent?.message ?? 'Host result received';
      return;
    }
    const pending = requests.get(message.id);
    if (!pending) return;
    requests.delete(message.id);
    if (message.error) pending.reject(new Error(message.error.message));
    else pending.resolve(message.result);
  });
  button.onclick = async () => {
    button.disabled = true;
    try {
      const result = await request('tools/call', {
        name: 'workbench_ui_ping',
        arguments: typeof projectRoot === 'string' ? { project_root: projectRoot } : {},
      });
      if (result.isError) throw new Error('Host returned a tool error');
      status.textContent = 'Tool bridge passed';
    } catch (error) {
      status.textContent = `Tool bridge failed: ${error instanceof Error ? error.message : String(error)}`;
    } finally {
      button.disabled = false;
    }
  };
  expand.onclick = async () => {
    if (!hostContext.availableDisplayModes?.includes('fullscreen')) return;
    displayError.textContent = '';
    expanding = true;
    updatePresentation();
    try {
      const result = await request('ui/request-display-mode', { mode: 'fullscreen' });
      updatePresentation({ displayMode: result.mode });
    } catch (error) {
      displayError.textContent = `Expansion failed: ${error instanceof Error ? error.message : String(error)}`;
    } finally {
      expanding = false;
      const modes = hostContext.availableDisplayModes ?? [];
      expand.disabled = !modes.includes('fullscreen') || hostContext.displayMode === 'fullscreen';
    }
  };
  request('ui/initialize', {
    appInfo: { name: 'ANECHOIC UI compatibility probe', version: '0.0.2' },
    appCapabilities: { availableDisplayModes: ['inline', 'fullscreen'] },
    protocolVersion: '2026-01-26',
  }).then(result => {
    updatePresentation(result.hostContext);
    window.parent.postMessage({ jsonrpc: '2.0', method: 'ui/notifications/initialized', params: {} }, '*');
    status.textContent = 'Host bridge connected';
    button.disabled = false;
  }).catch(error => { status.textContent = `Host bridge failed: ${error instanceof Error ? error.message : String(error)}`; });
