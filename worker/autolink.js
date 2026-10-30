// aiventure-glosar v1.2 — linkuri automate la edge (termeni -> glosar; subiecte -> site-ul proprietar din rețea)
const BLOCK = new Set(['a','h1','h2','h3','h4','h5','h6','script','style','code','pre','nav','header','footer','button','summary','caption','title','head','textarea','svg','noscript','label','option','select','figcaption','kbd','samp','th','dt','iframe','template']);
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

export function buildRules(cfg, hostname) {
  const d = cfg.domenii[hostname];
  if (!d) return null;
  const rules = [];
  if (d.retea) for (const r of cfg.retea) if (r.d !== hostname) rules.push({ t: r.t, key: 'n:' + r.d, href: r.u, kind: 'retea' });
  const owned = new Set(cfg.retea.filter((r) => r.d === hostname).map((r) => r.t));
  if (d.glosar) for (const g of cfg.glosar) rules.push({ t: g.t, key: 'g:' + g.a, href: '/glosar/#' + g.a, kind: 'glosar' });
  if (!rules.length) return null;
  const map = new Map();
  for (const r of rules) if (!map.has(r.t)) map.set(r.t, r); // reteaua are prioritate (e prima în listă)
  const forms = [...map.keys()].sort((a, b) => b.length - a.length).map(esc);
  const pat = new RegExp('(?<![\\p{L}\\p{N}_\\-/.#@])(' + forms.join('|') + ')(?![\\p{L}\\p{N}_\\-])', 'gu');
  return { map, pat, lim: cfg.limite };
}

export function autolink(html, rules) {
  const { map, pat, lim } = rules;
  const depth = {};
  const done = new Set();
  let nG = 0, nR = 0, out = '', i = 0, started = false;
  const n = html.length;
  const blocked = () => { for (const k in depth) if (depth[k] > 0) return true; return false; };
  while (i < n) {
    const lt = html.indexOf('<', i);
    const text = html.slice(i, lt < 0 ? n : lt);
    if (text) {
      if (started && !blocked() && text.trim()) {
        out += text.replace(rules.pat, (w) => {
          const r = map.get(w);
          if (!r || done.has(r.key)) return w;
          if (r.kind === 'glosar' && nG >= lim.glosar) return w;
          if (r.kind === 'retea' && nR >= lim.retea) return w;
          done.add(r.key);
          if (r.kind === 'glosar') nG++; else nR++;
          return '<a href="' + r.href + '" class="gl">' + w + '</a>';
        });
      } else out += text;
    }
    if (lt < 0) break;
    if (html.startsWith('<!--', lt)) { const e = html.indexOf('-->', lt); const end = e < 0 ? n : e + 3; out += html.slice(lt, end); i = end; continue; }
    const m = /^<(script|style)\b/i.exec(html.slice(lt, lt + 10));
    if (m) { const close = html.toLowerCase().indexOf('</' + m[1].toLowerCase(), lt); let end = close < 0 ? n : html.indexOf('>', close) + 1; if (end <= 0) end = n; out += html.slice(lt, end); i = end; continue; }
    const gt = html.indexOf('>', lt);
    const end = gt < 0 ? n : gt + 1;
    const tag = html.slice(lt, end);
    out += tag; i = end;
    const tm = /^<(\/?)([a-zA-Z][a-zA-Z0-9-]*)/.exec(tag);
    if (tm) {
      const name = tm[2].toLowerCase();
      if ((name === 'main' || name === 'body') && !tm[1]) started = true;
      if (BLOCK.has(name) && !tag.endsWith('/>')) { depth[name] = Math.max(0, (depth[name] || 0) + (tm[1] ? -1 : 1)); }
    }
  }
  return out;
}
