export const TOOL_REST_PATH = "/";

export type QueryRun = {
  sql: string;
  cursor_position?: number;
  page_size?: number;
  preview?: number;
  result_delivery?: "file" | "inline" | "auto";
  result_format?: "json_matrix" | "csv" | "toon";
  save?: boolean;
  name?: string;
};

export type QueryColumn = {
  name: string;
  type: string;
  has_values: boolean;
};

export type QueryPageCore = {
  query_id: string;
  columns: Array<QueryColumn>;
};
