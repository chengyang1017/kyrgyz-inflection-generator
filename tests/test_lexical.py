import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canonical import build_canonical_data, export_canonical_sqlite


def test_legacy_meanings_become_default_sense_with_dynamic_glosses():
    nouns_df = pd.DataFrame([
        {
            "singular": "китеп",
            "meaning_zh": "书",
            "meaning_en": "book",
            "meaning_ru": "книга",
            "meaning_vi": "sách",
        }
    ])
    verbs_df = pd.DataFrame(columns=["infinitive", "stem"])

    data = build_canonical_data(nouns_df, verbs_df)

    assert data["lexemes"] == [
        {
            "id": "noun:китеп",
            "language_code": "ky",
            "part_of_speech": "noun",
            "lemma": "китеп",
        }
    ]

    assert data["senses"] == [
        {
            "id": "noun:китеп:s1",
            "lexeme_id": "noun:китеп",
            "sense_no": 1,
        }
    ]

    assert {
        (item["sense_id"], item["language_code"], item["text"])
        for item in data["glosses"]
    } == {
        ("noun:китеп:s1", "zh", "书"),
        ("noun:китеп:s1", "en", "book"),
        ("noun:китеп:s1", "ru", "книга"),
        ("noun:китеп:s1", "vi", "sách"),
    }


def test_legacy_meaning_text_is_not_automatically_split_into_senses():
    nouns_df = pd.DataFrame([
        {
            "singular": "сумка",
            "meaning_zh": "书包；包",
            "meaning_en": "bag",
        }
    ])
    verbs_df = pd.DataFrame(columns=["infinitive", "stem"])

    data = build_canonical_data(nouns_df, verbs_df)

    assert len(data["senses"]) == 1

    zh_glosses = [
        item["text"]
        for item in data["glosses"]
        if item["language_code"] == "zh"
    ]

    assert zh_glosses == ["书包；包"]


def test_sqlite_supports_multiple_senses_and_arbitrary_gloss_languages(tmp_path):
    data = {
        "lexemes": [
            {
                "id": "verb:алуу",
                "language_code": "ky",
                "part_of_speech": "verb",
                "lemma": "алуу",
            }
        ],
        "senses": [
            {
                "id": "verb:алуу:s1",
                "lexeme_id": "verb:алуу",
                "sense_no": 1,
            },
            {
                "id": "verb:алуу:s2",
                "lexeme_id": "verb:алуу",
                "sense_no": 2,
            },
        ],
        "glosses": [
            {
                "sense_id": "verb:алуу:s1",
                "language_code": "zh",
                "text": "拿",
            },
            {
                "sense_id": "verb:алуу:s1",
                "language_code": "en",
                "text": "take",
            },
            {
                "sense_id": "verb:алуу:s2",
                "language_code": "zh",
                "text": "得到",
            },
            {
                "sense_id": "verb:алуу:s2",
                "language_code": "vi",
                "text": "nhận",
            },
        ],
        "noun_forms": [],
        "verb_forms": [],
    }

    sqlite_path = export_canonical_sqlite(
        data,
        tmp_path / "kyrgyz.db",
    )

    with sqlite3.connect(sqlite_path) as conn:
        lexeme = conn.execute(
            """
            SELECT language_code, part_of_speech, lemma
            FROM lexemes
            WHERE id = ?
            """,
            ("verb:алуу",),
        ).fetchone()

        senses = conn.execute(
            """
            SELECT id, sense_no
            FROM senses
            WHERE lexeme_id = ?
            ORDER BY sense_no
            """,
            ("verb:алуу",),
        ).fetchall()

        glosses = conn.execute(
            """
            SELECT sense_id, language_code, text
            FROM glosses
            ORDER BY sense_id, language_code
            """
        ).fetchall()

    assert lexeme == ("ky", "verb", "алуу")
    assert senses == [
        ("verb:алуу:s1", 1),
        ("verb:алуу:s2", 2),
    ]
    assert ("verb:алуу:s2", "vi", "nhận") in glosses


def test_morphology_remains_linked_directly_to_lexeme():
    nouns_df = pd.DataFrame([
        {
            "singular": "китеп",
            "meaning_zh": "书",
            "singular_locative": "китепте",
        }
    ])
    verbs_df = pd.DataFrame(columns=["infinitive", "stem"])

    data = build_canonical_data(nouns_df, verbs_df)

    locative = next(
        item
        for item in data["noun_forms"]
        if item["canonical_key"] == "singular_locative"
    )

    assert locative["lexeme_id"] == "noun:китеп"
    assert locative["form"] == "китепте"


def test_explicit_source_senses_override_legacy_meanings():
    nouns_df = pd.DataFrame([
        {
            "singular": "тест",
            "meaning_zh": "旧的合并释义",
            "senses": [
                {
                    "glosses": {
                        "zh": ["意思一"],
                        "en": ["sense one"],
                    }
                },
                {
                    "glosses": {
                        "zh": ["意思二"],
                        "vi": ["nghĩa hai"],
                    }
                },
            ],
        }
    ])

    verbs_df = pd.DataFrame(
        columns=["infinitive", "stem"]
    )

    data = build_canonical_data(
        nouns_df,
        verbs_df,
    )

    assert data["senses"] == [
        {
            "id": "noun:тест:s1",
            "lexeme_id": "noun:тест",
            "sense_no": 1,
        },
        {
            "id": "noun:тест:s2",
            "lexeme_id": "noun:тест",
            "sense_no": 2,
        },
    ]

    assert {
        (
            item["sense_id"],
            item["language_code"],
            item["text"],
        )
        for item in data["glosses"]
    } == {
        ("noun:тест:s1", "zh", "意思一"),
        ("noun:тест:s1", "en", "sense one"),
        ("noun:тест:s2", "zh", "意思二"),
        ("noun:тест:s2", "vi", "nghĩa hai"),
    }


def test_loaders_preserve_explicit_senses_and_build_legacy_meaning_columns(
    tmp_path,
    monkeypatch,
):
    import json
    import utils

    nouns = [
        {
            "singular": "сумка",
            "senses": [
                {
                    "glosses": {
                        "zh": ["书包", "包"],
                        "en": ["bag"],
                        "vi": ["túi"],
                    }
                }
            ],
        }
    ]

    verbs = [
        {
            "infinitive": "алуу",
            "stem": "ал",
            "senses": [
                {
                    "glosses": {
                        "zh": ["拿"],
                        "en": ["take"],
                    }
                },
                {
                    "glosses": {
                        "zh": ["得到"],
                        "en": ["get"],
                    }
                },
            ],
        }
    ]

    (tmp_path / "nouns.json").write_text(
        json.dumps(
            nouns,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    (tmp_path / "verbs.json").write_text(
        json.dumps(
            verbs,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        utils,
        "DATA_DIR",
        tmp_path,
    )

    loaded_nouns = utils.load_nouns()
    loaded_verbs = utils.load_verbs()

    assert loaded_nouns[0]["senses"] == nouns[0]["senses"]
    assert loaded_verbs[0]["senses"] == verbs[0]["senses"]

    assert loaded_nouns[0]["meaning_zh"] == "书包；包"
    assert loaded_nouns[0]["meaning_en"] == "bag"

    assert loaded_verbs[0]["meaning_zh"] == "拿；得到"
    assert loaded_verbs[0]["meaning_en"] == "take; get"


def test_real_source_lexicon_uses_normalized_senses_only():
    import json

    root = Path(__file__).resolve().parents[1]

    for filename in ("nouns.json", "verbs.json"):
        entries = json.loads(
            (root / "data" / filename).read_text(
                encoding="utf-8"
            )
        )

        for entry in entries:
            assert "meanings" not in entry

            senses = entry.get("senses")

            assert isinstance(senses, list)
            assert senses

            for sense in senses:
                assert isinstance(sense, dict)

                glosses = sense.get("glosses")

                assert isinstance(glosses, dict)
                assert glosses

                for language_code, values in glosses.items():
                    assert isinstance(language_code, str)
                    assert language_code.strip()

                    assert isinstance(values, list)
                    assert values

                    assert all(
                        isinstance(value, str)
                        and value.strip()
                        for value in values
                    )

                    assert all(
                        ";" not in value
                        and chr(0xFF1B) not in value
                        for value in values
                    )


def test_verified_turuu_senses_are_separate():
    import json

    root = Path(__file__).resolve().parents[1]

    verbs = json.loads(
        (root / "data" / "verbs.json").read_text(
            encoding="utf-8"
        )
    )

    infinitive = "\u0442\u0443\u0440\u0443\u0443"

    verb = next(
        item
        for item in verbs
        if item.get("infinitive") == infinitive
    )

    assert verb["senses"] == [
        {
            "glosses": {
                "zh": ["\u7ad9"],
                "en": ["stand"],
                "ru": [
                    "\u0441\u0442\u043e\u044f\u0442\u044c"
                ],
            }
        },
        {
            "glosses": {
                "zh": ["\u8d77\u5e8a"],
                "en": ["get up"],
                "ru": [
                    "\u0432\u0441\u0442\u0430\u0432\u0430\u0442\u044c"
                ],
            }
        },
    ]
