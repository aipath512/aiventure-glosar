// aiventure-glosar v1.2 (2026-10-30, sesiunea 0008C) — v1.2: linkuri automate la edge (legaturi.json); v1.1: corectat redirect 307
// Servește /glosar/ și /dictionar/ (+ fișierele de verificare) pe fiecare domeniu al rețelei AiVenture
// din aceleași fișiere (folderul public/, Workers Static Assets). Un domeniu primește paginile doar dacă
// are rută către acest Worker (vezi wrangler.jsonc). Rutele sunt pe căi, deci nu intră în conflict cu
// Workerii existenți (aiventure-footer, aiventure-gdpr, aiventure-legal-worker), care au rute pe domeniu/*.
import cfg from './legaturi.json' with { type: 'json' };
import { buildRules, autolink } from './autolink.js';

const PAGES = ['/glosar/', '/dictionar/'];

// Trece cererea spre origine și, pe paginile HTML ale domeniilor din legaturi.json, adaugă linkurile automate.
async function passthrough(request, url) {
  const res = await fetch(request);
  try {
    if (request.method !== 'GET' || res.status !== 200) return res;
    const ct = res.headers.get('content-type') || '';
    if (!ct.includes('text/html')) return res;
    if (cfg.exclude_cai.some((p) => url.pathname.startsWith(p)) || url.searchParams.has('nolinks')) return res;
    const rules = buildRules(cfg, url.hostname);
    if (!rules) return res;
    const html = await res.clone().text();
    if (html.includes('class="gl"')) return res; // deja legat static (ex. firmsfinder.eu)
    const out = autolink(html, rules);
    if (out === html) return res;
    const h = new Headers(res.headers);
    h.delete('content-length');
    h.set('x-aiventure-links', '1');
    return new Response(out, { status: res.status, statusText: res.statusText, headers: h });
  } catch (e) {
    return res; // în caz de eroare, pagina originală rămâne neatinsă
  }
}

function isTemplate(path) {
  return PAGES.includes(path);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let path = url.pathname;
    if (request.method !== 'GET' && request.method !== 'HEAD') return fetch(request);
    // (redirect-ul și paginile proprii sunt tratate mai jos)
    // /glosar și /dictionar fără slash final -> 301 la varianta cu slash
    if (path === '/glosar' || path === '/dictionar') {
      return Response.redirect(url.origin + path + '/' + url.search, 301);
    }
    const known = path.startsWith('/glosar/') || path.startsWith('/dictionar/');
    if (!known) return passthrough(request, url); // în afara căilor noastre: origine + linkuri automate
    const assetUrl = new URL(request.url);
    // Workers Static Assets rezolvă singur /glosar/ -> public/glosar/index.html (cerere pe index.html ar da redirect 307)
    const res = await env.ASSETS.fetch(new Request(assetUrl, request));
    if (res.status !== 200) return fetch(request); // 404, redirect sau altceva: trecem spre origine, nu servim corp gol
    const h = new Headers(res.headers);
    h.set('x-aiventure-glosar', '1.2');
    if (isTemplate(path)) {
      let html = await res.text();
      html = html.replaceAll('%%ORIGIN%%', url.origin).replaceAll('%%DOMAIN%%', url.hostname);
      h.set('content-type', 'text/html; charset=utf-8');
      h.set('cache-control', 'public, max-age=300');
      h.delete('content-length');
      return new Response(request.method === 'HEAD' ? null : html, { status: 200, headers: h });
    }
    if (path.endsWith('.json')) h.set('content-type', 'application/json; charset=utf-8');
    else if (path.endsWith('.md') || path.endsWith('.txt')) h.set('content-type', 'text/plain; charset=utf-8');
    h.set('access-control-allow-origin', '*');
    return new Response(res.body, { status: res.status, headers: h });
  },
};
