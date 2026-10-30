import json,re,html,unicodedata
R='repo/'
e=lambda x: html.escape(str(x if x is not None else ''),quote=False)
def slug(t):
    t=unicodedata.normalize('NFKD',t.lower()); t=''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+','-',t).strip('-')
d=json.load(open(R+'dictionar/dictionar-economic-firme_v1.0.2_2026-10-29.json',encoding='utf-8'))
old=open(R+'resurse/glosar/index.html',encoding='utf-8').read()
STARE={'in_uz':'în uz','planificat':'planificat','verificat':'verificat','partial_verificat':'parțial verificat','de_verificat':'de verificat','existent':'existent'}
st=lambda s: STARE.get(s,s)
# ---- concepts from old glossary
concepts=[]
for m in re.finditer(r'<article class="term" id="t-([^"]+)"[^>]*><h3>(.*?)</h3>(.*?)</article>',old,re.S):
    id_,h3,body=m.groups()
    name=re.sub(r'<small>.*?</small>','',h3).strip(); cat=(re.search(r'<small>(.*?)</small>',h3) or [None,''])[1]
    def grab(label):
        x=re.search(r'<strong>'+label+r'[^<]*</strong>\s*(.*?)</p>',body,re.S)
        return x.group(1).strip() if x else ''
    short=re.search(r'<p class="short"><strong>Pe scurt\.</strong>\s*(.*?)</p>',body,re.S)
    defn=re.search(r'<strong>Definiția din site\.</strong>\s*(.*?)(?:<span class="src">|</p>)',body,re.S)
    fix=lambda x: re.sub(r'href="#(cuvinte-cheie|intents|pagini|retea|index)"',lambda m:'href="/resurse/glosar/#'+m.group(1)+'"',x.replace('href="#t-','href="#c-'))
    concepts.append(dict(id=id_,name=name,cat=cat,short=fix(short.group(1)) if short else '',defn=fix(defn.group(1).strip()) if defn else '',alt=re.sub(r'<[^>]+>','',grab('Alte denumiri')).rstrip('.'),warn=re.sub(r'<[^>]+>','',grab('Nu confundați cu')).strip().rstrip('.')))
cmap={c['name'].lower():c for c in concepts}
OLD='/resurse/glosar/'
# ---- hand-written technical terms
T=[
('cui','CUI','Identificare','Codul Unic de Identificare al unei firme în România; numărul sub care firma este cunoscută la ONRC, ANAF și MF.','În FirmsFinder, CUI este cheia comună a tuturor datelor despre o firmă: ONRC, bilanțuri MF, situația fiscală. Fără CUI propriu (de exemplu sucursale), firma se identifică prin codul de înmatriculare.',['cod de înmatriculare','EUID','Firmă']),
('euid','EUID','Identificare','Identificatorul european unic al unei firme din registrele comerțului ale statelor membre UE (format ROONRC.J…).','Folosit ca cheie alternativă; se rezolvă în D1 către CUI.',['CUI','cod de înmatriculare']),
('cod-de-inmatriculare','Cod de înmatriculare','Identificare','Numărul din registrul comerțului al unei firme, în formatul J<județ>/<număr>/<an>.','În dicționar este proprietatea cod_inmatriculare a entității FIRMA; sucursalele fără CUI propriu se identifică prin el.',['CUI','EUID']),
('onrc','ONRC','Sursă oficială','Oficiul Național al Registrului Comerțului, instituția care ține registrul firmelor din România.','Sursa identității juridice a firmei: denumire, sediu, formă juridică, stare, data înmatriculării, CAEN autorizate. Date preluate de pe data.gov.ro.',['SRC-0001','Date oficiale']),
('mf','MF (Ministerul Finanțelor)','Sursă oficială','Ministerul Finanțelor, care publică situațiile financiare anuale ale firmelor.','În FirmsFinder: bilanțuri 2023–2025, 20 de indicatori pe firmă și an, pe CUI.',['Bilanț','CUI']),
('anaf','ANAF','Sursă oficială','Agenția Națională de Administrare Fiscală.','Surse evaluate: registrul plătitorilor de TVA, e-Factura, bilanț pe CUI și restanțieri. Starea fiecăreia este în registrul de pe pagina Surse.',['Registrul surselor']),
('data-gov-ro','data.gov.ro','Sursă oficială','Portalul național de date deschise, de unde se descarcă seturile ONRC și MF.','Seturile sunt publicate sub licența OGL-ROU-1.0, cu atribuirea „Sursa: ONRC / MF, data.gov.ro”.',['OGL-ROU-1.0','ONRC','MF (Ministerul Finanțelor)']),
('ogl-rou-1-0','OGL-ROU-1.0','Licență','Licența guvernamentală deschisă din România, sub care sunt publicate datele de pe data.gov.ro.','Permite refolosirea cu atribuire a sursei.',['data.gov.ro']),
('bilant','Bilanț (situație financiară)','Date financiare','Situația financiară anuală depusă de o firmă la MF, cu indicatori precum cifra de afaceri, profit, active.','În model este entitatea SITUATIE_FINANCIARA: un record per CUI și an (ENT-00000005). Un bilanț corectat înlocuiește doar anul respectiv.',['SITUATIE_FINANCIARA','CUI']),
('sesiune','Sesiune de lucru','Versionare','Unitate de lucru numerotată NNNN + literă: C = sesiune curentă, H = comună înghețată, T = test (de exemplu 0008C, 0008H).','Fișierele se creează noi la fiecare sesiune și nu se rescriu. Entitatea SESIUNE din dicționar leagă versiunile, amprentele și dovezile.',['SESIUNE','Dicționar de date']),
('decizie-ent','Decizie ENT-nnnnnnnn','Versionare','Număr de ordine al unei decizii înregistrate, cu opt cifre (de exemplu ENT-00000005), dată de Dan Ionescu prin „Adjudecat”.','Atenție la nume: ID-urile de entități din dicționar (ENT-000001…ENT-000018) au șase cifre și sunt altceva decât deciziile cu opt cifre.',['Dicționar de date','Sesiune de lucru']),
('dictionar-de-date','Dicționar de date','Model','Documentul înghețat pe versiune care descrie entitățile, proprietățile, relațiile, sursele și regulile de conflict ale bazei FirmsFinder.','Versiunea curentă este 1.0.2. Nu se modifică după publicare: o schimbare este o versiune nouă, cu SHA-256 și OpenTimestamps.',['Entități','Relații','SHA-256']),
('r2','R2','Infrastructură','Stocarea de obiecte Cloudflare R2; în FirmsFinder, păstrează datele primare ca fișiere imutabile versionate pe sesiune.','R2 este sursa de adevăr; D1 și Vectorize se pot reconstrui din R2.',['D1','Vectorize']),
('d1','D1','Infrastructură','Baza de date SQL Cloudflare D1; în FirmsFinder este indexul care spune în ce fișier și la ce octet se află un record.','Funcționează ca un KSDS: cheia (CUI) duce la poziția din R2, citită prin Range GET. Poate fi reconstruită din R2.',['R2','Vectorize']),
('vectorize','Vectorize','Infrastructură','Indexul vectorial Cloudflare folosit pentru căutarea semantică după sens.','Toate căile de acces (cheie, SQL, semantic) ajung la același CUI.',['R2','D1','Căutare semantică']),
('manifest','Manifest','Integritate','Fișier care listează fișierele preluate într-o rulare a robotului, cu SHA-256 și două horodatări; primește un singur OpenTimestamps.','Dovedește integritatea și existența copiei la acea dată, nu că sursa a publicat exact acel conținut (ENT-00000007).',['SHA-256','OpenTimestamps']),
('tip-record','tip_record','Model','Câmp prezent în fiecare record, care spune ce fel de record este (FIRMA, BILANT, CAEN, ANAF_TVA etc.).','Unul dintre cei patru invarianți din ENT-00000009.',['Decizie ENT-nnnnnnnn']),
('caen-mf','caen_mf','Model','Codul CAEN din bilanțul MF; filtrul de activitate folosește caen_mf când există, nu CAEN-ul autorizat de ONRC.','Regula de conflict „activitate”: activitatea reală rezultă din bilanț.',['Cod CAEN']),
('economic-twins','Economic twins','Concept','Firme cu profil economic asemănător cu al unei firme date, găsite pe baza datelor fiscale și vectoriale.','Folosit pentru a descoperi firme similare, încă neabordate, nu pentru contactare automată.',['Potrivire economică','Vectorize']),
('top','top','Model','Câmp care decide dacă o firmă se afișează public: 1 implicit; 0 pentru PFA, II, IF.','Persoanele fizice rămân în bază, dar nu se afișează public, iar numele se maschează după acordul GDPR.',['Persoane fizice']),
('persoane-fizice','Persoane fizice (PFA, II, IF, PF, AF)','Protecția datelor','Firme care sunt persoane fizice autorizate sau întreprinderi individuale/familiale.','Rămân în bază cu top=0; nu se afișează public; identificare doar la cerere pe contact@5thelement.ai.',['top']),
('registrul-surselor','Registrul surselor','Surse','Tabelul public al surselor oficiale evaluate, cu cum se preiau, starea la data verificării și link.','Se află pe pagina Surse; este actualizat separat de dicționar și poate arăta o stare mai nouă.',['Surse']),
]
techs=[dict(id=a,name=b,cat=c,short=dfn,defn=ext,alt='',see=sv) for a,b,c,dfn,ext,sv in T]
# ---- entities, relations
ents={x['nume']:x for x in d['entitati']}
props={}
for p in d['proprietati']: props.setdefault(p['entitate'],[]).append(p)
rels=d['relatii']
def eid(n): return 'ent-'+slug(n)
def rid(r): return 'rel-'+slug(r['id'])
def ra(n): return 'orice entitate' if n=='*' else f'<a href="#{eid(n)}">{e(n)}</a>'
out_rel={};in_rel={}
for r in rels:
    out_rel.setdefault(r['sursa'],[]).append(r); in_rel.setdefault(r['tinta'],[]).append(r)
CARD={'1':'exact una','0..1':'zero sau una','0..*':'oricâte, inclusiv zero','1..*':'cel puțin una'}
def card_text(c): return f'<code>{e(c)}</code> ({CARD.get(c,c)})'
# ---- sections
def sec_entities():
    h=[]
    for n,x in ents.items():
        ps=props.get(n,[])
        pl=', '.join(f'<code>{e(p["nume"])}</code>' for p in ps)
        o=''.join(f'<li><a href="#{rid(r)}">{e(r["nume"])}</a> → {ra(r["tinta"])} · cardinalitate direct {card_text(r["card_direct"])}, invers {card_text(r["card_invers"])}</li>' for r in out_rel.get(n,[]))
        i=''.join(f'<li>{ra(r["sursa"])} — <a href="#{rid(r)}">{e(r["nume"])}</a> → această entitate · cardinalitate direct {card_text(r["card_direct"])}, invers {card_text(r["card_invers"])}</li>' for r in in_rel.get(n,[]))
        h.append(f'<article class="term" id="{eid(n)}"><h3>{e(n)} <small>entitate · {e(x["tip"])} · {e(x["id"])}</small></h3>'
          f'<p><strong>Definiție.</strong> {e(x["descriere"])}</p>'
          f'<p><strong>Identificator (cheie):</strong> {" + ".join("<code>"+e(k)+"</code>" for k in x["cheie"])} · <strong>Stare:</strong> {e(st(x["stare"]))} · <strong>ID dicționar:</strong> <code>{e(x["id"])}</code></p>'
          f'<p><strong>Proprietăți ({len(ps)}):</strong> {pl or "—"}. Detalii: <a href="/dictionar/#proprietati">Dicționar, proprietăți pe entitate</a>.</p>'
          +(f'<p><strong>Relații pornind de aici:</strong></p><ul>{o}</ul>' if o else '')
          +(f'<p><strong>Relații care ajung aici:</strong></p><ul>{i}</ul>' if i else '')+'</article>')
    return ''.join(h)
def sec_rels():
    h=[]
    for r in rels:
        at=', '.join(f'<code>{e(a)}</code>' for a in r.get('atribute',[]))
        h.append(f'<article class="term" id="{rid(r)}"><h3>{e(r["nume"])} <small>relație · {e(r["id"])}</small></h3>'
          f'<p><strong>Se citește:</strong> {ra(r["sursa"])} — {e(r["nume"])} → {ra(r["tinta"])}. <strong>Inversa:</strong> {ra(r["tinta"])} — {e(r["inversa"])} → {ra(r["sursa"])}.</p>'
          f'<p><strong>Cardinalitate:</strong> direct {card_text(r["card_direct"])}; invers {card_text(r["card_invers"])}. <a href="#c-cardinalitate">Ce este cardinalitatea?</a></p>'
          f'<p><strong>Definiție.</strong> {e(r["descriere"])}</p>'
          +(f'<p><strong>Atribute ale relației:</strong> {at}</p>' if at else '')
          +f'<p><strong>Stare:</strong> {e(st(r["stare"]))}</p></article>')
    return ''.join(h)
def sec_sources():
    h=[]
    for s in d['surse']:
        h.append(f'<article class="term" id="src-{slug(s["id"])}"><h3>{e(s["nume"])} <small>sursă · {e(s["id"])}</small></h3>'
          f'<p><strong>Publicator:</strong> {e(s["publicator"])} · <strong>Cum se preia:</strong> {e(s["metoda"])} · <strong>Frecvență:</strong> {e(s["frecventa"])} · <strong>Stare:</strong> {e(st(s["stare"]))} (verificat {e(s["verificat_in"])})</p>'
          f'<p><strong>Acces/licență:</strong> {e(s["licenta_acces"])}. <strong>Limite:</strong> {e(s["limite"])}</p>'
          +(f'<p>{e(s["nota"])}</p>' if s.get('nota') else '')
          +(f'<p><a href="{e(s["url"])}" rel="noopener">{e(s["url"])}</a></p>' if s.get('url') else '')+'</article>')
    return ''.join(h)
techlinks={}  # name->slug for see-also resolution
allterms=[]  # (id,name,kind)
for t in techs: allterms.append(('c-'+t['id'],t['name']))
for c in concepts: allterms.append(('c-'+c['id'],c['name']))
for n in ents: allterms.append((eid(n),n))
for r in rels: allterms.append((rid(r),r['nume']))
for s in d['surse']: allterms.append(('src-'+slug(s['id']),s['id']+' '+s['nume']))
lookup={}
for i,n in allterms: lookup.setdefault(n.lower(),i)
def seelinks(names):
    o=[]
    for n in names:
        i=lookup.get(n.lower()) or lookup.get(n.lower().replace('_',' '))
        o.append(f'<a href="#{i}">{e(n)}</a>' if i else e(n))
    return ' · '.join(o)
def sec_concepts():
    h=[]
    # technical first, then old
    for t in techs:
        h.append(f'<article class="term" id="c-{t["id"]}"><h3>{e(t["name"])} <small>{e(t["cat"])}</small></h3><p class="short"><strong>Pe scurt.</strong> {e(t["short"])}</p><p><strong>Cum se folosește în FirmsFinder.</strong> {e(t["defn"])}</p><p><strong>Vezi și:</strong> {seelinks(t["see"])}</p></article>')
    for c in concepts:
        extra=''
        if c['name'].lower()=='cardinalitate':
            extra='<p><strong>Valori folosite în dicționar:</strong> '+' · '.join(f'<code>{k}</code> = {v}' for k,v in CARD.items())+'. Se dă pentru ambele sensuri ale relației.</p><p><strong>Relații cu cardinalități:</strong> <a href="#relatii">vezi lista relațiilor</a>.</p>'
        if c['name'].lower()=='firmă':
            extra=f'<p><strong>În model:</strong> entitatea {ra("FIRMA")}, cheie CUI.</p>'
        h.append(f'<article class="term" id="c-{c["id"]}"><h3>{c["name"]} <small>{e(c["cat"])}</small></h3><p class="short"><strong>Pe scurt.</strong> {c["short"]}</p><p><strong>Definiția din site.</strong> {c["defn"]}</p>'
           +(f'<p><strong>Alte denumiri:</strong> {e(c["alt"])}.</p>' if c['alt'] else '')
           +(f'<p><strong>Nu confundați cu:</strong> {e(c["warn"])}.</p>' if c['warn'] else '')+extra+f'<p><small>Explicație completă, cu exemple: <a href="{OLD}#t-{c["id"]}">glosarul pentru începători</a>.</small></p></article>')
    return ''.join(h)
body_sections=[
 ('concepte','Termeni și concepte',f'<p>{len(techs)+len(concepts)} de termeni folosiți pe site: identificatori, surse oficiale, infrastructură, integritate și concepte de căutare, AI și vizibilitate. Termenii din glosarul pentru începători sunt aici cu definiția lor; explicația lungă rămâne în glosarul pentru începători.</p>',sec_concepts()),
 ('entitati','Entități',f'<p>{len(ents)} de entități din <a href="/dictionar/">dicționarul de date</a> v1.0.2. O entitate este un tip de obiect despre care păstrăm date. Cheia identifică un exemplar (pentru firmă, CUI).</p>',sec_entities()),
 ('relatii','Relații și cardinalități',f'<p>{len(rels)} relații. Cardinalitatea răspunde la întrebarea „câte?”, pentru ambele sensuri: <code>1</code> exact una, <code>0..1</code> zero sau una, <code>0..*</code> oricâte, <code>1..*</code> cel puțin una.</p>',sec_rels()),
 ('surse','Surse',f'<p>{len(d["surse"])} de surse din dicționar, cu starea la 29.10.2026. Registrul actual este pe pagina <a href="/surse/#registru">Surse și metodologie</a>.</p>',sec_sources()),
]
# ---- index A-Z
idx=sorted(allterms,key=lambda t: slug(t[1]))
az='<ul class="idx">'+''.join(f'<li><a href="#{i}">{e(n)}</a></li>' for i,n in idx)+'</ul>'
# ---- page
dic=open(R+'dictionar/index.html',encoding='utf-8').read()
head=dic[:dic.find('<body')]
TITLE='Glosar de termeni, entități și relații | FirmsFinder AI'
DESC=f'Glosar unic FirmsFinder: {len(allterms)} de termeni cu definiții, cele {len(ents)} entități, {len(rels)} relații cu cardinalități și {len(d["surse"])} surse; fiecare termen are un link stabil.'
head=head.replace('Dicționar de date economice ale firmelor | FirmsFinder AI',TITLE)
head=head.replace('https://firmsfinder.eu/dictionar/','https://firmsfinder.eu/glosar/')
head=re.sub(r'Dicționarul de date FirmsFinder v1\.0\.2: [^"]*?OpenTimestamps\.',DESC,head)
head=head.replace('tip: Referință / dicționar de date','tip: Referință / glosar')
ld={"@context":"https://schema.org","@graph":[{"@type":"WebPage","@id":"https://firmsfinder.eu/glosar/#webpage","url":"https://firmsfinder.eu/glosar/","name":TITLE,"description":DESC,"inLanguage":"ro","isPartOf":{"@id":"https://firmsfinder.eu/#website"},"publisher":{"@id":"https://aiventure.ro/#organization"},"dateModified":"2026-10-30"},
 {"@type":"DefinedTermSet","@id":"https://firmsfinder.eu/glosar/#set","name":"Glosar FirmsFinder","url":"https://firmsfinder.eu/glosar/","inLanguage":"ro","hasDefinedTerm":[{"@type":"DefinedTerm","name":n,"url":"https://firmsfinder.eu/glosar/#"+i,"inDefinedTermSet":"https://firmsfinder.eu/glosar/#set"} for i,n in allterms]}]}
head=re.sub(r'<script type="application/ld\+json">.*?</script>','<script type="application/ld+json">\n'+json.dumps(ld,ensure_ascii=False,indent=1)+'\n</script>',head,count=1,flags=re.S)
nav=re.search(r'<nav aria-label="Navigație">.*?</nav>',dic,re.S).group(0).replace('<a href="/dictionar/">Dicționar</a>','<a href="/dictionar/">Dicționar</a><a href="/glosar/">Glosar</a>')
foot=dic[dic.find('<footer>'):]
sec_html=''.join(f'<section id="{i}"><h2>{t}</h2>{intro}{b}</section>' for i,t,intro,b in body_sections)
cuprins='<section id="cuprins"><h2>Pe această pagină</h2><ul>'+''.join(f'<li><a href="#{i}">{t}</a></li>' for i,t,_,_ in body_sections)+'<li><a href="#index">Index A–Z</a></li></ul></section>'
page=(head+'<body><main>'+nav+'<p aria-label="Breadcrumb"><a href="/">Acasă</a> / Glosar</p><h1>Glosar de termeni, entități și relații</h1>'
 f'<p>Un singur loc pentru toți termenii folosiți pe site: ce înseamnă, cum se leagă între ei și de unde vin. Fiecare termen are un link stabil (de exemplu <code>/glosar/#ent-firma</code>); pe celelalte pagini, prima apariție a termenului trimite aici. Entitățile, relațiile și sursele vin din <a href="/dictionar/">dicționarul de date</a> v1.0.2 (înghețat 2026-10-29), deci nu se pot abate de el.</p>'
 '<p><small>Glosarul pentru începători, cu exemple, cuvinte-cheie și intenții, rămâne la <a href="'+OLD+'">Resurse, glosar</a>.</small></p>'
 +cuprins+sec_html+'<section id="index"><h2>Index A–Z</h2>'+az+'</section>'+foot)
open('glosar-index_v1.0_2026-10-30.html','w',encoding='utf-8').write(page)
json.dump({'allterms':allterms},open('glosar_terms.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(page),len(allterms),len(concepts),len(techs))
