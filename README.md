# aiventure-glosar

Sursă unică pentru dicționarul de date și glosarul comun al rețelei de site-uri AiVenture.

- `dictionar/` — dicționarul de date înghețat pe versiune (JSON, MD, SHA256SUMS, dovezi OpenTimestamps, `latest.json`), plus `context/`.
- `sesiuni/registru-sesiuni.json` — legătura dintre sesiune, versiune, amprentă și dovadă.
- `generator/` — scripturile care produc paginile `/glosar/` și `/dictionar/` din JSON (în curs de adaptare la domeniu/limbă).
- `worker/` — Workerul `aiventure-glosar-worker` (de scris): servește `/glosar/` și `/dictionar/` pe fiecare domeniu din KV și leagă termenii la edge.

Etalon: https://firmsfinder.eu/glosar/ și https://firmsfinder.eu/dictionar/
Sesiune: 0008C · 2026-10-30
