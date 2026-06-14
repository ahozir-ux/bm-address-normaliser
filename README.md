# bm-address-normaliser

Expand abbreviated Malaysian addresses to full form for display and
text-to-speech. Ships JavaScript and Python libraries plus a small
Cloudflare Worker that exposes the normaliser over HTTP.

```
JLN BKT BINTANG, KL
   ↓
Jalan Bukit Bintang, Kuala Lumpur          ← normalised
Ja-lan Bu-kit Bin-tang, Kua-la Lum-pur     ← tts_ready
```

## What it handles

- Expands common Malaysian address abbreviations
  (`JLN`, `TMN`, `BKT`, `LRG`, `BDR`, `BT`, `SEK`, `TKT`, `BLK`, `APT`,
  `KG`, `SG`) and city codes (`KL`, `PJ`, `JB`, `KB`, `KK`).
- Normalises `ALL CAPS` non-dictionary words to `Title Case`.
- Returns syllabified output for TTS, using each entry's declared
  syllabification and falling back to a built-in Malay syllabifier for
  words it doesn't know.
- Flags ambiguous expansions instead of silently guessing:
  - `KG` becomes `Kampung` by default, but a numeric prefix
    (`5KG`, `5 KG`) is treated as the unit kilogram and left as-is.
  - `SG` defaults to `Sungai` but is always flagged because it could
    mean Singapore.

## Output

Every call returns the same shape:

```json
{
  "normalised": "Jalan Bukit Bintang, Kuala Lumpur",
  "tts_ready":  "Ja-lan Bu-kit Bin-tang, Kua-la Lum-pur",
  "expansions_applied": [
    { "from": "JLN", "to": "Jalan" },
    { "from": "BKT", "to": "Bukit" },
    { "from": "KL",  "to": "Kuala Lumpur" }
  ],
  "ambiguous_flags": []
}
```

## JavaScript

```bash
npm install bm-address-normaliser
```

```js
const { normalise } = require('bm-address-normaliser');

normalise('JLN BKT BINTANG, KL');
// { normalised: 'Jalan Bukit Bintang, Kuala Lumpur', ... }
```

Run the test suite:

```bash
cd packages/js
npm test
```

## Python

```bash
pip install bm-address
```

```python
from bm_address import normalise

normalise("JLN BKT BINTANG, KL")
# {'normalised': 'Jalan Bukit Bintang, Kuala Lumpur', ...}
```

Run the test suite:

```bash
cd packages/python
python -m unittest discover -s tests
```

## HTTP API (Cloudflare Worker)

A thin Worker in `api/` wraps the JS library.

```bash
cd api
npx wrangler dev      # local
npx wrangler deploy   # to Cloudflare
```

Endpoints:

```
GET  /?address=JLN+BKT+BINTANG,+KL
POST /            { "address": "JLN BKT BINTANG, KL" }
GET  /health      { "ok": true }
```

Each returns the same JSON shape as the libraries.

## Repository layout

```
packages/js/       npm package (bm-address-normaliser)
packages/python/   pip package (bm-address)
api/               Cloudflare Worker wrapping the JS library
```

The dictionary is duplicated on purpose:
`packages/js/src/dictionary.json` and `packages/python/bm_address/dictionary.py`
must stay in sync when entries are added.

## License

MIT — see [LICENSE](./LICENSE).
