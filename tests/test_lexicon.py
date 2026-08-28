import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from lexicon import lookup_lexeme


def _sample_data():
    return {
        "lexemes": [
            {
                "id": "verb:\u0430\u043b\u0443\u0443",
                "language_code": "ky",
                "part_of_speech": "verb",
                "lemma": "\u0430\u043b\u0443\u0443",
            },
            {
                "id": "noun:\u043a\u0438\u0442\u0435\u043f",
                "language_code": "ky",
                "part_of_speech": "noun",
                "lemma": "\u043a\u0438\u0442\u0435\u043f",
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
                "language_code": "zh",
                "text": "\u62ff",
            },
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s1",
                "language_code": "en",
                "text": "take",
            },
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s2",
                "language_code": "zh",
                "text": "\u5f97\u5230",
            },
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s2",
                "language_code": "en",
                "text": "get",
            },
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s3",
                "language_code": "zh",
                "text": "\u4e70",
            },
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s3",
                "language_code": "en",
                "text": "buy",
            },
        ],
        "noun_forms": [
            {
                "lexeme_id": "noun:\u043a\u0438\u0442\u0435\u043f",
                "form": "\u043a\u0438\u0442\u0435\u043f\u0442\u0435",
                "canonical_key": "singular_locative",
            },
        ],
        "verb_forms": [
            {
                "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
                "form": "\u0430\u043b\u0434\u044b\u043c",
                "canonical_key": "past_men",
            },
            {
                "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
                "form": "\u0430\u043b\u0430\u043c",
                "canonical_key": "future_men",
            },
        ],
    }


def test_lookup_returns_requested_language_glosses_by_sense():
    result = lookup_lexeme(
        _sample_data(),
        language_code="ky",
        lemma="\u0430\u043b\u0443\u0443",
        gloss_language="zh",
    )

    assert result["id"] == "verb:\u0430\u043b\u0443\u0443"
    assert result["lemma"] == "\u0430\u043b\u0443\u0443"
    assert result["part_of_speech"] == "verb"

    assert result["senses"] == [
        {
            "sense_no": 1,
            "glosses": ["\u62ff"],
        },
        {
            "sense_no": 2,
            "glosses": ["\u5f97\u5230"],
        },
        {
            "sense_no": 3,
            "glosses": ["\u4e70"],
        },
    ]


def test_lookup_can_switch_gloss_language_without_changing_lexeme():
    result = lookup_lexeme(
        _sample_data(),
        language_code="ky",
        lemma="\u0430\u043b\u0443\u0443",
        gloss_language="en",
    )

    assert [
        sense["glosses"]
        for sense in result["senses"]
    ] == [
        ["take"],
        ["get"],
        ["buy"],
    ]


def test_lookup_returns_only_matching_lexeme_morphology():
    result = lookup_lexeme(
        _sample_data(),
        language_code="ky",
        lemma="\u0430\u043b\u0443\u0443",
        gloss_language="en",
    )

    assert result["forms"] == [
        {
            "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
            "form": "\u0430\u043b\u0434\u044b\u043c",
            "canonical_key": "past_men",
        },
        {
            "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
            "form": "\u0430\u043b\u0430\u043c",
            "canonical_key": "future_men",
        },
    ]


def test_lookup_returns_none_for_unknown_lexeme():
    result = lookup_lexeme(
        _sample_data(),
        language_code="ky",
        lemma="missing",
        gloss_language="en",
    )

    assert result is None


def test_search_by_gloss_finds_lexeme_from_translation():
    from lexicon import search_lexemes_by_gloss

    results = search_lexemes_by_gloss(
        _sample_data(),
        query_language="en",
        query_text="buy",
        lexeme_language="ky",
        result_gloss_language="zh",
    )

    assert len(results) == 1

    result = results[0]

    assert result["id"] == "verb:\u0430\u043b\u0443\u0443"
    assert result["lemma"] == "\u0430\u043b\u0443\u0443"

    assert result["senses"] == [
        {
            "sense_no": 1,
            "glosses": ["\u62ff"],
        },
        {
            "sense_no": 2,
            "glosses": ["\u5f97\u5230"],
        },
        {
            "sense_no": 3,
            "glosses": ["\u4e70"],
        },
    ]


def test_search_by_gloss_is_case_insensitive():
    from lexicon import search_lexemes_by_gloss

    results = search_lexemes_by_gloss(
        _sample_data(),
        query_language="en",
        query_text="BUY",
        lexeme_language="ky",
        result_gloss_language="en",
    )

    assert [
        result["lemma"]
        for result in results
    ] == [
        "\u0430\u043b\u0443\u0443",
    ]


def test_search_by_gloss_returns_empty_list_when_not_found():
    from lexicon import search_lexemes_by_gloss

    results = search_lexemes_by_gloss(
        _sample_data(),
        query_language="en",
        query_text="missing",
        lexeme_language="ky",
        result_gloss_language="en",
    )

    assert results == []


def test_search_by_form_finds_lexeme_from_inflected_form():
    from lexicon import search_lexemes_by_form

    results = search_lexemes_by_form(
        _sample_data(),
        form_text="\u0430\u043b\u0434\u044b\u043c",
        language_code="ky",
        result_gloss_language="zh",
    )

    assert len(results) == 1

    result = results[0]

    assert result["id"] == "verb:\u0430\u043b\u0443\u0443"
    assert result["lemma"] == "\u0430\u043b\u0443\u0443"

    assert result["matched_forms"] == [
        {
            "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
            "form": "\u0430\u043b\u0434\u044b\u043c",
            "canonical_key": "past_men",
        }
    ]

    assert result["senses"] == [
        {
            "sense_no": 1,
            "glosses": ["\u62ff"],
        },
        {
            "sense_no": 2,
            "glosses": ["\u5f97\u5230"],
        },
        {
            "sense_no": 3,
            "glosses": ["\u4e70"],
        },
    ]


def test_search_by_form_supports_noun_forms():
    from lexicon import search_lexemes_by_form

    results = search_lexemes_by_form(
        _sample_data(),
        form_text="\u043a\u0438\u0442\u0435\u043f\u0442\u0435",
        language_code="ky",
        result_gloss_language="en",
    )

    assert len(results) == 1
    assert results[0]["id"] == "noun:\u043a\u0438\u0442\u0435\u043f"


def test_search_by_form_returns_empty_list_when_not_found():
    from lexicon import search_lexemes_by_form

    results = search_lexemes_by_form(
        _sample_data(),
        form_text="missing",
        language_code="ky",
        result_gloss_language="en",
    )

    assert results == []


def test_search_lexicon_finds_exact_lemma():
    from lexicon import search_lexicon

    results = search_lexicon(
        _sample_data(),
        query_text="\u0430\u043b\u0443\u0443",
        query_language="ky",
        lexeme_language="ky",
        result_gloss_language="zh",
    )

    assert len(results) == 1

    assert results[0]["id"] == (
        "verb:\u0430\u043b\u0443\u0443"
    )
    assert results[0]["primary_match"] == "lemma"
    assert results[0]["match_types"] == ["lemma"]


def test_search_lexicon_finds_translation_gloss():
    from lexicon import search_lexicon

    results = search_lexicon(
        _sample_data(),
        query_text="buy",
        query_language="en",
        lexeme_language="ky",
        result_gloss_language="zh",
    )

    assert len(results) == 1

    result = results[0]

    assert result["lemma"] == (
        "\u0430\u043b\u0443\u0443"
    )
    assert result["primary_match"] == "gloss"
    assert result["match_types"] == ["gloss"]

    assert result["senses"][2]["glosses"] == [
        "\u4e70"
    ]


def test_search_lexicon_finds_inflected_form():
    from lexicon import search_lexicon

    results = search_lexicon(
        _sample_data(),
        query_text="\u0430\u043b\u0434\u044b\u043c",
        query_language="ky",
        lexeme_language="ky",
        result_gloss_language="zh",
    )

    assert len(results) == 1

    result = results[0]

    assert result["lemma"] == (
        "\u0430\u043b\u0443\u0443"
    )
    assert result["primary_match"] == "form"
    assert result["match_types"] == ["form"]

    assert result["matched_forms"][0][
        "canonical_key"
    ] == "past_men"


def test_search_lexicon_deduplicates_same_lexeme():
    from lexicon import search_lexicon

    data = _sample_data()

    data["verb_forms"].append(
        {
            "lexeme_id": (
                "verb:\u0430\u043b\u0443\u0443"
            ),
            "form": "\u0430\u043b\u0443\u0443",
            "canonical_key": "infinitive",
        }
    )

    results = search_lexicon(
        data,
        query_text="\u0430\u043b\u0443\u0443",
        query_language="ky",
        lexeme_language="ky",
        result_gloss_language="en",
    )

    assert len(results) == 1

    result = results[0]

    assert result["primary_match"] == "lemma"
    assert result["match_types"] == [
        "lemma",
        "form",
    ]

    assert result["matched_forms"] == [
        {
            "lexeme_id": (
                "verb:\u0430\u043b\u0443\u0443"
            ),
            "form": "\u0430\u043b\u0443\u0443",
            "canonical_key": "infinitive",
        }
    ]


def test_search_lexicon_returns_empty_list_when_not_found():
    from lexicon import search_lexicon

    results = search_lexicon(
        _sample_data(),
        query_text="missing",
        query_language="en",
        lexeme_language="ky",
        result_gloss_language="zh",
    )

    assert results == []


def test_search_lexicon_localizes_matched_verb_form():
    from lexicon import search_lexicon

    results = search_lexicon(
        _sample_data(),
        query_text="\u0430\u043b\u0434\u044b\u043c",
        query_language="ky",
        lexeme_language="ky",
        result_gloss_language="en",
        form_locale="zh",
    )

    assert len(results) == 1

    result = results[0]

    assert result["senses"] == [
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
    ]

    assert result["matched_forms"][0]["canonical_key"] == (
        "past_men"
    )
    assert result["matched_forms"][0]["label"] == (
        "\u8fc7\u53bb\u65f6 \u00b7 \u6211"
    )


def test_search_lexicon_localizes_matched_noun_form():
    from lexicon import search_lexicon

    results = search_lexicon(
        _sample_data(),
        query_text="\u043a\u0438\u0442\u0435\u043f\u0442\u0435",
        query_language="ky",
        lexeme_language="ky",
        result_gloss_language="en",
        form_locale="zh",
    )

    assert len(results) == 1

    result = results[0]

    assert result["id"] == (
        "noun:\u043a\u0438\u0442\u0435\u043f"
    )

    assert result["matched_forms"][0]["label"] == (
        "\u5355\u6570 \u00b7 \u4f4d\u683c"
    )


def test_search_lexicon_preserves_multiple_form_analyses():
    from lexicon import search_lexicon

    data = _sample_data()

    data["verb_forms"].append(
        {
            "lexeme_id": (
                "verb:\u0430\u043b\u0443\u0443"
            ),
            "form": "\u0430\u043b\u0434\u044b\u043c",
            "canonical_key": "future_men",
        }
    )

    results = search_lexicon(
        data,
        query_text="\u0430\u043b\u0434\u044b\u043c",
        query_language="ky",
        lexeme_language="ky",
        result_gloss_language="en",
        form_locale="zh",
    )

    assert len(results) == 1

    matched_forms = results[0]["matched_forms"]

    assert matched_forms == [
        {
            "lexeme_id": (
                "verb:\u0430\u043b\u0443\u0443"
            ),
            "form": "\u0430\u043b\u0434\u044b\u043c",
            "canonical_key": "past_men",
            "label": "\u8fc7\u53bb\u65f6 \u00b7 \u6211",
        },
        {
            "lexeme_id": (
                "verb:\u0430\u043b\u0443\u0443"
            ),
            "form": "\u0430\u043b\u0434\u044b\u043c",
            "canonical_key": "future_men",
            "label": (
                "\u73b0\u5728\u5c06\u6765\u65f6 "
                "\u00b7 \u6211"
            ),
        },
    ]
