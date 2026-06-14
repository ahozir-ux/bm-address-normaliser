'use strict';

const dictionary = require('./dictionary.json');

const VOWELS = new Set(['a', 'e', 'i', 'o', 'u']);
const DIGRAPHS = ['ng', 'ny', 'sy', 'kh', 'gh'];
const DIPHTHONGS = ['ai', 'au', 'oi'];

function titleCase(word) {
  if (!word) return word;
  return word[0].toUpperCase() + word.slice(1).toLowerCase();
}

// Lightweight Malay syllabifier. Used for tokens not in the dictionary so the
// tts_ready output is consistent across the whole address.
function syllabify(word) {
  if (word.length <= 2) return word;
  const lower = word.toLowerCase();

  // Tokenise the word into atomic units, keeping digraphs (ng, ny, ...) together.
  const units = [];
  for (let i = 0; i < word.length; ) {
    const two = lower.slice(i, i + 2);
    if (DIGRAPHS.includes(two)) {
      units.push({ chars: word.slice(i, i + 2), type: 'consonant' });
      i += 2;
    } else {
      const ch = lower[i];
      units.push({ chars: word[i], type: VOWELS.has(ch) ? 'vowel' : 'consonant' });
      i += 1;
    }
  }

  // Collapse word-final diphthongs (ai, au, oi) into a single vowel unit so
  // names like "Sungai" syllabify as "Su-ngai", not "Su-nga-i".
  if (units.length >= 2) {
    const last = units[units.length - 1];
    const prev = units[units.length - 2];
    if (last.type === 'vowel' && prev.type === 'vowel') {
      const pair = (prev.chars + last.chars).toLowerCase();
      if (DIPHTHONGS.includes(pair)) {
        units.splice(units.length - 2, 2, { chars: prev.chars + last.chars, type: 'vowel' });
      }
    }
  }

  const vowelIdx = [];
  units.forEach((u, j) => { if (u.type === 'vowel') vowelIdx.push(j); });
  if (vowelIdx.length <= 1) return word;

  // Maximum-onset rule: a lone consonant between vowels starts the next
  // syllable (V-CV); two or more split one-to-the-left (VC-CV / VC-CCV).
  const boundaries = [0];
  for (let k = 0; k < vowelIdx.length - 1; k++) {
    const v1 = vowelIdx[k];
    const v2 = vowelIdx[k + 1];
    const between = v2 - v1 - 1;
    if (between === 0)      boundaries.push(v2);
    else if (between === 1) boundaries.push(v1 + 1);
    else                    boundaries.push(v1 + 2);
  }

  const syllables = [];
  for (let b = 0; b < boundaries.length; b++) {
    const start = boundaries[b];
    const end = b + 1 < boundaries.length ? boundaries[b + 1] : units.length;
    syllables.push(units.slice(start, end).map(u => u.chars).join(''));
  }
  return syllables.join('-');
}

function isAllCaps(s) {
  return /[A-Z]/.test(s) && s === s.toUpperCase();
}

function isWhitespace(t) { return /^\s+$/.test(t); }
function isPunctuation(t) { return /^[,.;:()\/]+$/.test(t); }

// A bare number or alphanumeric code that starts with a digit (1, 12, 1A, 2B).
// Used by the numeric_suffix_is_code rule.
function isCodeToken(t) { return /^\d[\dA-Za-z]*$/.test(t); }

function nextContentToken(tokens, fromIndex) {
  for (let i = fromIndex + 1; i < tokens.length; i++) {
    const t = tokens[i];
    if (!isWhitespace(t) && !isPunctuation(t)) return t;
  }
  return null;
}

function normalise(input) {
  if (typeof input !== 'string') {
    throw new TypeError('input must be a string');
  }

  // Split on whitespace and a small set of address punctuation, keeping the
  // separators so we can reassemble the original spacing.
  const tokens = input.split(/(\s+|[,.;:()\/])/).filter(t => t !== '');

  const normalisedParts = [];
  const ttsParts = [];
  const expansionsApplied = [];
  const ambiguousFlags = [];
  let previousContentToken = null;

  for (let idx = 0; idx < tokens.length; idx++) {
    const token = tokens[idx];
    if (isWhitespace(token) || isPunctuation(token)) {
      normalisedParts.push(token);
      ttsParts.push(token);
      continue;
    }

    // Detect a number glued to letters, e.g. "5KG", so we can both look up the
    // alpha part in the dictionary and apply the weight heuristic.
    const glued = token.match(/^(\d+)([A-Za-z]+)$/);
    const numericAttached = glued ? glued[1] : null;
    const alphaPart = glued ? glued[2] : token;
    const upper = alphaPart.toUpperCase();
    const entry = dictionary[upper];

    if (entry) {
      // Weight heuristic: a numeric prefix (in-token or as the previous token)
      // means we're looking at a unit like "5 KG of rice", not "Kampung".
      if (entry.rule === 'numeric_prefix_is_weight') {
        const numericContext = numericAttached !== null
          || (previousContentToken !== null && /^\d+$/.test(previousContentToken));
        if (numericContext) {
          normalisedParts.push(token);
          ttsParts.push(token);
          ambiguousFlags.push({
            token,
            chosen: token,
            alternative: entry.expansion,
            reason: `numeric context suggests ${entry.ambiguous_with}; left unexpanded`,
          });
          previousContentToken = token;
          continue;
        }
      }

      // Section-code heuristic: when the following token starts with a digit
      // (e.g. "KT 1", "KT 2B"), treat KT as a section prefix and leave it
      // alone. With no numeric follower, fall through to the expansion.
      if (entry.rule === 'numeric_suffix_is_code') {
        const next = nextContentToken(tokens, idx);
        if (next && isCodeToken(next)) {
          normalisedParts.push(token);
          ttsParts.push(token);
          ambiguousFlags.push({
            token,
            chosen: token,
            alternative: entry.expansion,
            reason: `following token "${next}" suggests ${entry.ambiguous_with}; left unexpanded`,
          });
          previousContentToken = token;
          continue;
        }
      }

      const expansion = entry.expansion;
      const syllables = entry.syllables;
      const display = numericAttached ? `${numericAttached} ${expansion}` : expansion;
      const tts = numericAttached ? `${numericAttached} ${syllables}` : syllables;

      normalisedParts.push(display);
      ttsParts.push(tts);
      expansionsApplied.push({ from: token, to: expansion });

      // Only flag when we *defaulted* — i.e. picked one of multiple plausible
      // meanings without a deterministic rule to resolve it. KG resolved by
      // numeric_prefix_is_weight is not a guess; SG defaulting to Sungai is.
      if (entry.ambiguous_with && entry.rule === 'default_to_malay') {
        ambiguousFlags.push({
          token,
          chosen: expansion,
          alternative: entry.ambiguous_with,
          reason: `defaulted to ${expansion}; could also mean ${entry.ambiguous_with}`,
        });
      }
    } else {
      // Title-case only purely alphabetic all-caps tokens. Mixed alphanumeric
      // tokens (KT1, A12, 50450) are codes — preserve them verbatim.
      const pureAlpha = /^[A-Za-z]+$/.test(alphaPart);
      const display = (pureAlpha && isAllCaps(alphaPart)) ? titleCase(alphaPart) : alphaPart;
      const tts = syllabify(display);
      normalisedParts.push(numericAttached ? numericAttached + display : display);
      ttsParts.push(numericAttached ? numericAttached + tts : tts);
    }

    previousContentToken = token;
  }

  return {
    normalised: normalisedParts.join(''),
    tts_ready: ttsParts.join(''),
    expansions_applied: expansionsApplied,
    ambiguous_flags: ambiguousFlags,
  };
}

module.exports = { normalise, syllabify };
