'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { normalise, syllabify } = require('../src/normalise.js');

test('expands a single abbreviation', () => {
  const r = normalise('JLN Bukit Bintang');
  assert.equal(r.normalised, 'Jalan Bukit Bintang');
  assert.deepEqual(r.expansions_applied, [{ from: 'JLN', to: 'Jalan' }]);
  assert.deepEqual(r.ambiguous_flags, []);
});

test('returns the full output shape', () => {
  const r = normalise('JLN');
  assert.ok('normalised' in r);
  assert.ok('tts_ready' in r);
  assert.ok('expansions_applied' in r);
  assert.ok('ambiguous_flags' in r);
});

test('title-cases all-caps non-dictionary words', () => {
  const r = normalise('JLN BUKIT BINTANG');
  assert.equal(r.normalised, 'Jalan Bukit Bintang');
});

test('leaves already-cased words alone', () => {
  const r = normalise('JLN Tun Razak');
  assert.equal(r.normalised, 'Jalan Tun Razak');
});

test('expands a full address with city code', () => {
  const r = normalise('JLN BKT BINTANG, KL');
  assert.equal(r.normalised, 'Jalan Bukit Bintang, Kuala Lumpur');
  assert.equal(r.tts_ready, 'Ja-lan Bu-kit Bin-tang, Kua-la Lum-pur');
  assert.equal(r.expansions_applied.length, 3);
});

test('KG with attached numeric prefix is treated as a weight', () => {
  const r = normalise('5KG beras');
  assert.equal(r.normalised, '5KG beras');
  assert.equal(r.expansions_applied.length, 0);
  assert.equal(r.ambiguous_flags.length, 1);
  assert.equal(r.ambiguous_flags[0].alternative, 'Kampung');
});

test('KG with separated numeric prefix is also a weight', () => {
  const r = normalise('5 KG beras');
  assert.equal(r.expansions_applied.length, 0);
  assert.equal(r.ambiguous_flags.length, 1);
});

test('KG without numeric context expands to Kampung', () => {
  const r = normalise('KG Baru');
  assert.equal(r.normalised, 'Kampung Baru');
  assert.deepEqual(r.expansions_applied, [{ from: 'KG', to: 'Kampung' }]);
  assert.equal(r.ambiguous_flags.length, 0);
});

test('SG expands to Sungai but is always flagged', () => {
  const r = normalise('SG Klang');
  assert.equal(r.normalised, 'Sungai Klang');
  assert.equal(r.expansions_applied.length, 1);
  assert.equal(r.ambiguous_flags.length, 1);
  assert.equal(r.ambiguous_flags[0].alternative, 'Singapore');
});

test('preserves punctuation and spacing', () => {
  const r = normalise('No. 12, JLN Tun Razak, 50450 KL');
  assert.equal(r.normalised, 'No. 12, Jalan Tun Razak, 50450 Kuala Lumpur');
});

test('syllabifies dictionary words from their declared syllables', () => {
  const r = normalise('JLN');
  assert.equal(r.tts_ready, 'Ja-lan');
});

test('syllabifier handles digraphs and diphthongs', () => {
  assert.equal(syllabify('Bintang'), 'Bin-tang');
  assert.equal(syllabify('Bukit'), 'Bu-kit');
  assert.equal(syllabify('Sungai'), 'Su-ngai');
  assert.equal(syllabify('Klang'), 'Klang');
});

test('throws on non-string input', () => {
  assert.throws(() => normalise(123), TypeError);
});

test('handles empty string', () => {
  const r = normalise('');
  assert.equal(r.normalised, '');
  assert.equal(r.tts_ready, '');
  assert.deepEqual(r.expansions_applied, []);
  assert.deepEqual(r.ambiguous_flags, []);
});

// --- Case-insensitive lookup ---------------------------------------------

test('Kg, KG, and kg all expand to Kampung when not numeric-prefixed', () => {
  assert.equal(normalise('Kg Baru').normalised, 'Kampung Baru');
  assert.equal(normalise('KG Baru').normalised, 'Kampung Baru');
  assert.equal(normalise('kg Baru').normalised, 'Kampung Baru');
});

test('lowercase kg with numeric prefix is treated as weight', () => {
  const r = normalise('5 kg beras');
  assert.equal(r.normalised, '5 kg beras');
  assert.equal(r.expansions_applied.length, 0);
  assert.equal(r.ambiguous_flags.length, 1);
});

// --- KT / numeric_suffix_is_code -----------------------------------------

test('KT followed by a numeric code is left unexpanded (separated)', () => {
  const r = normalise('JLN KT 1');
  assert.equal(r.normalised, 'Jalan KT 1');
  assert.ok(r.ambiguous_flags.some(f => f.token === 'KT'));
});

test('KT glued to a numeric code is left unexpanded', () => {
  const r = normalise('JLN KT1');
  assert.equal(r.normalised, 'Jalan KT1');
});

test('KT with no numeric follower expands to Kuala Terengganu', () => {
  assert.equal(normalise('21000 KT').normalised, '21000 Kuala Terengganu');
  assert.equal(normalise('TMN MESRA, KT').normalised, 'Taman Mesra, Kuala Terengganu');
});

// --- New address and state abbreviations ---------------------------------

test('KPG expands like KG', () => {
  assert.equal(normalise('KPG Gersik, Sabah').normalised, 'Kampung Gersik, Sabah');
});

test('expands state codes alongside address terms', () => {
  assert.equal(
    normalise('TMN SRI PETALING, SGR').normalised,
    'Taman Sri Petaling, Selangor',
  );
  assert.equal(
    normalise('JLN DATO KERAMAT, KTN').normalised,
    'Jalan Dato Keramat, Kelantan',
  );
  assert.equal(
    normalise('BKT BINTANG, KL').normalised,
    'Bukit Bintang, Kuala Lumpur',
  );
  assert.equal(
    normalise('PRESINT 1, PJY').normalised,
    'Presint 1, Putrajaya',
  );
  assert.equal(
    normalise('JLN MASJID, TRG').normalised,
    'Jalan Masjid, Terengganu',
  );
});
