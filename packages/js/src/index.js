'use strict';

const { normalise, syllabify } = require('./normalise.js');
const dictionary = require('./dictionary.json');

module.exports = { normalise, syllabify, dictionary };
