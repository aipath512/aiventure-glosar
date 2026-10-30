import json,re,html
R='repo/'
d=json.load(open(R+'dictionar/dictionar-economic-firme_v1.0.2_2026-10-29.json',encoding='utf-8'))
reg=json.load(open(R+'sesiuni/registru-sesiuni.json',encoding='utf-8'))
latest=json.load(open(R+'dictionar/latest.json',encoding='utf-8'))
e=lambda x: html.escape(str(x if x is not None else ''),quote=False)
def a(u,t=None): return f'<a href="{html.escape(u)}" rel="noopener">{e(t or u)}</a>'
def tbl(cap,heads,rows):
    return f'<table><caption>{e(cap)}</caption><thead><tr>'+''.join(f'<th scope="col">{e(h)}</th>' for h in heads)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table>'
STARE={'in_uz':'în uz','planificat':'planificat','verificat':'verificat','partial_verificat':'parțial verificat','de_verificat':'de verificat','existent':'existent'}
st=lambda s: e(STARE.get(s,s))
sesiuni={s['sesiune']:s for s in reg['sesiuni']}
ses=sesiuni['0008H']; ses_prev=sesiuni['0007H']
# files
def files_rows(s):
    out=[]
    for f in s['fisiere']:
        n=f['cale'].split('/')[-1]
        ots_state={'confirmat_bitcoin':'confirmat în Bitcoin la '+f.get('ots_confirmat_la','')[:10]}.get(f.get('ots_stare'),f.get('ots_stare',''))
        out.append((a('/'+f['cale'],n),f'<code>{f["sha256"]}</code>',a('/'+f['ots'],'.ots')+'<br><small>'+e(ots_state)+'</small>'))
    return out
heads=['Fișier','SHA-256','Dovadă OpenTimestamps']
stat=d['statistici']
ent=[(f'<code>{e(x["id"])}</code>',f'<strong>{e(x["nume"])}</strong>',e(x['tip']),e(', '.join(x.get('cheie',[]) or [])),st(x['stare']),e(x['descriere'])) for x in d['entitati']]
rel=[(f'<code>{e(x["id"])}</code>',f'{e(x["sursa"])} — {e(x["nume"])} → {e(x["tinta"])}',f'{e(x["tinta"])} — {e(x["inversa"])} → {e(x["sursa"])}',f'{e(x["card_direct"])} / {e(x["card_invers"])}',st(x['stare']),e(x['descriere'])) for x in d['relatii']]
src=[]
for x in d['surse']:
    u=x.get('url') or ''
    link=a(u,u.replace('https://','').replace('http://','').rstrip('/')[:48]) if u.startswith('http') else '—'
    src.append((f'<code>{e(x["id"])}</code>',f'<strong>{e(x["nume"])}</strong>',link,e(x.get('metoda','')),e(x.get('frecventa','')),e(x.get('licenta_acces','')),e(x.get('limite','')),st(x['stare'])))
conf=[(e(c['grup']),e(c['castiga'] or 'nu se alege o sursă'),e(c.get('nota',''))) for c in d['reguli_conflict'] if 'grup' in c]
regula_conf=''.join(e(c['regula']) for c in d['reguli_conflict'] if 'regula' in c)
pol=''.join(f'<li><strong>{e(p["nume"])}</strong>: {e(p["text"])}</li>' for p in d['politici'])
dec=''.join(f'<li>{e(x)}</li>' for x in d['decizii_deschise'])
ist=''.join(f'<li><strong>v{e(x["versiune"])}</strong> ({e(x["data"])}): {e(x["text"])}</li>' for x in d['istoric'])
vz=d['versionare']
body=f'''<h1>Dicționar de date economice ale firmelor</h1>
<p>Dicționarul descrie ce informații păstrează FirmsFinder despre fiecare firmă: ce entități există, ce proprietăți are fiecare, cum se leagă între ele, de unde vine fiecare dată și cum se rezolvă conflictele dintre surse. Versiunea curentă este <strong>{e(d["versiune"])}</strong>, înghețată la {e(ses["inghetata_la"][:10])}, în sesiunea <strong>{e(ses["sesiune"])}</strong>. O versiune publicată nu se modifică: orice schimbare este o versiune nouă, cu fișiere noi.</p>
<p>Starea fiecărui element arată ce există efectiv: „în uz” înseamnă că datele sunt în baza FirmsFinder, „planificat” că elementul este doar definit. Un element „planificat” nu dovedește că este implementat.</p>
<section id="cuprins"><h2>Pe această pagină</h2><ul><li><a href="#fisiere">Fișierele și verificarea lor</a></li><li><a href="#entitati">Entități</a></li><li><a href="#relatii">Relații și cardinalități</a></li><li><a href="#surse">Surse</a></li><li><a href="#reguli">Reguli de conflict și politici</a></li><li><a href="#deschise">Decizii deschise</a></li><li><a href="#istoric">Istoric versiuni</a></li></ul></section>
<section id="cifre"><h2>În cifre</h2>{tbl("Dicționar v"+d["versiune"],["Element","Număr"],[("Entități",e(stat["entitati"])),("Proprietăți",f'{e(stat["proprietati"])} (din care {e(stat["proprietati_existente"])} existente)'),("Relații",e(stat["relatii"])),("Surse",e(stat["surse"]))])}<p class="muted"><small>Lista completă a celor {e(stat["proprietati"])} de proprietăți este în fișierul {a("/dictionar/dictionar-economic-firme_v1.0.2_2026-10-29.md","Markdown")} și în {a("/dictionar/dictionar-economic-firme_v1.0.2_2026-10-29.json","JSON")}.</small></p></section>
<section id="fisiere"><h2>Fișierele și verificarea lor</h2><p>Fiecare fișier are o amprentă SHA-256 (arată că rămâne același conținut) și o dovadă OpenTimestamps (arată cel târziu când a existat, ancorată în Bitcoin). Indicatorul curent este {a("/dictionar/latest.json","latest.json")}; legătura dintre sesiune, versiune, amprentă și dovadă este în {a("/sesiuni/registru-sesiuni.json","registru-sesiuni.json")}. Aceste dovezi nu constituie, singure, dovadă juridică de originalitate sau proprietate.</p>{tbl("Versiunea curentă "+d["versiune"]+", sesiunea "+ses["sesiune"],heads,files_rows(ses))}{tbl("Versiunea anterioară 1.0.1, sesiunea "+ses_prev["sesiune"],heads,files_rows(ses_prev))}<h3>Cum verifici</h3><ol><li>Descarcă fișierele din tabel în același folder.</li><li>Rulează <code>sha256sum -c SHA256SUMS_v1.0.2_2026-10-29.txt</code> și verifică să apară „OK” la fiecare fișier.</li><li>Pentru data certă, rulează <code>ots verify fișier.ots</code> cu clientul OpenTimestamps.</li></ol></section>
<section id="entitati"><h2>Entități</h2><p>O entitate este un tip de obiect despre care păstrăm date (firmă, bilanț, sursă). Cheia identifică un exemplar. Firma se identifică prin CUI, cu excepția sucursalelor fără CUI propriu, care se identifică prin codul de înmatriculare.</p>{tbl("Entități",["ID","Entitate","Tip","Cheie","Stare","Descriere"],ent)}</section>
<section id="relatii"><h2>Relații și cardinalități</h2><p>O relație se scrie <em>A — RELAȚIE → B</em> și are o inversă <em>B — INVERSĂ → A</em>. Cardinalitatea se dă pentru ambele sensuri (direct / invers): <code>1</code> exact una, <code>0..1</code> zero sau una, <code>0..*</code> oricâte, <code>1..*</code> cel puțin una.</p>{tbl("Relații",["ID","Relație","Inversa","Cardinalitate","Stare","Descriere"],rel)}</section>
<section id="surse"><h2>Surse</h2><p>Sursele pe care se sprijină dicționarul, cu starea la data înghețării (29 octombrie 2026). Registrul surselor de pe pagina {a("/surse/","Surse și metodologie")} este actualizat separat și poate arăta o stare mai nouă.</p>{tbl("Surse",["ID","Sursă","Link","Cum","Frecvență","Acces","Limite","Stare"],src)}</section>
<section id="reguli"><h2>Reguli de conflict și politici</h2><p>Când două surse dau valori diferite, câștigă sursa de mai jos:</p>{tbl("Reguli de conflict",["Grup de date","Câștigă sursa","Notă"],conf)}<p>{regula_conf}</p><h3>Politici</h3><ul>{pol}</ul></section>
<section id="deschise"><h2>Decizii deschise</h2><ul>{dec}</ul></section>
<section id="istoric"><h2>Istoric versiuni</h2><p>Versiunile se numerotează MAJOR.MINOR.PATCH. MAJOR: {e(vz["major"])}. MINOR: {e(vz["minor"])}. PATCH: {e(vz["patch"])}. {e(vz["imuabilitate"])}</p><ul>{ist}</ul></section>
'''
# page shell from surse
s=open(R+'surse/index.html',encoding='utf-8').read()
head=s[:s.find('<script type="application/ld+json">')]
TITLE="Dicționar de date economice ale firmelor | FirmsFinder AI"
DESC=f"Dicționarul de date FirmsFinder v{d['versiune']}: entități, relații, surse, reguli de conflict, fișiere cu amprente SHA-256 și dovezi OpenTimestamps."
head=head.replace('<title>Surse oficiale și metodologia datelor | FirmsFinder AI</title>',f'<title>{TITLE}</title>')
head=head.replace('https://firmsfinder.eu/surse/','https://firmsfinder.eu/dictionar/')
head=head.replace('Surse oficiale și metodologia datelor | FirmsFinder AI',TITLE)
head=head.replace('Sursele publice ale datelor FirmsFinder (ONRC, Ministerul Finanțelor, ANAF, UE), cum păstrăm datele (R2, D1), cum se verifică integritatea (SHA-256, OpenTimestamps), deciziile de arhitectură și limitele interpretării.',DESC)
head=re.sub(r'<!-- SCHEMA v1\.2 \|[^>]*-->','<!-- SCHEMA v1.2 | https://firmsfinder.eu/dictionar/ | tip: Referință / dicționar de date | mod: tot setul -->',head)
assert 'surse/' not in head.replace('resurse/',''), re.findall(r'.{40}surse/.{20}',head)
ld={"@context":"https://schema.org","@graph":[{"@type":"WebPage","@id":"https://firmsfinder.eu/dictionar/#webpage","url":"https://firmsfinder.eu/dictionar/","name":TITLE,"description":DESC,"inLanguage":"ro","isPartOf":{"@id":"https://firmsfinder.eu/#website"},"publisher":{"@id":"https://aiventure.ro/#organization"},"dateModified":"2026-10-30"},{"@type":"Dataset","@id":"https://firmsfinder.eu/dictionar/#dataset","name":"Dicționar de date economice ale firmelor (FirmsFinder)","version":d['versiune'],"description":DESC,"url":"https://firmsfinder.eu/dictionar/","license":"https://creativecommons.org/licenses/by/4.0/","creator":{"@id":"https://aiventure.ro/#organization"},"distribution":[{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":"https://firmsfinder.eu/dictionar/dictionar-economic-firme_v1.0.2_2026-10-29.json","sha256":"0fb8e5cac4a95065d18d86cf106ead4bf71b2878824827a2162260630466680e"},{"@type":"DataDownload","encodingFormat":"text/markdown","contentUrl":"https://firmsfinder.eu/dictionar/dictionar-economic-firme_v1.0.2_2026-10-29.md","sha256":"af8e66f209c8c6706417ceee69346ad5142ddae5b5c608d4e1d2220441d20a2c"}]}]}
tail=s[s.find('<link href="/onsite.css"'):]
nav_start=tail.find('<main>'); foot=tail[tail.find('<footer>'):]
nav=tail[nav_start:tail.find('<h1>')]
nav=nav.replace('Surse și metodologie</p>','<a href="/surse/">Surse și metodologie</a> / Dicționar de date</p>')
page=head+'<script type="application/ld+json">\n'+json.dumps(ld,ensure_ascii=False,indent=2)+'\n</script>\n\n'+tail[:nav_start]+nav+body+foot
open('dictionar-index_v1.0_2026-10-30.html','w',encoding='utf-8').write(page)
print(len(page), page.count('<tr>'))
