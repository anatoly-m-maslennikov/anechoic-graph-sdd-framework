<script lang="ts">
  import { atomTextParts } from './console_document';
  import AtomLink from './AtomLink.svelte';
  import { atomGraph, edgePoints, graphLayout, importsGraph,
    relationTypes, type Graph } from './console_graph';
  import type { QueryResult } from './types';
  let { refs, imports = false, importOccurrences, layout, query, onOpen }: {
    refs: string[]; imports?: boolean; importOccurrences?
      : string[]; layout: 'vertical' | 'horizontal';
    query: (sql: string) => Promise<QueryResult>;
    onOpen: (ref: string, dest: 'modal' | 'pane' | 'tab') => void;
  } = $props();
  let graph = $state<Graph>({ nodes: [], edges: [] });
  let types = $state<string[]>([]), selected = $state<string[]>([]);
  let depthInput = $state(0), depth = $state(0), structure = $state(false);
  let error = $state(''), typesError = $state(
    ''), loading = $state(false), generation = 0;
  const arrowId = $props.id();
  let positioned = $derived(graphLayout(graph, layout));
  $effect(() => {
    const runQuery = query;
    if (imports) return;
    let active = true;
    relationTypes(runQuery).then(result => {
      if (active) { typesError = ''; types = result; selected = [...result]; }
    }).catch(reason => { if (active) typesError = String(reason); });
    return () => { active = false; };
  });
  $effect(() => {
    const runQuery = query, seeds = [...refs], selectedTypes =
      [...selected], level = depth, withStructure =
      structure, showImports = imports, occurrences =
        importOccurrences ? [...importOccurrences] : undefined;
    const current = ++generation;
    loading = true; error = '';
    const task = showImports ? importsGraph(runQuery, occurrences) :
      atomGraph(runQuery, seeds, level, selectedTypes, withStructure);
    task.then(result => { if (current === generation) graph = result; })
      .catch(reason => { if (current === generation) { graph =
        { nodes: [], edges: [] }; error = String(reason); } })
      .finally(() => { if (current === generation) loading = false; });
  });
  function showRelated() {
    if (!Number.isSafeInteger(depthInput) || depthInput < 0) {
      error = 'Depth must be a non-negative whole number.'; return;
    }
    error = ''; depth = depthInput;
  }
  function selectType(type: string, checked: boolean) {
    selected = checked ? [...selected, type] :
      selected.filter(value => value !== type);
  }
</script>

<section class="graph-view" data-layout={layout}
  aria-label={imports ? 'Imports Graph' : 'Atom Graph'}>
  {#if !imports}
    <div class="controls">
      <label>Depth <input type="number" min="0"
        step="1" bind:value={depthInput} /></label>
      <button type="button" onclick={showRelated}>Show related</button>
      <label><input type="checkbox"
        bind:checked={structure} /> Components and Packages with Spec
          Bindings</label>
      <details><summary>Relation types (
        {selected.length}/{types.length})</summary>
        {#each types as type}<label><input type="checkbox"
          checked={selected.includes(type)}
          onchange={(event) => selectType(type,
            event.currentTarget.checked)} /> {type}</label>{/each}
      </details>
    </div>
  {/if}
  {#if loading}<p role="status">Loading graph…</p>{/if}
  {#if typesError}<p role="alert">{typesError}</p>{/if}
  {#if error}<p role="alert">{error}</p>{/if}
  {#if !loading && !error && !graph.nodes.length}<p>No graph nodes.</p>{/if}
  {#if graph.edges.length}
    <details><summary>Graph edges ({graph.edges.length})</summary><ul>
      {#each graph.edges as edge}<li>
        {#each atomTextParts(`${edge.source} → ${edge.target}`) as part}
          {#if part.ref && !imports}<AtomLink refId={part.ref}
            {onOpen} />{:else}{part.text}{/if}
        {/each}
        · {edge.type}{edge.violation ? ' · violation' : ''}
      </li>{/each}
    </ul></details>
  {/if}
  <div class="viewport">
    <div class="canvas" style:width={`${positioned.width}px`}
      style:height={`${positioned.height}px`}>
      <svg width={positioned.width}
        height={positioned.height} aria-hidden="true">
        <defs><marker id={arrowId} markerWidth="8"
          markerHeight="8" refX="7" refY="4"
          orient="auto"><path d="M0,0 L8,4 L0,8 z"
            fill="context-stroke" /></marker></defs>
        {#each graph.edges as edge}
          {@const from = positioned.positions.get(edge.source)}
          {@const to = positioned.positions.get(edge.target)}
          {#if from && to}
            {#if edge.source === edge.target}
              <path
                d={`M${from.x + 150},${from.y} C${from.x
                  + 200},${from.y - 60} ${from.x + 50},${from.y - 60} ${from.x
                    + 40},${from.y}`}
                class:violation={edge.violation}
                  marker-end={`url(#${arrowId})`} />
            {:else}
              <line {...edgePoints(from, to)} class:violation={edge.violation}
                marker-end={`url(#${arrowId})`} />
            {/if}
            <text x={(from.x + to.x) / 2 + 90} y={(from.y + to.y) / 2 + 20}
              class:violation={edge.violation}>{edge.type}{edge.violation
                ? ' · violation' : ''}</text>
          {/if}
        {/each}
      </svg>
      {#each graph.nodes as node}
        {@const point = positioned.positions.get(node.id)}
        {#if point}<div class="node" style:left={`${point.x}px`}
          style:top={`${point.y}px`}>
          <small>{node.kind}</small>
          {#if node.kind === 'Atom'}<AtomLink refId={node.id}
            label={node.label} {onOpen} />{:else}<span>{node.label}</span>{/if}
        </div>{/if}
      {/each}
    </div>
  </div>
</section>

<style>
  .controls { display: flex; flex-wrap: wrap; align-items: center;
    gap: .75rem; }
  .controls input[type=number] { width: 4rem; }
  details label { display: block; }
  .viewport { overflow: auto; max-height: 70vh; border: 1px solid #aaa;
    margin-top: .5rem; }
  .canvas { position: relative; }
  svg { position: absolute; inset: 0; pointer-events: none; }
  line, svg > path { stroke: #667; stroke-width: 2; fill: none; }
  line.violation, svg > path.violation { stroke: #c22; stroke-width: 3; }
  text { fill: #445; font-size: 11px; paint-order: stroke; stroke: white;
    stroke-width: 3px; }
  text.violation { fill: #b00; }
  .node { position: absolute; width: 180px; min-height: 48px;
    box-sizing: border-box; padding: .3rem; background: var(--surface, white);
      border: 1px solid #888; border-radius: 4px; overflow-wrap: anywhere; }
  .node small { display: block; color: #666; }
</style>
