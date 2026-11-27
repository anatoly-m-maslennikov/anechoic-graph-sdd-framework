import {
  STORAGE_PREFIX, legacyStorageKey, readConsoleStorage, storageKey,
} from './lib/lib__shared';

export function standaloneContext(browserStorage: <T>(operation:
  () => T) => T | undefined) {
  const base = location.pathname.replace(/\/+$/, '');
  const urlProject = base.split('/').filter(Boolean).at(-1) ?? '';
  const parameters = new URLSearchParams(location.search);
  const projectRoot = parameters.get('project_root');
  const explicitWorkspaceId = parameters.get('workspace');
  const embedded = parameters.get('embedded') === '1';
  const sessionScope = projectRoot || urlProject;
  const standaloneSessionKey =
    `${STORAGE_PREFIX}${sessionScope}.standalone-session`;
  const persistedStandaloneId = browserStorage(
    () => readConsoleStorage(localStorage, standaloneSessionKey),
  );
  const standaloneBinding = !explicitWorkspaceId ||
    explicitWorkspaceId === persistedStandaloneId;
  const workspaceId = (() => {
    if (!standaloneBinding) return explicitWorkspaceId ?? undefined;
    if (persistedStandaloneId) return persistedStandaloneId;
    const created = `standalone-${crypto.randomUUID()}`;
    browserStorage(() => localStorage.setItem(standaloneSessionKey, created));
    return created;
  })();
  if (explicitWorkspaceId && explicitWorkspaceId === persistedStandaloneId) {
    parameters.delete('workspace');
    const search = parameters.toString(); history.replaceState(null,
      '', `${base}${search ? `?${search}` : ''}${location.hash}`);
  }
  const namespace = storageKey(urlProject,
    workspaceId, projectRoot ?? undefined);
  const migrationKey = `${standaloneSessionKey}.unbound-migrated`;
  const legacySessionId = standaloneBinding ? browserStorage(
    () => localStorage.getItem(legacyStorageKey(standaloneSessionKey)),
  ) : null;
  return {
    parameters, projectRoot, workspaceId,
      embedded, standaloneBinding, namespace,
    legacyNamespace: storageKey(urlProject), legacySessionId, migrationKey,
    migrationProgressKey: `${migrationKey}.progress`,
  };
}
