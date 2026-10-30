import w from './index.js';import fs from 'fs';
const env={ASSETS:{fetch:async()=>new Response('nf',{status:404})}};
const page='<html><body><main><p>Folosim AI-LENS și 3WEBOBS.</p></main></body></html>';
globalThis.fetch=async(req)=>new Response(page,{status:200,headers:{'content-type':'text/html; charset=utf-8'}});
for(const [u] of [['https://b2b-ai-library.org/'],['https://b2b-ai-library.org/legal/'],['https://altceva.com/'],['https://b2b-ai-library.org/?nolinks=1']]){const r=await w.fetch(new Request(u),env);const b=await r.text();console.log(u,r.status,r.headers.get('x-aiventure-links'),(b.match(/class="gl"/g)||[]).length)}
