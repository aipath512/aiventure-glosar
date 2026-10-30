// aiventure-glosar v1.0 (2026-10-30, sesiunea 0008C)
// Servește /glosar/ și /dictionar/ (+ fișierele de verificare) pe fiecare domeniu al rețelei AiVenture
// din aceleași fișiere (folderul public/, Workers Static Assets). Un domeniu primește paginile doar dacă
// are rută către acest Worker (vezi wrangler.jsonc). Rutele sunt pe căi, deci nu intră în conflict cu
// Workerii existenți (aiventure-footer, aiventure-gdpr, aiventure-legal-worker), care au rute pe domeniu/*.
const PAGES = ['/glosar/', '/dictionar/'];

function isTemplate(path) {
  return PAGES.includes(path);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let path = url.pathname;
    if (request.method !== 'GET' && request.method !== 'HEAD') return fetch(request);
    // /glosar și /dictionar fără slash final -> 301 la varianta cu slash
    if (path === '/glosar' || path === '/dictionar') {
      return Response.redirect(url.origin + path + '/' + url.search, 301);
    }
    const known = path.startsWith('/glosar/') || path.startsWith('/dictionar/');
    if (!known) return fetch(request); // în afara căilor noastre: trecem mai departe spre origine
    const assetUrl = new URL(request.url);
    assetUrl.pathname = isTemplate(path) ? path + 'index.html' : path;
    const res = await env.ASSETS.fetch(new Request(assetUrl, request));
    if (res.status === 404) return fetch(request);
    const h = new Headers(res.headers);
    h.set('x-aiventure-glosar', '1.0');
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
