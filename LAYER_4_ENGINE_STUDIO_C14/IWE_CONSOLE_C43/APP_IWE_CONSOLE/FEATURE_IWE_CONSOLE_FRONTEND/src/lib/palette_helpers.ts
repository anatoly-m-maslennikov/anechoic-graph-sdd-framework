import type { Command } from './types';

export function filterCommands(commands: Command[
  ], query: string) { return commands.filter(
  (command) => command.label.toLowerCase().includes(query.toLowerCase())); }
export function moveSelection(index: number,
  count: number, direction: number) {
  return Math.max(0, Math.min(index + direction, Math.max(0, count - 1))); }
