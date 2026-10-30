# aiventure-glosar

Worker + sursă unică pentru **dicționarul de date** și **glosarul** comune rețelei de site-uri AiVenture.
Servește `/glosar/` și `/dictionar/` pe fiecare domeniu din rețea, din aceleași fișiere.

- `public/` — paginile autonome (șabloane cu `%%ORIGIN%%` și `%%DOMAIN%%`), dicționarul înghețat (JSON, MD, SHA256SUMS, dovezi `.ots`, `latest.json`) și contextul public.
- `worker/index.js` — Workerul (v1.0). `worker/test.mjs` — test local (`node worker/test.mjs`).
- `wrangler.jsonc` — numele Workerului (`aiventure-glosar`) și rutele. **Faza 1: doar b2b-ai-library.org**; celelalte domenii se adaugă pe rând.
- `dictionar/`, `sesiuni/` — sursa înghețată (nu se modifică; o schimbare = versiune nouă cu SHA-256 și OTS).
- `generator/` — scripturile care produc paginile. `build_standalone.py` reface `public/` din paginile etalon de pe firmsfinder.eu.

Rutele sunt pe căi (`domeniu/glosar*`, `domeniu/dictionar*`), deci nu intră în conflict cu Workerii care au rute `domeniu/*`.

Etalon: https://firmsfinder.eu/glosar/ · https://firmsfinder.eu/dictionar/ · Sesiune 0008C · 2026-10-30
