
import { mount } from 'svelte';
import App from './App.svelte';
import './app.css';
import { HttpOperationCaller } from './lib/lib__shared';

const projectInstance = document.querySelector<HTMLMetaElement>(
  'meta[name="anechoic-project-instance"]')?.content;
const projectRoot = new URLSearchParams(location.search).get('project_root');

mount(App, { target: document.getElementById('app')!, props: { caller:
  new HttpOperationCaller(projectInstance, projectRoot) } });
