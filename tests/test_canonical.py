import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canonical import (
    build_canonical_data,
    export_canonical_json,
    export_canonical_sqlite,
    parse_noun_column,
    parse_verb_column,
)
from noun_generator import generate_nouns_df
from verb_generator import generate_verbs_df


def test_parse_noun_column_features():
    assert parse_noun_column("singular_my_locative_interrogative") == {
        "number": "sg",
        "possessive": "1sg",
        "case": "locative",
        "interrogative": True,
        "special": False,
    }

    assert parse_noun_column("plural_his_her_special_dative_interrogative") == {
        "number": "pl",
        "possessive": "3sg",
        "case": "dative",
        "interrogative": True,
        "special": True,
    }


def test_parse_verb_column_features():
    assert parse_verb_column("negative_past_sizder") == {
        "form_type": "finite",
        "tense": "past",
        "person": "2pl_polite",
        "negative": True,
    }

    assert parse_verb_column("imperative") == {
        "form_type": "imperative",
        "negative": False,
        "tense": None,
        "person": None,
    }


def test_build_canonical_data_from_wide_frames():
    nouns_df = pd.DataFrame([
        {
            "meaning_zh": "书",
            "meaning_en": "book",
            "meaning_ru": "книга",
            "singular": "китеп",
            "singular_locative": "китепте",
            "singular_my_locative_interrogative": "китебимдеби",
            "plural": "китептер",
        }
    ])
    verbs_df = pd.DataFrame([
        {
            "meaning_zh": "去",
            "meaning_en": "go",
            "meaning_ru": "идти",
            "infinitive": "баруу",
            "stem": "бар",
            "future_men": "барам",
            "negative_past_sizder": "барган жоксуздар",
        }
    ])

    data = build_canonical_data(nouns_df, verbs_df)

    assert len(data["lexemes"]) == 2
    assert data["lexemes"][0] == {
        "id": "noun:китеп",
        "part_of_speech": "noun",
        "lemma": "китеп",
        "meanings": {"zh": "书", "en": "book", "ru": "книга"},
    }

    noun_form = next(
        item for item in data["noun_forms"]
        if item["canonical_key"] == "singular_my_locative_interrogative"
    )
    assert noun_form["form"] == "китебимдеби"
    assert noun_form["number"] == "sg"
    assert noun_form["possessive"] == "1sg"
    assert noun_form["case"] == "locative"
    assert noun_form["interrogative"] is True

    verb_form = next(
        item for item in data["verb_forms"]
        if item["canonical_key"] == "negative_past_sizder"
    )
    assert verb_form["negative"] is True
    assert verb_form["tense"] == "past"
    assert verb_form["person"] == "2pl_polite"


def test_full_generated_frames_convert_without_losing_forms():
    nouns_df = generate_nouns_df()
    verbs_df = generate_verbs_df()
    data = build_canonical_data(nouns_df, verbs_df)

    noun_columns = [
        column for column in nouns_df.columns
        if parse_noun_column(column) is not None
    ]
    verb_columns = [
        column for column in verbs_df.columns
        if parse_verb_column(column) is not None
    ]

    expected_noun_forms = sum(
        bool(row.get(column, ""))
        for _, row in nouns_df.iterrows()
        for column in noun_columns
    )
    expected_verb_forms = sum(
        bool(row.get(column, ""))
        for _, row in verbs_df.iterrows()
        for column in verb_columns
    )

    assert len(data["lexemes"]) == len(nouns_df) + len(verbs_df)
    assert len(data["noun_forms"]) == expected_noun_forms
    assert len(data["verb_forms"]) == expected_verb_forms
    assert all(item["form"] for item in data["noun_forms"])
    assert all(item["form"] for item in data["verb_forms"])


def test_duplicate_lemmas_get_distinct_lexeme_ids():
    nouns_df = pd.DataFrame([
        {
            "meaning_zh": "意思一",
            "meaning_en": "sense one",
            "meaning_ru": "значение один",
            "singular": "тест",
        },
        {
            "meaning_zh": "意思二",
            "meaning_en": "sense two",
            "meaning_ru": "значение два",
            "singular": "тест",
        },
    ])
    verbs_df = pd.DataFrame(columns=[
        "meaning_zh", "meaning_en", "meaning_ru", "infinitive", "stem"
    ])

    data = build_canonical_data(nouns_df, verbs_df)

    assert [item["id"] for item in data["lexemes"]] == [
        "noun:тест",
        "noun:тест#2",
    ]


def test_canonical_exports_json_and_sqlite(tmp_path):
    data = {
        "lexemes": [
            {
                "id": "noun:китеп",
                "part_of_speech": "noun",
                "lemma": "китеп",
                "meanings": {"zh": "书", "en": "book", "ru": "книга"},
            }
        ],
        "noun_forms": [
            {
                "lexeme_id": "noun:китеп",
                "form": "китепте",
                "canonical_key": "singular_locative",
                "number": "sg",
                "possessive": None,
                "case": "locative",
                "interrogative": False,
                "special": False,
            }
        ],
        "verb_forms": [],
    }

    json_path = export_canonical_json(data, tmp_path / "kyrgyz.json")
    sqlite_path = export_canonical_sqlite(data, tmp_path / "kyrgyz.db")

    with json_path.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["noun_forms"][0]["case"] == "locative"

    with sqlite3.connect(sqlite_path) as conn:
        lexeme = conn.execute(
            "SELECT lemma, meaning_en FROM lexemes WHERE id = ?",
            ("noun:китеп",),
        ).fetchone()
        noun_form = conn.execute(
            "SELECT form, number, case_name FROM noun_forms"
        ).fetchone()

    assert lexeme == ("китеп", "book")
    assert noun_form == ("китепте", "sg", "locative")
