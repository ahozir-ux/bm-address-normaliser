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

A thin Worker in `api/` wraps the JS library. A live instance is deployed at:

**https://bm-address-normaliser.ahozir.workers.dev**

### Try it

```bash
# Health check
curl https://bm-address-normaliser.ahozir.workers.dev/health
# → {"ok":true}

# Normalise via GET
curl 'https://bm-address-normaliser.ahozir.workers.dev/?address=JLN+BKT+BINTANG,+KL'

# Normalise via POST
curl -X POST https://bm-address-normaliser.ahozir.workers.dev/ \
  -H 'Content-Type: application/json' \
  -d '{"address": "TMN MIDAH, KL"}'
```

All three return the same JSON shape as the libraries:

```json
{
  "normalised": "Jalan Bukit Bintang, Kuala Lumpur",
  "tts_ready":  "Ja-lan Bu-kit Bin-tang, Kua-la Lum-pur",
  "expansions_applied": [
    {"from": "JLN", "to": "Jalan"},
    {"from": "BKT", "to": "Bukit"},
    {"from": "KL",  "to": "Kuala Lumpur"}
  ],
  "ambiguous_flags": []
}
```

### Deploy your own

```bash
cd api
npx wrangler dev      # local
npx wrangler deploy   # to your Cloudflare account
```

## Repository layout

```
packages/js/       npm package (bm-address-normaliser)
packages/python/   pip package (bm-address)
api/               Cloudflare Worker wrapping the JS library
```

The dictionary is duplicated on purpose:
`packages/js/src/dictionary.json` and `packages/python/bm_address/dictionary.py`
must stay in sync when entries are added.

## Obsidian Integration

Use the live API directly inside Obsidian via the [Templater plugin](https://github.com/SilentVoid13/Templater) — no installation needed beyond Templater itself.

### Setup

1. Install Templater from Obsidian Community Plugins
2. In Templater settings, enable **Allow JS system commands**
3. Create a new template file in your templates folder

### Address Normaliser Template

Create a file called `normalise-address.md` in your Obsidian templates folder with this content:

```javascript
<%*
const raw = await tp.system.prompt("Enter Malaysian address");
const encoded = encodeURIComponent(raw);
const response = await fetch(
  `https://bm-address-normaliser.ahozir.workers.dev/?address=${encoded}`
);
const data = await response.json();
tR += `**Original:** ${data.normalised}\n`;
tR += `**TTS-ready:** ${data.tts_ready}\n`;
if (data.expansions_applied.length > 0) {
  tR += `**Expanded:** ${data.expansions_applied.map(e => `${e.from}→${e.to}`).join(', ')}\n`;
}
if (data.ambiguous_flags.length > 0) {
  tR += `**Flagged:** ${data.ambiguous_flags.map(f => `${f.token} (${f.reason})`).join(', ')}\n`;
}
%>
```

### Usage

1. Open any Obsidian note
2. Open command palette (`Cmd+P`)
3. Run **Templater: Insert Template**
4. Select `normalise-address`
5. Type your abbreviated address when prompted
6. The normalised result inserts inline into your note

### Example Output

Input: `JLN BKT BINTANG, KL`
Original: Jalan Bukit Bintang, Kuala Lumpur

TTS-ready: Ja-lan Bu-kit Bin-tang, Kua-la Lum-pur

Expanded: JLN→Jalan, BKT→Bukit, KL→Kuala Lumpur

### QuickAdd Alternative

If you use [QuickAdd](https://github.com/chhoumann/quickadd) instead of Templater, create a Macro with this script:

```javascript
module.exports = async (params) => {
  const raw = await params.quickAddApi.inputPrompt("Enter Malaysian address");
  const encoded = encodeURIComponent(raw);
  const response = await fetch(
    `https://bm-address-normaliser.ahozir.workers.dev/?address=${encoded}`
  );
  const data = await response.json();
  params.quickAddApi.notify(`✓ ${data.normalised}`);
  return data.normalised;
};
```

## Related

- [claude-skill-bm](https://github.com/ahozir-ux/claude-skill-bm) — Claude skill for Bahasa Malaysia that references this library for address normalisation

## License

MIT — see [LICENSE](./LICENSE).
