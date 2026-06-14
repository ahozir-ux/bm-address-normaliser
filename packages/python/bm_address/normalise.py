"""Address normaliser. Mirrors packages/js/src/normalise.js."""

from __future__ import annotations

import re
from typing import Any

from .dictionary import DICTIONARY

VOWELS = set("aeiou")
DIGRAPHS = ("ng", "ny", "sy", "kh", "gh")
DIPHTHONGS = ("ai", "au", "oi")

_TOKEN_RE = re.compile(r"(\s+|[,.;:()/])")
_GLUED_RE = re.compile(r"^(\d+)([A-Za-z]+)$")
_WHITESPACE_RE = re.compile(r"^\s+$")
_PUNCT_RE = re.compile(r"^[,.;:()/]+$")
_NUMERIC_RE = re.compile(r"^\d+$")
# A bare number or alphanumeric code that starts with a digit (1, 12, 1A, 2B).
# Used by the numeric_suffix_is_code rule.
_CODE_RE = re.compile(r"^\d[\dA-Za-z]*$")
_PURE_ALPHA_RE = re.compile(r"^[A-Za-z]+$")


def _title_case(word: str) -> str:
    if not word:
        return word
    return word[0].upper() + word[1:].lower()


def _is_all_caps(s: str) -> bool:
    return any(c.isalpha() for c in s) and s == s.upper()


def _next_content_token(tokens: list[str], from_index: int) -> str | None:
    for i in range(from_index + 1, len(tokens)):
        t = tokens[i]
        if not _WHITESPACE_RE.match(t) and not _PUNCT_RE.match(t):
            return t
    return None


def syllabify(word: str) -> str:
    """Split a Malay word into hyphenated syllables.

    Used for words not in the dictionary so tts_ready stays consistent across
    the whole address. Dictionary entries supply their own syllabification.
    """
    if len(word) <= 2:
        return word
    lower = word.lower()

    units = []
    i = 0
    while i < len(word):
        two = lower[i:i + 2]
        if two in DIGRAPHS:
            units.append({"chars": word[i:i + 2], "type": "consonant"})
            i += 2
        else:
            ch = lower[i]
            t = "vowel" if ch in VOWELS else "consonant"
            units.append({"chars": word[i], "type": t})
            i += 1

    # Collapse word-final diphthongs so "Sungai" syllabifies "Su-ngai", not
    # "Su-nga-i".
    if len(units) >= 2:
        last, prev = units[-1], units[-2]
        if last["type"] == "vowel" and prev["type"] == "vowel":
            pair = (prev["chars"] + last["chars"]).lower()
            if pair in DIPHTHONGS:
                units = units[:-2] + [{"chars": prev["chars"] + last["chars"], "type": "vowel"}]

    vowel_idx = [j for j, u in enumerate(units) if u["type"] == "vowel"]
    if len(vowel_idx) <= 1:
        return word

    # Maximum-onset rule: one consonant between vowels starts the next syllable
    # (V-CV); two or more split one-to-the-left (VC-CV / VC-CCV).
    boundaries = [0]
    for k in range(len(vowel_idx) - 1):
        v1, v2 = vowel_idx[k], vowel_idx[k + 1]
        between = v2 - v1 - 1
        if between == 0:
            boundaries.append(v2)
        elif between == 1:
            boundaries.append(v1 + 1)
        else:
            boundaries.append(v1 + 2)

    syllables = []
    for b, start in enumerate(boundaries):
        end = boundaries[b + 1] if b + 1 < len(boundaries) else len(units)
        syllables.append("".join(u["chars"] for u in units[start:end]))
    return "-".join(syllables)


def normalise(input_str: str) -> dict[str, Any]:
    """Expand an abbreviated Malaysian address.

    Returns a dict with: normalised, tts_ready, expansions_applied,
    ambiguous_flags.
    """
    if not isinstance(input_str, str):
        raise TypeError("input must be a string")

    tokens = [t for t in _TOKEN_RE.split(input_str) if t != ""]

    normalised_parts: list[str] = []
    tts_parts: list[str] = []
    expansions_applied: list[dict[str, str]] = []
    ambiguous_flags: list[dict[str, str]] = []
    previous_content_token: str | None = None

    for idx, token in enumerate(tokens):
        if _WHITESPACE_RE.match(token) or _PUNCT_RE.match(token):
            normalised_parts.append(token)
            tts_parts.append(token)
            continue

        glued = _GLUED_RE.match(token)
        numeric_attached = glued.group(1) if glued else None
        alpha_part = glued.group(2) if glued else token
        upper = alpha_part.upper()
        entry = DICTIONARY.get(upper)

        if entry is not None:
            if entry.get("rule") == "numeric_prefix_is_weight":
                numeric_context = numeric_attached is not None or (
                    previous_content_token is not None
                    and _NUMERIC_RE.match(previous_content_token) is not None
                )
                if numeric_context:
                    normalised_parts.append(token)
                    tts_parts.append(token)
                    ambiguous_flags.append({
                        "token": token,
                        "chosen": token,
                        "alternative": entry["expansion"],
                        "reason": f"numeric context suggests {entry['ambiguous_with']}; left unexpanded",
                    })
                    previous_content_token = token
                    continue

            # Section-code heuristic: when the following token starts with a
            # digit (e.g. "KT 1", "KT 2B"), treat KT as a section prefix and
            # leave it alone. With no numeric follower, fall through to expand.
            if entry.get("rule") == "numeric_suffix_is_code":
                nxt = _next_content_token(tokens, idx)
                if nxt is not None and _CODE_RE.match(nxt) is not None:
                    normalised_parts.append(token)
                    tts_parts.append(token)
                    ambiguous_flags.append({
                        "token": token,
                        "chosen": token,
                        "alternative": entry["expansion"],
                        "reason": f'following token "{nxt}" suggests {entry["ambiguous_with"]}; left unexpanded',
                    })
                    previous_content_token = token
                    continue

            expansion = entry["expansion"]
            syllables = entry["syllables"]
            display = f"{numeric_attached} {expansion}" if numeric_attached else expansion
            tts = f"{numeric_attached} {syllables}" if numeric_attached else syllables

            normalised_parts.append(display)
            tts_parts.append(tts)
            expansions_applied.append({"from": token, "to": expansion})

            # Only flag when we *defaulted* — i.e. picked one of multiple plausible
            # meanings without a deterministic rule to resolve it. KG resolved by
            # numeric_prefix_is_weight is not a guess; SG defaulting to Sungai is.
            if "ambiguous_with" in entry and entry.get("rule") == "default_to_malay":
                ambiguous_flags.append({
                    "token": token,
                    "chosen": expansion,
                    "alternative": entry["ambiguous_with"],
                    "reason": f"defaulted to {expansion}; could also mean {entry['ambiguous_with']}",
                })
        else:
            # Title-case only purely alphabetic all-caps tokens. Mixed
            # alphanumeric tokens (KT1, A12, 50450) are codes — preserve them.
            pure_alpha = _PURE_ALPHA_RE.match(alpha_part) is not None
            display_alpha = (
                _title_case(alpha_part)
                if pure_alpha and _is_all_caps(alpha_part)
                else alpha_part
            )
            tts = syllabify(display_alpha)
            normalised_parts.append((numeric_attached or "") + display_alpha)
            tts_parts.append((numeric_attached or "") + tts)

        previous_content_token = token

    return {
        "normalised": "".join(normalised_parts),
        "tts_ready": "".join(tts_parts),
        "expansions_applied": expansions_applied,
        "ambiguous_flags": ambiguous_flags,
    }
