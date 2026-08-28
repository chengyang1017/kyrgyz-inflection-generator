from lexicon import search_lexicon


def build_dictionary_search_result(search_result):
    analyses = [
        {
            "text": form.get("form", ""),
            "key": form.get("canonical_key", ""),
            "label": form.get("label", ""),
        }
        for form in search_result.get(
            "matched_forms",
            [],
        )
    ]

    senses = [
        {
            "number": sense["sense_no"],
            "glosses": list(
                sense.get("glosses", [])
            ),
        }
        for sense in search_result.get(
            "senses",
            [],
        )
    ]

    return {
        "id": search_result["id"],
        "headword": search_result["lemma"],
        "language_code": (
            search_result["language_code"]
        ),
        "part_of_speech": (
            search_result["part_of_speech"]
        ),
        "match": {
            "primary": search_result[
                "primary_match"
            ],
            "types": list(
                search_result.get(
                    "match_types",
                    [],
                )
            ),
            "analyses": analyses,
        },
        "senses": senses,
    }



def search_dictionary(
    data,
    query_text,
    query_language,
    lexeme_language,
    result_gloss_language,
    form_locale=None,
):
    search_results = search_lexicon(
        data,
        query_text=query_text,
        query_language=query_language,
        lexeme_language=lexeme_language,
        result_gloss_language=result_gloss_language,
        form_locale=form_locale,
    )

    return [
        build_dictionary_search_result(result)
        for result in search_results
    ]
