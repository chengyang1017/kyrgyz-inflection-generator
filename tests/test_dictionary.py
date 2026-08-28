import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)


def _search_result():
    return {
        "id": "verb:\u0430\u043b\u0443\u0443",
        "language_code": "ky",
        "part_of_speech": "verb",
        "lemma": "\u0430\u043b\u0443\u0443",
        "primary_match": "form",
        "match_types": ["form"],
        "senses": [
            {
                "sense_no": 1,
                "glosses": ["take"],
            },
            {
                "sense_no": 2,
                "glosses": ["get"],
            },
            {
                "sense_no": 3,
                "glosses": ["buy"],
            },
        ],
        "matched_forms": [
            {
                "lexeme_id": (
                    "verb:\u0430\u043b\u0443\u0443"
                ),
                "form": "\u0430\u043b\u0434\u044b\u043c",
                "canonical_key": "past_men",
                "label": (
                    "\u8fc7\u53bb\u65f6 "
                    "\u00b7 \u6211"
                ),
            },
        ],
        "forms": [
            {
                "lexeme_id": (
                    "verb:\u0430\u043b\u0443\u0443"
                ),
                "form": "\u0430\u043b\u0443\u0443",
                "canonical_key": "infinitive",
            },
            {
                "lexeme_id": (
                    "verb:\u0430\u043b\u0443\u0443"
                ),
                "form": "\u0430\u043b\u0434\u044b\u043c",
                "canonical_key": "past_men",
            },
        ],
    }


def test_build_dictionary_search_result_has_stable_shape():
    from dictionary import build_dictionary_search_result

    result = build_dictionary_search_result(
        _search_result()
    )

    assert result == {
        "id": "verb:\u0430\u043b\u0443\u0443",
        "headword": "\u0430\u043b\u0443\u0443",
        "language_code": "ky",
        "part_of_speech": "verb",
        "match": {
            "primary": "form",
            "types": ["form"],
            "analyses": [
                {
                    "text": (
                        "\u0430\u043b\u0434\u044b\u043c"
                    ),
                    "key": "past_men",
                    "label": (
                        "\u8fc7\u53bb\u65f6 "
                        "\u00b7 \u6211"
                    ),
                }
            ],
        },
        "senses": [
            {
                "number": 1,
                "glosses": ["take"],
            },
            {
                "number": 2,
                "glosses": ["get"],
            },
            {
                "number": 3,
                "glosses": ["buy"],
            },
        ],
    }


def test_dictionary_search_result_does_not_expose_all_forms():
    from dictionary import build_dictionary_search_result

    result = build_dictionary_search_result(
        _search_result()
    )

    assert "forms" not in result


def test_dictionary_search_result_supports_no_form_match():
    from dictionary import build_dictionary_search_result

    source = _search_result()

    source.pop("matched_forms")
    source["primary_match"] = "gloss"
    source["match_types"] = ["gloss"]

    result = build_dictionary_search_result(source)

    assert result["match"] == {
        "primary": "gloss",
        "types": ["gloss"],
        "analyses": [],
    }


def _sample_dictionary_data():
    return {
        "lexemes": [
            {
                "id": "verb:\u0430\u043b\u0443\u0443",
                "language_code": "ky",
                "part_of_speech": "verb",
                "lemma": "\u0430\u043b\u0443\u0443",
            },
        ],
        "senses": [
            {
                "id": "verb:\u0430\u043b\u0443\u0443:s1",
                "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
                "sense_no": 1,
            },
            {
                "id": "verb:\u0430\u043b\u0443\u0443:s2",
                "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
                "sense_no": 2,
            },
            {
                "id": "verb:\u0430\u043b\u0443\u0443:s3",
                "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
                "sense_no": 3,
            },
        ],
        "glosses": [
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s1",
                "language_code": "en",
                "text": "take",
            },
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s2",
                "language_code": "en",
                "text": "get",
            },
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s3",
                "language_code": "en",
                "text": "buy",
            },
        ],
        "noun_forms": [],
        "verb_forms": [
            {
                "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
                "form": "\u0430\u043b\u0443\u0443",
                "canonical_key": "infinitive",
            },
            {
                "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
                "form": "\u0430\u043b\u0434\u044b\u043c",
                "canonical_key": "past_men",
            },
        ],
    }


def test_search_dictionary_returns_presentation_results():
    from dictionary import search_dictionary

    results = search_dictionary(
        _sample_dictionary_data(),
        query_text="\u0430\u043b\u0434\u044b\u043c",
        query_language="ky",
        lexeme_language="ky",
        result_gloss_language="en",
        form_locale="zh",
    )

    assert results == [
        {
            "id": "verb:\u0430\u043b\u0443\u0443",
            "headword": "\u0430\u043b\u0443\u0443",
            "language_code": "ky",
            "part_of_speech": "verb",
            "match": {
                "primary": "form",
                "types": ["form"],
                "analyses": [
                    {
                        "text": (
                            "\u0430\u043b\u0434\u044b\u043c"
                        ),
                        "key": "past_men",
                        "label": (
                            "\u8fc7\u53bb\u65f6 "
                            "\u00b7 \u6211"
                        ),
                    },
                ],
            },
            "senses": [
                {
                    "number": 1,
                    "glosses": ["take"],
                },
                {
                    "number": 2,
                    "glosses": ["get"],
                },
                {
                    "number": 3,
                    "glosses": ["buy"],
                },
            ],
        }
    ]


def test_search_dictionary_returns_empty_list_when_not_found():
    from dictionary import search_dictionary

    results = search_dictionary(
        _sample_dictionary_data(),
        query_text="missing",
        query_language="en",
        lexeme_language="ky",
        result_gloss_language="en",
        form_locale="zh",
    )

    assert results == []


def test_dictionary_analysis_exposes_verb_morphology_features():
    from dictionary import build_dictionary_search_result

    source = _search_result()

    source["matched_forms"][0].update(
        {
            "form_type": "finite",
            "tense": "past",
            "person": "1sg",
            "negative": False,
        }
    )

    result = build_dictionary_search_result(source)

    analysis = result["match"]["analyses"][0]

    assert analysis["features"] == {
        "form_type": "finite",
        "tense": "past",
        "person": "1sg",
        "negative": False,
    }


def test_dictionary_analysis_exposes_noun_morphology_features():
    from dictionary import build_dictionary_search_result

    source = {
        "id": "noun:\u043a\u0438\u0442\u0435\u043f",
        "language_code": "ky",
        "part_of_speech": "noun",
        "lemma": "\u043a\u0438\u0442\u0435\u043f",
        "primary_match": "form",
        "match_types": ["form"],
        "senses": [
            {
                "sense_no": 1,
                "glosses": ["book"],
            },
        ],
        "matched_forms": [
            {
                "lexeme_id": (
                    "noun:\u043a\u0438\u0442\u0435\u043f"
                ),
                "form": (
                    "\u043a\u0438\u0442\u0435\u043f\u0442\u0435"
                ),
                "canonical_key": "singular_locative",
                "label": (
                    "\u5355\u6570 "
                    "\u00b7 \u4f4d\u683c"
                ),
                "number": "sg",
                "possessive": None,
                "case": "locative",
                "interrogative": False,
                "special": False,
            },
        ],
        "forms": [],
    }

    result = build_dictionary_search_result(source)

    analysis = result["match"]["analyses"][0]

    assert analysis["features"] == {
        "number": "sg",
        "possessive": None,
        "case": "locative",
        "interrogative": False,
        "special": False,
    }
