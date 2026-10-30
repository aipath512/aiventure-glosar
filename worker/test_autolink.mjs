import {buildRules,autolink} from './autolink.js';
import fs from 'fs';
const cfg=JSON.parse(fs.readFileSync('worker/legaturi.json','utf8'));
let r=buildRules(cfg,'b2b-ai-library.org');
const h='<html><head><title>AI-LENS test</title><script>var x="AI-LENS <b";</script></head><body><header><a href="/">3WEBOBS</a></header><main><h1>3WEBOBS</h1><p>Folosim AI-LENS și 3WEBOBS pentru CUI. AI-LENS din nou, FirmsFinder, EU AI Act Ready și AI-READY INJECTOR.</p><p><a href="/x">AI-LENS</a> <code>3WEBOBS</code></p></main><footer>FirmsFinder</footer></body></html>';
console.log(autolink(h,r));
const ro=buildRules(cfg,'aiventure.ro');
console.log(autolink('<body><main><p>Căutăm după CUI și CAEN, bilanțuri ONRC; AI-LENS, GEO, cardinalități. CUI din nou.</p></main></body>',ro));
console.log(buildRules(cfg,'altceva.com'));
