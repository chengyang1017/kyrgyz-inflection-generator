import sys
from copy import deepcopy
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
                "id": "noun:\u043a\u0438\u0442\u0435\u043f:s1",
                "lexeme_id": "noun:\u043a\u0438\u0442\u0435\u043f",
                "sense_no": 1,
            },
        ],
        "glosses": [
            {
                "sense_id": "verb:\u0430\u043b\u0443\u0443:s1",
                "language_code": "en",
                "text": "take",
            },
            {
                "sense_id": "noun:\u043a\u0438\u0442\u0435\u043f:s1",
                "language_code": "en",
                "text": "book",
            },
        ],
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
        "noun_forms": [
            {
                "lexeme_id": "noun:\u043a\u0438\u0442\u0435\u043f",
                "form": "\u043a\u0438\u0442\u0435\u043f\u0442\u0435",
                "canonical_key": "singular_locative",
                "number": "sg",
                "possessive": None,
                "case": "locative",
                "interrogative": False,
                "special": False,
            },
        ],
    }


def _database(tmp_path):
    from canonical import export_canonical_sqlite

    data = _sample_data()
    path = export_canonical_sqlite(
        data,
        tmp_path / "dictionary.db",
    )
    return data, path


def _search(path, text, query_language="ky", form_locale=None):
    from dictionary import search_dictionary_sqlite

    return search_dictionary_sqlite(
        path,
        query_text=text,
        query_language=query_language,
        lexeme_language="ky",
        result_gloss_language="en",
        form_locale=form_locale,
    )


def test_search_dictionary_sqlite_finds_lemma(tmp_path):
    _, path = _database(tmp_path)

    result = _search(path, "\u0430\u043b\u0443\u0443")[0]

    assert result["headword"] == "\u0430\u043b\u0443\u0443"
    assert result["language_code"] == "ky"
    assert result["part_of_speech"] == "verb"
    assert result["match"]["primary"] == "lemma"
    assert result["match"]["types"] == ["lemma", "form"]
    assert result["senses"] == [
        {"number": 1, "glosses": ["take"]},
    ]


def test_search_dictionary_sqlite_finds_inflected_verb(tmp_path):
    _, path = _database(tmp_path)

    result = _search(path, "\u0430\u043b\u0434\u044b\u043c")[0]

    assert result["match"]["primary"] == "form"
    assert result["match"]["analyses"][0]["key"] == "past_men"


def test_search_dictionary_sqlite_finds_gloss(tmp_path):
    _, path = _database(tmp_path)

    result = _search(path, "book", query_language="en")[0]

    assert result["headword"] == "\u043a\u0438\u0442\u0435\u043f"
    assert result["match"] == {
        "primary": "gloss",
        "types": ["gloss"],
        "analyses": [],
    }


def test_search_dictionary_sqlite_returns_empty_when_missing(tmp_path):
    _, path = _database(tmp_path)

    assert _search(path, "missing", query_language="en") == []


def test_search_dictionary_sqlite_localizes_verb_form(tmp_path):
    _, path = _database(tmp_path)

    result = _search(
        path,
        "\u0430\u043b\u0434\u044b\u043c",
        form_locale="zh",
    )[0]

    assert result["match"]["analyses"][0]["label"] == "\u8fc7\u53bb\u65f6 \u00b7 \u6211"


def test_search_dictionary_sqlite_localizes_noun_form(tmp_path):
    _, path = _database(tmp_path)

    result = _search(
        path,
        "\u043a\u0438\u0442\u0435\u043f\u0442\u0435",
        form_locale="zh",
    )[0]

    assert result["match"]["analyses"][0]["label"] == "\u5355\u6570 \u00b7 \u4f4d\u683c"


def test_search_dictionary_sqlite_preserves_structured_features(tmp_path):
    _, path = _database(tmp_path)

    verb = _search(path, "\u0430\u043b\u0434\u044b\u043c")[0]
    noun = _search(path, "\u043a\u0438\u0442\u0435\u043f\u0442\u0435")[0]

    assert verb["match"]["analyses"][0]["features"] == {
        "form_type": "finite",
        "tense": "past",
        "person": "1sg",
        "negative": False,
    }
    assert noun["match"]["analyses"][0]["features"] == {
        "number": "sg",
        "possessive": None,
        "case": "locative",
        "interrogative": False,
        "special": False,
    }


def test_search_dictionary_sqlite_preserves_ambiguous_analyses(tmp_path):
    from canonical import export_canonical_sqlite

    data = _sample_data()
    data["verb_forms"].append({
        "lexeme_id": "verb:\u0430\u043b\u0443\u0443",
        "form": "\u0430\u043b\u0434\u044b\u043c",
        "canonical_key": "future_men",
        "form_type": "finite",
        "tense": "future",
        "person": "1sg",
        "negative": False,
    })
    path = export_canonical_sqlite(
        data,
        tmp_path / "ambiguous.db",
    )

    result = _search(path, "\u0430\u043b\u0434\u044b\u043c")[0]

    assert [
        analysis["key"]
        for analysis in result["match"]["analyses"]
    ] == ["past_men", "future_men"]


def test_sqlite_dictionary_matches_in_memory_dictionary(tmp_path):
    from dictionary import search_dictionary

    data, path = _database(tmp_path)
    arguments = {
        "query_text": "\u0430\u043b\u0434\u044b\u043c",
        "query_language": "ky",
        "lexeme_language": "ky",
        "result_gloss_language": "en",
        "form_locale": "zh",
    }

    assert _search(
        path,
        arguments["query_text"],
        form_locale=arguments["form_locale"],
    ) == search_dictionary(data, **arguments)


def test_sqlite_dictionary_does_not_mutate_repository_results(monkeypatch):
    import dictionary

    repository_results = [{
        "id": "verb:\u0430\u043b\u0443\u0443",
        "language_code": "ky",
        "part_of_speech": "verb",
        "lemma": "\u0430\u043b\u0443\u0443",
        "primary_match": "form",
        "match_types": ["form"],
        "senses": [],
        "matched_forms": [{
            "form": "\u0430\u043b\u0434\u044b\u043c",
            "canonical_key": "past_men",
        }],
    }]
    original = deepcopy(repository_results)
    monkeypatch.setattr(
        dictionary,
        "search_lexicon_sqlite",
        lambda *args, **kwargs: repository_results,
    )

    dictionary.search_dictionary_sqlite(
        "unused.db", "\u0430\u043b\u0434\u044b\u043c", "ky", "ky", "en", "zh"
    )

    assert repository_results == original
