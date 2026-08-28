def lookup_lexeme(
    data,
    language_code,
    lemma,
    gloss_language,
):
    lexeme = next(
        (
            item
            for item in data.get("lexemes", [])
            if item.get("language_code") == language_code
            and item.get("lemma") == lemma
        ),
        None,
    )

    if lexeme is None:
        return None

    lexeme_id = lexeme["id"]

    source_senses = sorted(
        (
            sense
            for sense in data.get("senses", [])
            if sense.get("lexeme_id") == lexeme_id
        ),
        key=lambda sense: sense.get("sense_no", 0),
    )

    senses = []

    for sense in source_senses:
        sense_id = sense["id"]

        glosses = [
            gloss["text"]
            for gloss in data.get("glosses", [])
            if gloss.get("sense_id") == sense_id
            and gloss.get("language_code") == gloss_language
        ]

        senses.append(
            {
                "sense_no": sense["sense_no"],
                "glosses": glosses,
            }
        )

    if lexeme["part_of_speech"] == "noun":
        form_source = data.get("noun_forms", [])
    elif lexeme["part_of_speech"] == "verb":
        form_source = data.get("verb_forms", [])
    else:
        form_source = []

    forms = [
        form
        for form in form_source
        if form.get("lexeme_id") == lexeme_id
    ]

    return {
        "id": lexeme["id"],
        "language_code": lexeme["language_code"],
        "part_of_speech": lexeme["part_of_speech"],
        "lemma": lexeme["lemma"],
        "senses": senses,
        "forms": forms,
    }


def search_lexemes_by_gloss(
    data,
    query_language,
    query_text,
    lexeme_language,
    result_gloss_language,
):
    normalized_query = str(query_text).strip().casefold()

    if not normalized_query:
        return []

    matching_sense_ids = {
        gloss["sense_id"]
        for gloss in data.get("glosses", [])
        if gloss.get("language_code") == query_language
        and str(gloss.get("text", "")).strip().casefold()
        == normalized_query
    }

    if not matching_sense_ids:
        return []

    matching_lexeme_ids = {
        sense["lexeme_id"]
        for sense in data.get("senses", [])
        if sense.get("id") in matching_sense_ids
    }

    results = []

    for lexeme in data.get("lexemes", []):
        if lexeme.get("id") not in matching_lexeme_ids:
            continue

        if lexeme.get("language_code") != lexeme_language:
            continue

        result = lookup_lexeme(
            data,
            language_code=lexeme_language,
            lemma=lexeme["lemma"],
            gloss_language=result_gloss_language,
        )

        if result is not None:
            results.append(result)

    return results


def search_lexemes_by_form(
    data,
    form_text,
    language_code,
    result_gloss_language,
):
    normalized_form = str(form_text).strip()

    if not normalized_form:
        return []

    matching_forms = []

    for form_source in (
        data.get("noun_forms", []),
        data.get("verb_forms", []),
    ):
        for form in form_source:
            if str(form.get("form", "")).strip() == normalized_form:
                matching_forms.append(form)

    if not matching_forms:
        return []

    matching_forms_by_lexeme = {}

    for form in matching_forms:
        lexeme_id = form.get("lexeme_id")

        matching_forms_by_lexeme.setdefault(
            lexeme_id,
            [],
        ).append(form)

    results = []

    for lexeme in data.get("lexemes", []):
        lexeme_id = lexeme.get("id")

        if lexeme_id not in matching_forms_by_lexeme:
            continue

        if lexeme.get("language_code") != language_code:
            continue

        result = lookup_lexeme(
            data,
            language_code=language_code,
            lemma=lexeme["lemma"],
            gloss_language=result_gloss_language,
        )

        if result is None:
            continue

        result["matched_forms"] = (
            matching_forms_by_lexeme[lexeme_id]
        )

        results.append(result)

    return results


def search_lexicon(
    data,
    query_text,
    query_language,
    lexeme_language,
    result_gloss_language,
):
    normalized_query = str(query_text).strip()

    if not normalized_query:
        return []

    results_by_id = {}
    match_order = (
        "lemma",
        "form",
        "gloss",
    )

    def add_result(result, match_type):
        if result is None:
            return

        lexeme_id = result["id"]

        if lexeme_id not in results_by_id:
            results_by_id[lexeme_id] = {
                **result,
                "primary_match": match_type,
                "match_types": [match_type],
            }
            return

        existing = results_by_id[lexeme_id]

        if match_type not in existing["match_types"]:
            existing["match_types"].append(match_type)

        if "matched_forms" in result:
            existing_forms = existing.setdefault(
                "matched_forms",
                [],
            )

            for form in result["matched_forms"]:
                if form not in existing_forms:
                    existing_forms.append(form)

    # 1. Exact lemma match.
    if query_language == lexeme_language:
        lemma_result = lookup_lexeme(
            data,
            language_code=lexeme_language,
            lemma=normalized_query,
            gloss_language=result_gloss_language,
        )

        add_result(
            lemma_result,
            "lemma",
        )

    # 2. Inflected form match.
    if query_language == lexeme_language:
        form_results = search_lexemes_by_form(
            data,
            form_text=normalized_query,
            language_code=lexeme_language,
            result_gloss_language=result_gloss_language,
        )

        for result in form_results:
            add_result(
                result,
                "form",
            )

    # 3. Translation / gloss match.
    gloss_results = search_lexemes_by_gloss(
        data,
        query_language=query_language,
        query_text=normalized_query,
        lexeme_language=lexeme_language,
        result_gloss_language=result_gloss_language,
    )

    for result in gloss_results:
        add_result(
            result,
            "gloss",
        )

    results = list(results_by_id.values())

    # Keep match metadata deterministic even if the
    # implementation order changes later.
    for result in results:
        result["match_types"].sort(
            key=match_order.index
        )

        result["primary_match"] = (
            result["match_types"][0]
        )

    results.sort(
        key=lambda result: (
            match_order.index(
                result["primary_match"]
            ),
            result["lemma"].casefold(),
            result["id"],
        )
    )

    return results
