import json
import sqlite3
from pathlib import Path


MEANING_LOCALES = ("zh", "en", "ru")

POSSESSIVE_KEYS = (
    "your_plural_polite",
    "your_singular",
    "your_polite",
    "your_plural",
    "his_her",
    "their",
    "my",
    "our",
)

POSSESSIVE_FEATURE_VALUES = {
    "my": "1sg",
    "your_singular": "2sg",
    "your_polite": "2sg_polite",
    "his_her": "3sg",
    "our": "1pl",
    "your_plural": "2pl",
    "your_plural_polite": "2pl_polite",
    "their": "3pl",
}

PERSON_FEATURE_VALUES = {
    "men": "1sg",
    "sen": "2sg",
    "siz": "2sg_polite",
    "al": "3sg",
    "biz": "1pl",
    "siler": "2pl",
    "sizder": "2pl_polite",
    "alar": "3pl",
}

CASE_KEYS = (
    "locative_modifier",
    "instrumental",
    "comparative",
    "accusative",
    "ablative",
    "genitive",
    "locative",
    "caritive",
    "dative",
)

TENSE_KEYS = (
    "present_continuous",
    "negative_future",
    "negative_past",
    "future",
    "past",
)

VERB_BASE_COLUMNS = {
    "infinitive": {"form_type": "infinitive", "negative": False},
    "stem": {"form_type": "stem", "negative": False},
    "converb_p": {"form_type": "converb_p", "negative": False},
    "negative_stem": {"form_type": "stem", "negative": True},
    "imperative": {"form_type": "imperative", "negative": False},
    "negative_imperative": {"form_type": "imperative", "negative": True},
}


def _consume_prefix(value, candidates):
    for key in candidates:
        if value == key:
            return key, ""
        prefix = key + "_"
        if value.startswith(prefix):
            return key, value[len(prefix):]
    return None, value


def parse_noun_column(column):
    number, rest = _consume_prefix(column, ("singular", "plural"))
    if number is None:
        return None

    features = {
        "number": "sg" if number == "singular" else "pl",
        "possessive": None,
        "case": None,
        "interrogative": False,
        "special": False,
    }

    if not rest:
        return features

    possessive_key, rest = _consume_prefix(rest, POSSESSIVE_KEYS)
    if possessive_key:
        features["possessive"] = POSSESSIVE_FEATURE_VALUES[possessive_key]

    if rest == "special":
        features["special"] = True
        rest = ""
    elif rest.startswith("special_"):
        features["special"] = True
        rest = rest[len("special_"):]

    case_name, rest = _consume_prefix(rest, CASE_KEYS)
    if case_name:
        features["case"] = case_name

    if rest == "interrogative":
        features["interrogative"] = True
        rest = ""

    return features if not rest else None


def parse_verb_column(column):
    if column in VERB_BASE_COLUMNS:
        return {
            **VERB_BASE_COLUMNS[column],
            "tense": None,
            "person": None,
        }

    tense_key, person_key = _consume_prefix(column, TENSE_KEYS)
    if not tense_key or person_key not in PERSON_FEATURE_VALUES:
        return None

    negative = tense_key.startswith("negative_")
    tense = tense_key[len("negative_"):] if negative else tense_key
    return {
        "form_type": "finite",
        "tense": tense,
        "person": PERSON_FEATURE_VALUES[person_key],
        "negative": negative,
    }


def _meanings(row):
    return {
        locale: row.get(f"meaning_{locale}", "")
        for locale in MEANING_LOCALES
    }


def _next_lexeme_id(part_of_speech, lemma, seen_ids):
    base_id = f"{part_of_speech}:{lemma}"
    count = seen_ids.get(base_id, 0) + 1
    seen_ids[base_id] = count
    return base_id if count == 1 else f"{base_id}#{count}"


def build_canonical_data(nouns_df, verbs_df):
    lexemes = []
    noun_forms = []
    verb_forms = []
    seen_ids = {}

    noun_form_columns = [
        column for column in nouns_df.columns
        if parse_noun_column(column) is not None
    ]

    for _, row in nouns_df.iterrows():
        lemma = row.get("singular", "")
        lexeme_id = _next_lexeme_id("noun", lemma, seen_ids)
        lexemes.append({
            "id": lexeme_id,
            "part_of_speech": "noun",
            "lemma": lemma,
            "meanings": _meanings(row),
        })

        for column in noun_form_columns:
            form = row.get(column, "")
            if not form:
                continue
            features = parse_noun_column(column)
            noun_forms.append({
                "lexeme_id": lexeme_id,
                "form": form,
                "canonical_key": column,
                **features,
            })

    verb_form_columns = [
        column for column in verbs_df.columns
        if parse_verb_column(column) is not None
    ]

    for _, row in verbs_df.iterrows():
        lemma = row.get("infinitive", "")
        lexeme_id = _next_lexeme_id("verb", lemma, seen_ids)
        lexemes.append({
            "id": lexeme_id,
            "part_of_speech": "verb",
            "lemma": lemma,
            "meanings": _meanings(row),
        })

        for column in verb_form_columns:
            form = row.get(column, "")
            if not form:
                continue
            features = parse_verb_column(column)
            verb_forms.append({
                "lexeme_id": lexeme_id,
                "form": form,
                "canonical_key": column,
                **features,
            })

    return {
        "lexemes": lexemes,
        "noun_forms": noun_forms,
        "verb_forms": verb_forms,
    }


def export_canonical_json(data, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def export_canonical_sqlite(data, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DROP TABLE IF EXISTS noun_forms")
        conn.execute("DROP TABLE IF EXISTS verb_forms")
        conn.execute("DROP TABLE IF EXISTS lexemes")

        conn.execute(
            """
            CREATE TABLE lexemes (
                id TEXT PRIMARY KEY,
                part_of_speech TEXT NOT NULL,
                lemma TEXT NOT NULL,
                meaning_zh TEXT,
                meaning_en TEXT,
                meaning_ru TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE noun_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lexeme_id TEXT NOT NULL,
                form TEXT NOT NULL,
                canonical_key TEXT NOT NULL,
                number TEXT NOT NULL,
                possessive TEXT,
                case_name TEXT,
                interrogative INTEGER NOT NULL,
                special INTEGER NOT NULL,
                FOREIGN KEY (lexeme_id) REFERENCES lexemes(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE verb_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lexeme_id TEXT NOT NULL,
                form TEXT NOT NULL,
                canonical_key TEXT NOT NULL,
                form_type TEXT NOT NULL,
                tense TEXT,
                person TEXT,
                negative INTEGER NOT NULL,
                FOREIGN KEY (lexeme_id) REFERENCES lexemes(id)
            )
            """
        )

        conn.executemany(
            """
            INSERT INTO lexemes (
                id, part_of_speech, lemma, meaning_zh, meaning_en, meaning_ru
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    lexeme["id"],
                    lexeme["part_of_speech"],
                    lexeme["lemma"],
                    lexeme["meanings"].get("zh", ""),
                    lexeme["meanings"].get("en", ""),
                    lexeme["meanings"].get("ru", ""),
                )
                for lexeme in data["lexemes"]
            ],
        )

        conn.executemany(
            """
            INSERT INTO noun_forms (
                lexeme_id, form, canonical_key, number, possessive,
                case_name, interrogative, special
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item["lexeme_id"],
                    item["form"],
                    item["canonical_key"],
                    item["number"],
                    item["possessive"],
                    item["case"],
                    int(item["interrogative"]),
                    int(item["special"]),
                )
                for item in data["noun_forms"]
            ],
        )

        conn.executemany(
            """
            INSERT INTO verb_forms (
                lexeme_id, form, canonical_key, form_type,
                tense, person, negative
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item["lexeme_id"],
                    item["form"],
                    item["canonical_key"],
                    item["form_type"],
                    item["tense"],
                    item["person"],
                    int(item["negative"]),
                )
                for item in data["verb_forms"]
            ],
        )

        conn.execute("CREATE INDEX idx_lexemes_lemma ON lexemes(lemma)")
        conn.execute("CREATE INDEX idx_noun_forms_lexeme ON noun_forms(lexeme_id)")
        conn.execute("CREATE INDEX idx_noun_forms_features ON noun_forms(number, possessive, case_name, interrogative, special)")
        conn.execute("CREATE INDEX idx_verb_forms_lexeme ON verb_forms(lexeme_id)")
        conn.execute("CREATE INDEX idx_verb_forms_features ON verb_forms(form_type, tense, person, negative)")

    return path


def export_canonical_data(data, output_dir="output/canonical"):
    output_dir = Path(output_dir)
    return {
        "json": export_canonical_json(data, output_dir / "kyrgyz.json"),
        "sqlite": export_canonical_sqlite(data, output_dir / "kyrgyz.db"),
    }
