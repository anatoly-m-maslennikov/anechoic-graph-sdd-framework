
import { mount } from 'svelte';
import App from './App.svelte';
import './app.css';
import { HttpOperationCaller } from './lib/lib__shared';

const base = location.pathname.replace(/\/+$/, '');
const projectRoot = new URLSearchParams(location.search).get('project_root');

mount(App, { target: document.getElementById('app')!, props: { caller: new HttpOperationCaller(base, projectRoot) } });
