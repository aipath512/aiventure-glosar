import w from './index.js';
import fs from 'fs';
const env={ASSETS:{fetch:async(req)=>{let pn=new URL(req.url).pathname;if(pn.endsWith('index.html'))return new Response(null,{status:307,headers:{location:pn.replace('index.html','')}});if(pn.endsWith('/'))pn+='index.html';const p='public'+pn;try{const b=fs.readFileSync(p);return new Response(b,{status:200})}catch(e){return new Response('nf',{status:404})}}}};
globalThis.fetch=async()=>new Response('origin',{status:200});
const t=async(u)=>{const r=await w.fetch(new Request(u),env);const b=await r.text();return [u,r.status,r.headers.get('content-type'),b.length,b.includes('%%'),b.includes('b2b-ai-library.org')]};
for(const u of ['https://b2b-ai-library.org/glosar/','https://b2b-ai-library.org/dictionar/','https://b2b-ai-library.org/dictionar/latest.json','https://b2b-ai-library.org/dictionar/context/SHA256SUMS_context_2026-10-30.txt','https://b2b-ai-library.org/glosar','https://b2b-ai-library.org/dictionar/nu-exista.json','https://b2b-ai-library.org/altceva/'])console.log(await t(u));
