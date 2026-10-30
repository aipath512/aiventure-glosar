import re,sys,glob,json
R='repo/'
# surface form -> anchor (case-sensitive unless flagged)
LINKS=[
('CUI','c-cui',0),('EUID','c-euid',0),('CAEN','c-cod-caen',0),('ONRC','c-onrc',0),('ANAF','c-anaf',0),
('data.gov.ro','c-data-gov-ro',0),('OGL-ROU-1.0','c-ogl-rou-1-0',0),('SHA-256','c-sha-256',0),('OpenTimestamps','c-opentimestamps',0),
('JSON-LD','c-json-ld',0),('GEO','c-geo',0),('AEO','c-aeo',0),('AIO','c-aio',0),('A2A','c-a2a',0),('MCP','c-mcp',0),('RAG','c-rag',0),('HITL','c-hitl',0),
('RRVI','c-rrvi',0),('AI-LENS','c-ai-lens',0),('3WEBOBS','c-3webobs',0),('INJECTOR','c-injector',0),('Knowledge Graph','c-knowledge-graph',0),
('Vector Search','c-vector-search',0),('Vectorize','c-vectorize',0),('R2','c-r2',0),('D1','c-d1',0),('cardinalitate','c-cardinalitate',0),('cardinalități','c-cardinalitate',0),('Cardinalitate','c-cardinalitate',0),
('economic twins','c-economic-twins',1),('Economic twins','c-economic-twins',0),('dicționar de date','c-dictionar-de-date',1),('Dicționar de date','c-dictionar-de-date',0),('bilanț','c-bilant',0),('bilanțuri','c-bilant',0),('bilanțul','c-bilant',0),
('PFA','c-persoane-fizice',0),('Manifest','c-manifest',0),('manifest','c-manifest',0),
]
ids=set(re.findall(r' id="([^"]+)"',open(R+'glosar/index.html',encoding='utf-8').read()))
LINKS=[l for l in LINKS if l[1] in ids]; missing=set(x[1] for x in [('',k,0) for k in []])
# longest first
LINKS.sort(key=lambda l:-len(l[0]))
pat=re.compile('(?<![\\w\\-/.#])('+'|'.join(re.escape(l[0]) for l in LINKS)+')(?![\\w\\-])')
amap={l[0]:l[1] for l in LINKS}
BLOCK={'a','h1','h2','h3','h4','h5','h6','script','style','code','pre','nav','header','footer','button','summary','caption','title','head','textarea','svg','noscript','label','option','select','figcaption','kbd','samp','th','dt'}
SKIP_FILES={'glosar/index.html','resurse/glosar/index.html','utm/index.html'}
def process(html_):
    # restrict to <main>...</main> if present else body
    a=html_.find('<main'); 
    if a<0: a=html_.find('<body')
    if a<0: return html_,0
    b=html_.rfind('</main>'); b=len(html_) if b<0 else b
    head,mid,tail=html_[:a],html_[a:b],html_[b:]
    toks=re.split(r'(<!--.*?-->|<[^>]+>)',mid,flags=re.S)
    depth={k:0 for k in BLOCK}; done=set(); n=0
    for i,t in enumerate(toks):
        if t.startswith('<!--'): continue
        if t.startswith('<'):
            m=re.match(r'<(/?)([a-zA-Z0-9]+)',t)
            if m:
                tag=m.group(2).lower()
                if tag in BLOCK and not t.endswith('/>'):
                    depth[tag]+= -1 if m.group(1) else 1
                    if depth[tag]<0: depth[tag]=0
            continue
        if any(depth.values()) or not t.strip(): continue
        def rep(mm):
            nonlocal n
            w=mm.group(1); an=amap[w]
            if an in done: return w
            done.add(an); n+=1
            return f'<a href="/glosar/#{an}" class="gl">{w}</a>'
        toks[i]=pat.sub(rep,t)
    return head+''.join(toks)+tail,n
if __name__=='__main__':
    apply=len(sys.argv)>1 and sys.argv[1]=='apply'
    tot=0
    for f in sorted(glob.glob(R+'**/index.html',recursive=True)):
        rel=f[len(R):]
        if rel in SKIP_FILES: continue
        s=open(f,encoding='utf-8').read()
        if 'class="gl"' in s: continue
        s2,n=process(s)
        if n: tot+=n; print(rel,n)
        if apply and n: open(f,'w',encoding='utf-8').write(s2)
    print('total',tot)
