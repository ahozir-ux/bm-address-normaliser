"""Abbreviation dictionary for Malaysian addresses.

Mirrors packages/js/src/dictionary.json. Keep both in sync when adding entries.
"""

DICTIONARY = {
    # Address terms
    "JLN": {"expansion": "Jalan",         "syllables": "Ja-lan"},
    "TMN": {"expansion": "Taman",         "syllables": "Ta-man"},
    "BKT": {"expansion": "Bukit",         "syllables": "Bu-kit"},
    "LRG": {"expansion": "Lorong",        "syllables": "Lo-rong"},
    "BDR": {"expansion": "Bandar",        "syllables": "Ban-dar"},
    "BT":  {"expansion": "Batu",          "syllables": "Ba-tu"},
    "SEK": {"expansion": "Seksyen",       "syllables": "Sek-syen"},
    "TKT": {"expansion": "Tingkat",       "syllables": "Ting-kat"},
    "BLK": {"expansion": "Blok",          "syllables": "Blok"},
    "APT": {"expansion": "Apartmen",      "syllables": "A-part-men"},
    "ULU": {"expansion": "Ulu",           "syllables": "U-lu"},

    # City codes
    "KL":  {"expansion": "Kuala Lumpur",  "syllables": "Kua-la Lum-pur"},
    "PJ":  {"expansion": "Petaling Jaya", "syllables": "Pe-ta-ling Ja-ya"},
    "JB":  {"expansion": "Johor Bahru",   "syllables": "Jo-hor Bah-ru"},
    "KB":  {"expansion": "Kota Bharu",    "syllables": "Ko-ta Bha-ru"},
    "KK":  {"expansion": "Kota Kinabalu", "syllables": "Ko-ta Ki-na-ba-lu"},
    "PNG": {"expansion": "Pulau Pinang",  "syllables": "Pu-lau Pi-nang"},
    "KCH": {"expansion": "Kuching",       "syllables": "Ku-ching"},

    # Ambiguous (driven by rule + ambiguous_with)
    "KG": {
        "expansion": "Kampung",
        "syllables": "Kam-pung",
        "ambiguous_with": "kilogram",
        "rule": "numeric_prefix_is_weight",
    },
    "KPG": {
        "expansion": "Kampung",
        "syllables": "Kam-pung",
        "ambiguous_with": "kilogram",
        "rule": "numeric_prefix_is_weight",
    },
    "SG": {
        "expansion": "Sungai",
        "syllables": "Su-ngai",
        "ambiguous_with": "Singapore",
        "rule": "default_to_malay",
    },
    "KT": {
        "expansion": "Kuala Terengganu",
        "syllables": "Kua-la Te-reng-ga-nu",
        "ambiguous_with": "section code prefix",
        "rule": "numeric_suffix_is_code",
    },

    # State and federal territory codes
    "SGR": {"expansion": "Selangor",        "syllables": "Se-lan-gor"},
    "JHR": {"expansion": "Johor",           "syllables": "Jo-hor"},
    "PHG": {"expansion": "Pahang",          "syllables": "Pa-hang"},
    "PRK": {"expansion": "Perak",           "syllables": "Pe-rak"},
    "KDH": {"expansion": "Kedah",           "syllables": "Ke-dah"},
    "KTN": {"expansion": "Kelantan",        "syllables": "Ke-lan-tan"},
    "MLK": {"expansion": "Melaka",          "syllables": "Me-la-ka"},
    "NSN": {"expansion": "Negeri Sembilan", "syllables": "Ne-ge-ri Sem-bi-lan"},
    "TRG": {"expansion": "Terengganu",      "syllables": "Te-reng-ga-nu"},
    "SBH": {"expansion": "Sabah",           "syllables": "Sa-bah"},
    "SWK": {"expansion": "Sarawak",         "syllables": "Sa-ra-wak"},
    "LBN": {"expansion": "Labuan",          "syllables": "La-bu-an"},
    "PJY": {"expansion": "Putrajaya",       "syllables": "Pu-tra-ja-ya"},
}
