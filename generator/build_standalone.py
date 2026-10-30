"""Construiește paginile autonome /glosar/ și /dictionar/ (șabloane cu %%ORIGIN%% și %%DOMAIN%%)
din paginile etalon de pe firmsfinder.eu. Rulare: python3 generator/build_standalone.py <cale_repo_firmsfinder>"""
import re,sys,json,shutil,html,os
FF=sys.argv[1] if len(sys.argv)>1 else 'ff/repo'
OUT='public'
css=open(FF+'/onsite.css',encoding='utf-8').read()
EXTRA='.gl{text-decoration-style:dotted}nav.top{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:8px}.net{border:1px solid #f5c84238;border-radius:8px;padding:10px 14px;margin:12px 0;font-size:15px;color:#b9b5ab}article.term{border-bottom:1px solid #f5c84238;padding:14px 0}article.term h3{margin:0 0 6px}.idx{columns:2;list-style:none;padding:0}@media(max-width:600px){.idx{columns:1}}details>summary{margin:12px 0}td code{overflow-wrap:anywhere;word-break:break-all}footer small{color:#b9b5ab}'
LOCAL=('/glosar/','/dictionar/')
def absolutize(m):
    u=m.group(2)
    if u.startswith(LOCAL) or u.startswith('//'): return m.group(0)
    return m.group(1)+'https://firmsfinder.eu'+u+m.group(3)
def build(src,path,title,desc):
    s=open(FF+'/'+src+'/index.html',encoding='utf-8').read()
    ld=re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)
    g=json.loads(ld.group(1))
    for n in g['@graph']:
        n.pop('isPartOf',None); n.pop('publisher',None)
        if n.get('url'): n['url']=n['url'].replace('https://firmsfinder.eu','%%ORIGIN%%')
        if n.get('@id'): n['@id']=n['@id'].replace('https://firmsfinder.eu','%%ORIGIN%%')
        if n['@type'] in('WebPage',): n['isBasedOn']='https://firmsfinder.eu/'+path+'/'
        for k in ('hasDefinedTerm','distribution'):
            for t in n.get(k,[]):
                for kk in ('url','contentUrl'):
                    if kk in t: t[kk]=t[kk].replace('https://firmsfinder.eu','%%ORIGIN%%')
        if 'inDefinedTermSet' in n: pass
    ldj=json.dumps(g,ensure_ascii=False).replace('https://firmsfinder.eu/'+path+'/#set','%%ORIGIN%%/'+path+'/#set').replace('"inDefinedTermSet": "https://firmsfinder.eu','"inDefinedTermSet": "%%ORIGIN%%')
    ldj=ldj.replace('https://firmsfinder.eu/glosar/#set','%%ORIGIN%%/glosar/#set')
    main=s[s.find('</nav>',s.find('<main'))+6:s.find('<footer>')]
    main=re.sub(r'(href=")(/[^"#][^"]*|/)(")',absolutize,main)
    main=re.sub(r'(href=")/(")',r'\1https://firmsfinder.eu/\2',main)
    main=re.sub(r'<p aria-label="Breadcrumb">.*?</p>','',main,count=1,flags=re.S)
    head=(f'<!DOCTYPE html><html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{html.escape(title)}</title><link rel="canonical" href="%%ORIGIN%%/{path}/"><meta name="description" content="{html.escape(desc)}">'
      f'<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><meta property="og:type" content="website"><meta property="og:title" content="{html.escape(title)}">'
      f'<meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="%%ORIGIN%%/{path}/"><meta property="og:locale" content="ro_RO"><meta name="author" content="AiVenture S.R.L.">'
      f'<meta name="theme-color" content="#050505"><script type="application/ld+json">{ldj}</script><style>{css}{EXTRA}</style></head>')
    body=('<body><main><nav class="top" aria-label="Navigație"><a href="/">Acasă</a><a href="/glosar/">Glosar</a><a href="/dictionar/">Dicționar</a><a href="/legal/">Legal</a></nav>'
      f'<p class="net">Pagină comună a rețelei de site-uri AiVenture. Sursă unică: <a href="https://github.com/aipath512/aiventure-glosar" rel="noopener">aiventure-glosar</a>; etalon: <a href="https://firmsfinder.eu/{path}/" rel="noopener">firmsfinder.eu/{path}/</a>. Domeniu: %%DOMAIN%%.</p>'
      +main+'<footer><small>AiVenture S.R.L. · pagină servită pe %%DOMAIN%% · <a href="https://firmsfinder.eu/dictionar/">dicționar</a> · <a href="https://firmsfinder.eu/glosar/">glosar</a></small></footer></main></body></html>')
    os.makedirs(f'{OUT}/{path}',exist_ok=True)
    open(f'{OUT}/{path}/index.html','w',encoding='utf-8').write(head+body)
t=lambda f: re.search(r'<title>(.*?)</title>',open(FF+'/'+f+'/index.html',encoding='utf-8').read()).group(1).replace('| FirmsFinder AI','| AiVenture')
d=lambda f: re.search(r'<meta name="description" content="(.*?)"',open(FF+'/'+f+'/index.html',encoding='utf-8').read()).group(1)
build('glosar','glosar',t('glosar'),d('glosar'))
build('dictionar','dictionar',t('dictionar'),d('dictionar'))
# fișiere de verificare ale dicționarului
for f in os.listdir('dictionar'):
    p='dictionar/'+f
    if os.path.isfile(p): shutil.copy(p,f'{OUT}/dictionar/{f}')
if os.path.isdir('dictionar/context'):
    shutil.copytree('dictionar/context',f'{OUT}/dictionar/context',dirs_exist_ok=True)
print('ok')
