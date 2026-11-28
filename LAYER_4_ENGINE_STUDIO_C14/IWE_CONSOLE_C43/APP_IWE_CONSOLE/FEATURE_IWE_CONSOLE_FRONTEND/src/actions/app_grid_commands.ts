import type { Command, GridState, QueryResult } from '../lib/lib__shared';

type GridTab = { result?: QueryResult; busy?: boolean };

function gridColumn(active: GridTab | undefined) {
  const result = active?.result; if (!result) return -1;
  const value = window.prompt(
    `Result column index (0-${result.columns.length - 1})`, '0');
  if (value === null) return -1;
  const index = Number(value); return Number.isInteger(index) &&
    index >= 0 && index < result.columns.length ? index : -1;
}
function gridRow(active: GridTab | undefined) {
  const result = active?.result; if (!result) return -1;
  const value = window.prompt(
    `Result row index on this page (0-${result.rows.length - 1})`, '0');
  if (value === null) return -1;
  const index = Number(value); return Number.isInteger(index) &&
    index >= 0 && index < result.rows.length ? index : -1;
}

function resultValue(value: unknown) {
  if (value === null) return 'NULL';
  try { return typeof value === 'object' ?
    JSON.stringify(value) : String(value); }
  catch { return String(value); }
}

function copyResult(value: unknown) {
  void navigator.clipboard?.writeText(resultValue(value)).catch(() => {});
}

function filterGrid(active: GridTab | undefined, grid:
  GridState, setGrid: (next: GridState) => void) {
  if (!active?.result || active.busy) return;
  const column = gridColumn(active);
  if (column < 0) return;
  const value = window.prompt(`Filter ${active.result.columns[column].name}`,
    grid.filters.find((item) => item.column === column)?.value ?? '');
  if (value === null) return;
  const filters = grid.filters.filter((item) => item.column !== column);
  if (value) filters.push({ column, operator: 'contains', value });
  setGrid({ ...grid, filters });
}

function readCommands(
  getActive: () => GridTab | undefined, result: QueryResult | undefined,
): Command[] {
  return [
    { id: 'grid-copy-value', label: 'Result grid: Copy cell value',
      enabled: !!result, run: () => {
        const row = gridRow(getActive());
        const column = gridColumn(getActive());
        if (row >= 0 && column >= 0) copyResult(result!.rows[row][column]);
      } },
    { id: 'grid-show-value', label: 'Result grid: Show full cell value',
      enabled: !!result, run: () => {
        const row = gridRow(getActive());
        const column = gridColumn(getActive());
        if (row >= 0 && column >= 0)
          window.alert(resultValue(result!.rows[row][column]));
      } },
    { id: 'grid-copy-row', label: 'Result grid: Copy row', enabled: !!result,
      run: () => {
        const row = gridRow(getActive());
        if (row >= 0) copyResult(result!.rows[row]);
      } },
  ];
}

export function gridCommands(getActive: () => GridTab | undefined, getGrid:
  () => GridState, setGrid: (next: GridState) => void): Command[] {
  const active = getActive();
  const result = active?.result;
  const grid = getGrid();
  const enabled = !!result && !active?.busy;
  const sort = (direction: 'asc' | 'desc') => {
    const column = gridColumn(getActive());
    if (column < 0) return;
    const current = getGrid();
    setGrid({ ...current, sort: [...current.sort.filter((item) =>
      item.column !== column), { column, direction }] });
  };
  const group = (direction: 'asc' | 'desc') => {
    const column = gridColumn(getActive());
    if (column >= 0)
      setGrid({ ...getGrid(), group_by: { column, direction } });
  };
  return [
    ...readCommands(getActive, result),
    { id: 'grid-sort-asc', label: 'Result grid: Sort column ascending',
      enabled, run: () => sort('asc') },
    { id: 'grid-sort-desc', label: 'Result grid: Sort column descending',
      enabled, run: () => sort('desc') },
    { id: 'grid-group-asc', label: 'Result grid: Group column ascending',
      enabled, run: () => group('asc') },
    { id: 'grid-group-desc', label: 'Result grid: Group column descending',
      enabled, run: () => group('desc') },
    { id: 'grid-clear-group', label: 'Result grid: Clear grouping',
      enabled: enabled && !!grid.group_by,
      run: () => setGrid({ ...getGrid(), group_by: undefined }) },
    { id: 'grid-filter', label: 'Result grid: Filter column', enabled,
      run: () => filterGrid(getActive(), getGrid(), setGrid) },
    { id: 'grid-clear-filter', label: 'Result grid: Clear filter',
      enabled: enabled && grid.filters.length > 0,
      run: () => setGrid({ ...getGrid(), filters: [] }) },
  ];
}
