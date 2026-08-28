import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)


def _sample_data():
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
                "form_type": "infinitive",
                "tense": None,
                "person": None,
                "negative": False,
            },
            {
                "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
                "form": "\u0430\u043b\u0434\u044b\u043c",
                "canonical_key": "past_men",
                "form_type": "finite",
                "tense": "past",
                "person": "1sg",
                "negative": False,
            },
        ],
    }


def test_sqlite_lookup_lexeme_returns_domain_result(
    tmp_path,
):
    from canonical import export_canonical_sqlite
    from sqlite_lexicon import lookup_lexeme_sqlite

    db_path = export_canonical_sqlite(
        _sample_data(),
        tmp_path / "dictionary.db",
    )

    result = lookup_lexeme_sqlite(
        db_path,
        language_code="ky",
        lemma="\u0430\u043b\u0443\u0443",
        gloss_language="en",
    )

    assert result["id"] == (
        "verb:\u0430\u043b\u0443\u0443"
    )
    assert result["lemma"] == (
        "\u0430\u043b\u0443\u0443"
    )
    assert result["part_of_speech"] == "verb"

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

    assert result["forms"][1] == {
        "lexeme_id": (
            "verb:\u0430\u043b\u0443\u0443"
        ),
        "form": "\u0430\u043b\u0434\u044b\u043c",
        "canonical_key": "past_men",
        "form_type": "finite",
        "tense": "past",
        "person": "1sg",
        "negative": False,
    }


def test_sqlite_lookup_lexeme_returns_none_when_missing(
    tmp_path,
):
    from canonical import export_canonical_sqlite
    from sqlite_lexicon import lookup_lexeme_sqlite

    db_path = export_canonical_sqlite(
        _sample_data(),
        tmp_path / "dictionary.db",
    )

    result = lookup_lexeme_sqlite(
        db_path,
        language_code="ky",
        lemma="missing",
        gloss_language="en",
    )

    assert result is None


def test_sqlite_search_by_form_finds_verb(
    tmp_path,
):
    from canonical import export_canonical_sqlite
    from sqlite_lexicon import search_lexemes_by_form_sqlite

    db_path = export_canonical_sqlite(
        _sample_data(),
        tmp_path / "dictionary.db",
    )

    results = search_lexemes_by_form_sqlite(
        db_path,
        form_text="\u0430\u043b\u0434\u044b\u043c",
        language_code="ky",
        result_gloss_language="en",
    )

    assert len(results) == 1

    result = results[0]

    assert result["id"] == (
        "verb:\u0430\u043b\u0443\u0443"
    )
    assert result["lemma"] == (
        "\u0430\u043b\u0443\u0443"
    )

    assert result["matched_forms"] == [
        {
            "lexeme_id": (
                "verb:\u0430\u043b\u0443\u0443"
            ),
            "form": "\u0430\u043b\u0434\u044b\u043c",
            "canonical_key": "past_men",
            "form_type": "finite",
            "tense": "past",
            "person": "1sg",
            "negative": False,
        }
    ]


def test_sqlite_search_by_form_finds_noun(
    tmp_path,
):
    from canonical import export_canonical_sqlite
    from sqlite_lexicon import search_lexemes_by_form_sqlite

    data = _sample_data()

    data["lexemes"].append(
        {
            "id": "noun:\u043a\u0438\u0442\u0435\u043f",
            "language_code": "ky",
            "part_of_speech": "noun",
            "lemma": "\u043a\u0438\u0442\u0435\u043f",
        }
    )

    data["senses"].append(
        {
            "id": "noun:\u043a\u0438\u0442\u0435\u043f:s1",
            "lexeme_id": (
                "noun:\u043a\u0438\u0442\u0435\u043f"
            ),
            "sense_no": 1,
        }
    )

    data["glosses"].append(
        {
            "sense_id": (
                "noun:\u043a\u0438\u0442\u0435\u043f:s1"
            ),
            "language_code": "en",
            "text": "book",
        }
    )

    data["noun_forms"].append(
        {
            "lexeme_id": (
                "noun:\u043a\u0438\u0442\u0435\u043f"
            ),
            "form": (
                "\u043a\u0438\u0442\u0435\u043f\u0442\u0435"
            ),
            "canonical_key": "singular_locative",
            "number": "sg",
            "possessive": None,
            "case": "locative",
            "interrogative": False,
            "special": False,
        }
    )

    db_path = export_canonical_sqlite(
        data,
        tmp_path / "dictionary.db",
    )

    results = search_lexemes_by_form_sqlite(
        db_path,
        form_text=(
            "\u043a\u0438\u0442\u0435\u043f\u0442\u0435"
        ),
        language_code="ky",
        result_gloss_language="en",
    )

    assert len(results) == 1

    result = results[0]

    assert result["id"] == (
        "noun:\u043a\u0438\u0442\u0435\u043f"
    )

    assert result["matched_forms"][0] == {
        "lexeme_id": (
            "noun:\u043a\u0438\u0442\u0435\u043f"
        ),
        "form": (
            "\u043a\u0438\u0442\u0435\u043f\u0442\u0435"
        ),
        "canonical_key": "singular_locative",
        "number": "sg",
        "possessive": None,
        "case": "locative",
        "interrogative": False,
        "special": False,
    }


def test_sqlite_search_by_form_returns_empty_list_when_missing(
    tmp_path,
):
    from canonical import export_canonical_sqlite
    from sqlite_lexicon import search_lexemes_by_form_sqlite

    db_path = export_canonical_sqlite(
        _sample_data(),
        tmp_path / "dictionary.db",
    )

    results = search_lexemes_by_form_sqlite(
        db_path,
        form_text="missing",
        language_code="ky",
        result_gloss_language="en",
    )

    assert results == []


def test_sqlite_search_by_gloss_finds_lexeme(
    tmp_path,
):
    from canonical import export_canonical_sqlite
    from sqlite_lexicon import (
        search_lexemes_by_gloss_sqlite,
    )

    db_path = export_canonical_sqlite(
        _sample_data(),
        tmp_path / "dictionary.db",
    )

    results = search_lexemes_by_gloss_sqlite(
        db_path,
        query_language="en",
        query_text="buy",
        lexeme_language="ky",
        result_gloss_language="en",
    )

    assert len(results) == 1

    result = results[0]

    assert result["id"] == (
        "verb:\u0430\u043b\u0443\u0443"
    )

    assert result["lemma"] == (
        "\u0430\u043b\u0443\u0443"
    )

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


def test_sqlite_search_by_gloss_is_case_insensitive(
    tmp_path,
):
    from canonical import export_canonical_sqlite
    from sqlite_lexicon import (
        search_lexemes_by_gloss_sqlite,
    )

    data = _sample_data()

    data["glosses"].append(
        {
            "sense_id": (
                "verb:\u0430\u043b\u0443\u0443:s3"
            ),
            "language_code": "en",
            "text": "Purchase",
        }
    )

    db_path = export_canonical_sqlite(
        data,
        tmp_path / "dictionary.db",
    )

    results = search_lexemes_by_gloss_sqlite(
        db_path,
        query_language="en",
        query_text="purchase",
        lexeme_language="ky",
        result_gloss_language="en",
    )

    assert len(results) == 1
    assert results[0]["lemma"] == (
        "\u0430\u043b\u0443\u0443"
    )


def test_sqlite_search_by_gloss_returns_empty_list_when_missing(
    tmp_path,
):
    from canonical import export_canonical_sqlite
    from sqlite_lexicon import (
        search_lexemes_by_gloss_sqlite,
    )

    db_path = export_canonical_sqlite(
        _sample_data(),
        tmp_path / "dictionary.db",
    )

    results = search_lexemes_by_gloss_sqlite(
        db_path,
        query_language="en",
        query_text="missing",
        lexeme_language="ky",
        result_gloss_language="en",
    )

    assert results == []
