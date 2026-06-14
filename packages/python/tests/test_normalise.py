import unittest

from bm_address import normalise, syllabify


class TestNormalise(unittest.TestCase):
    def test_expands_single_abbreviation(self):
        r = normalise("JLN Bukit Bintang")
        self.assertEqual(r["normalised"], "Jalan Bukit Bintang")
        self.assertEqual(r["expansions_applied"], [{"from": "JLN", "to": "Jalan"}])
        self.assertEqual(r["ambiguous_flags"], [])

    def test_returns_full_output_shape(self):
        r = normalise("JLN")
        for key in ("normalised", "tts_ready", "expansions_applied", "ambiguous_flags"):
            self.assertIn(key, r)

    def test_title_cases_all_caps_non_dictionary_words(self):
        r = normalise("JLN BUKIT BINTANG")
        self.assertEqual(r["normalised"], "Jalan Bukit Bintang")

    def test_leaves_already_cased_words_alone(self):
        r = normalise("JLN Tun Razak")
        self.assertEqual(r["normalised"], "Jalan Tun Razak")

    def test_full_address_with_city_code(self):
        r = normalise("JLN BKT BINTANG, KL")
        self.assertEqual(r["normalised"], "Jalan Bukit Bintang, Kuala Lumpur")
        self.assertEqual(r["tts_ready"], "Ja-lan Bu-kit Bin-tang, Kua-la Lum-pur")
        self.assertEqual(len(r["expansions_applied"]), 3)

    def test_kg_with_attached_numeric_prefix_is_weight(self):
        r = normalise("5KG beras")
        self.assertEqual(r["normalised"], "5KG beras")
        self.assertEqual(len(r["expansions_applied"]), 0)
        self.assertEqual(len(r["ambiguous_flags"]), 1)
        self.assertEqual(r["ambiguous_flags"][0]["alternative"], "Kampung")

    def test_kg_with_separated_numeric_prefix_is_weight(self):
        r = normalise("5 KG beras")
        self.assertEqual(len(r["expansions_applied"]), 0)
        self.assertEqual(len(r["ambiguous_flags"]), 1)

    def test_kg_without_numeric_context_expands_to_kampung(self):
        r = normalise("KG Baru")
        self.assertEqual(r["normalised"], "Kampung Baru")
        self.assertEqual(r["expansions_applied"], [{"from": "KG", "to": "Kampung"}])
        self.assertEqual(len(r["ambiguous_flags"]), 0)

    def test_sg_expands_to_sungai_but_is_always_flagged(self):
        r = normalise("SG Klang")
        self.assertEqual(r["normalised"], "Sungai Klang")
        self.assertEqual(len(r["expansions_applied"]), 1)
        self.assertEqual(len(r["ambiguous_flags"]), 1)
        self.assertEqual(r["ambiguous_flags"][0]["alternative"], "Singapore")

    def test_preserves_punctuation_and_spacing(self):
        r = normalise("No. 12, JLN Tun Razak, 50450 KL")
        self.assertEqual(r["normalised"], "No. 12, Jalan Tun Razak, 50450 Kuala Lumpur")

    def test_dictionary_words_use_declared_syllables(self):
        r = normalise("JLN")
        self.assertEqual(r["tts_ready"], "Ja-lan")

    def test_syllabifier_handles_digraphs_and_diphthongs(self):
        self.assertEqual(syllabify("Bintang"), "Bin-tang")
        self.assertEqual(syllabify("Bukit"), "Bu-kit")
        self.assertEqual(syllabify("Sungai"), "Su-ngai")
        self.assertEqual(syllabify("Klang"), "Klang")

    def test_raises_on_non_string_input(self):
        with self.assertRaises(TypeError):
            normalise(123)

    def test_handles_empty_string(self):
        r = normalise("")
        self.assertEqual(r["normalised"], "")
        self.assertEqual(r["tts_ready"], "")
        self.assertEqual(r["expansions_applied"], [])
        self.assertEqual(r["ambiguous_flags"], [])

    # --- Case-insensitive lookup ----------------------------------------

    def test_kg_lookup_is_case_insensitive(self):
        self.assertEqual(normalise("Kg Baru")["normalised"], "Kampung Baru")
        self.assertEqual(normalise("KG Baru")["normalised"], "Kampung Baru")
        self.assertEqual(normalise("kg Baru")["normalised"], "Kampung Baru")

    def test_lowercase_kg_with_numeric_prefix_is_weight(self):
        r = normalise("5 kg beras")
        self.assertEqual(r["normalised"], "5 kg beras")
        self.assertEqual(len(r["expansions_applied"]), 0)
        self.assertEqual(len(r["ambiguous_flags"]), 1)

    # --- KT / numeric_suffix_is_code ------------------------------------

    def test_kt_followed_by_numeric_code_is_unexpanded(self):
        r = normalise("JLN KT 1")
        self.assertEqual(r["normalised"], "Jalan KT 1")
        self.assertTrue(any(f["token"] == "KT" for f in r["ambiguous_flags"]))

    def test_kt_glued_to_numeric_code_is_unexpanded(self):
        r = normalise("JLN KT1")
        self.assertEqual(r["normalised"], "Jalan KT1")

    def test_kt_with_no_numeric_follower_expands(self):
        self.assertEqual(
            normalise("21000 KT")["normalised"], "21000 Kuala Terengganu"
        )
        self.assertEqual(
            normalise("TMN MESRA, KT")["normalised"],
            "Taman Mesra, Kuala Terengganu",
        )

    # --- New address and state abbreviations ----------------------------

    def test_kpg_expands_like_kg(self):
        self.assertEqual(
            normalise("KPG Gersik, Sabah")["normalised"],
            "Kampung Gersik, Sabah",
        )

    def test_state_codes_alongside_address_terms(self):
        cases = [
            ("TMN SRI PETALING, SGR", "Taman Sri Petaling, Selangor"),
            ("JLN DATO KERAMAT, KTN", "Jalan Dato Keramat, Kelantan"),
            ("BKT BINTANG, KL",       "Bukit Bintang, Kuala Lumpur"),
            ("PRESINT 1, PJY",        "Presint 1, Putrajaya"),
            ("JLN MASJID, TRG",       "Jalan Masjid, Terengganu"),
        ]
        for input_str, expected in cases:
            with self.subTest(input=input_str):
                self.assertEqual(normalise(input_str)["normalised"], expected)


if __name__ == "__main__":
    unittest.main()
