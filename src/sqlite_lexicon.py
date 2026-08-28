import sqlite3


def _noun_form_from_row(row):
    return {
        "lexeme_id": row["lexeme_id"],
        "form": row["form"],
        "canonical_key": row["canonical_key"],
        "number": row["number"],
        "possessive": row["possessive"],
        "case": row["case_name"],
        "interrogative": bool(
            row["interrogative"]
        ),
        "special": bool(
            row["special"]
        ),
    }


def _verb_form_from_row(row):
    return {
        "lexeme_id": row["lexeme_id"],
        "form": row["form"],
        "canonical_key": row["canonical_key"],
        "form_type": row["form_type"],
        "tense": row["tense"],
        "person": row["person"],
        "negative": bool(
            row["negative"]
        ),
    }


def _load_senses(
    conn,
    lexeme_id,
    gloss_language,
):
    sense_rows = conn.execute(
        """
        SELECT id, sense_no
        FROM senses
        WHERE lexeme_id = ?
        ORDER BY sense_no
        """,
        (lexeme_id,),
    ).fetchall()

    senses = []

    for sense in sense_rows:
        gloss_rows = conn.execute(
            """
            SELECT text
            FROM glosses
            WHERE sense_id = ?
              AND language_code = ?
            ORDER BY id
            """,
            (
                sense["id"],
                gloss_language,
            ),
        ).fetchall()

        senses.append(
            {
                "sense_no": sense["sense_no"],
                "glosses": [
                    row["text"]
                    for row in gloss_rows
                ],
            }
        )

    return senses


def _load_noun_forms(
    conn,
    lexeme_id,
):
    rows = conn.execute(
        """
        SELECT
            lexeme_id,
            form,
            canonical_key,
            number,
            possessive,
            case_name,
            interrogative,
            special
        FROM noun_forms
        WHERE lexeme_id = ?
        ORDER BY id
        """,
        (lexeme_id,),
    ).fetchall()

    return [
        _noun_form_from_row(row)
        for row in rows
    ]


def _load_verb_forms(
    conn,
    lexeme_id,
):
    rows = conn.execute(
        """
        SELECT
            lexeme_id,
            form,
            canonical_key,
            form_type,
            tense,
            person,
            negative
        FROM verb_forms
        WHERE lexeme_id = ?
        ORDER BY id
        """,
        (lexeme_id,),
    ).fetchall()

    return [
        _verb_form_from_row(row)
        for row in rows
    ]


def _build_lexeme_result(
    conn,
    lexeme,
    gloss_language,
):
    lexeme_id = lexeme["id"]

    senses = _load_senses(
        conn,
        lexeme_id,
        gloss_language,
    )

    if lexeme["part_of_speech"] == "noun":
        forms = _load_noun_forms(
            conn,
            lexeme_id,
        )
    elif lexeme["part_of_speech"] == "verb":
        forms = _load_verb_forms(
            conn,
            lexeme_id,
        )
    else:
        forms = []

    return {
        "id": lexeme["id"],
        "language_code": (
            lexeme["language_code"]
        ),
        "part_of_speech": (
            lexeme["part_of_speech"]
        ),
        "lemma": lexeme["lemma"],
        "senses": senses,
        "forms": forms,
    }


def lookup_lexeme_sqlite(
    db_path,
    language_code,
    lemma,
    gloss_language,
):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        lexeme = conn.execute(
            """
            SELECT
                id,
                language_code,
                part_of_speech,
                lemma
            FROM lexemes
            WHERE language_code = ?
              AND lemma = ?
            ORDER BY id
            LIMIT 1
            """,
            (
                language_code,
                lemma,
            ),
        ).fetchone()

        if lexeme is None:
            return None

        return _build_lexeme_result(
            conn,
            lexeme,
            gloss_language,
        )


def search_lexemes_by_form_sqlite(
    db_path,
    form_text,
    language_code,
    result_gloss_language,
):
    normalized_form = str(form_text).strip()

    if not normalized_form:
        return []

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        noun_rows = conn.execute(
            """
            SELECT
                noun_forms.lexeme_id,
                noun_forms.form,
                noun_forms.canonical_key,
                noun_forms.number,
                noun_forms.possessive,
                noun_forms.case_name,
                noun_forms.interrogative,
                noun_forms.special
            FROM noun_forms
            JOIN lexemes
              ON lexemes.id = noun_forms.lexeme_id
            WHERE noun_forms.form = ?
              AND lexemes.language_code = ?
            ORDER BY noun_forms.id
            """,
            (
                normalized_form,
                language_code,
            ),
        ).fetchall()

        verb_rows = conn.execute(
            """
            SELECT
                verb_forms.lexeme_id,
                verb_forms.form,
                verb_forms.canonical_key,
                verb_forms.form_type,
                verb_forms.tense,
                verb_forms.person,
                verb_forms.negative
            FROM verb_forms
            JOIN lexemes
              ON lexemes.id = verb_forms.lexeme_id
            WHERE verb_forms.form = ?
              AND lexemes.language_code = ?
            ORDER BY verb_forms.id
            """,
            (
                normalized_form,
                language_code,
            ),
        ).fetchall()

        matched_forms_by_lexeme = {}

        for row in noun_rows:
            matched_forms_by_lexeme.setdefault(
                row["lexeme_id"],
                [],
            ).append(
                _noun_form_from_row(row)
            )

        for row in verb_rows:
            matched_forms_by_lexeme.setdefault(
                row["lexeme_id"],
                [],
            ).append(
                _verb_form_from_row(row)
            )

        if not matched_forms_by_lexeme:
            return []

        results = []

        for lexeme_id, matched_forms in (
            matched_forms_by_lexeme.items()
        ):
            lexeme = conn.execute(
                """
                SELECT
                    id,
                    language_code,
                    part_of_speech,
                    lemma
                FROM lexemes
                WHERE id = ?
                """,
                (lexeme_id,),
            ).fetchone()

            if lexeme is None:
                continue

            result = _build_lexeme_result(
                conn,
                lexeme,
                result_gloss_language,
            )

            result["matched_forms"] = (
                matched_forms
            )

            results.append(result)

        return results


def search_lexemes_by_gloss_sqlite(
    db_path,
    query_language,
    query_text,
    lexeme_language,
    result_gloss_language,
):
    normalized_query = str(query_text).strip()

    if not normalized_query:
        return []

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        lexeme_rows = conn.execute(
            """
            SELECT DISTINCT
                lexemes.id,
                lexemes.language_code,
                lexemes.part_of_speech,
                lexemes.lemma
            FROM glosses
            JOIN senses
              ON senses.id = glosses.sense_id
            JOIN lexemes
              ON lexemes.id = senses.lexeme_id
            WHERE glosses.language_code = ?
              AND glosses.text = ? COLLATE NOCASE
              AND lexemes.language_code = ?
            ORDER BY lexemes.lemma, lexemes.id
            """,
            (
                query_language,
                normalized_query,
                lexeme_language,
            ),
        ).fetchall()

        return [
            _build_lexeme_result(
                conn,
                lexeme,
                result_gloss_language,
            )
            for lexeme in lexeme_rows
        ]
