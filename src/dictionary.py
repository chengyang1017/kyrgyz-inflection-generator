from lexicon import search_lexicon
from i18n import localize_form_key
from sqlite_lexicon import search_lexicon_sqlite


VERB_FEATURE_KEYS = (
    "form_type",
    "tense",
    "person",
    "negative",
)

NOUN_FEATURE_KEYS = (
    "number",
    "possessive",
    "case",
    "interrogative",
    "special",
)


def _build_analysis(
    form,
    part_of_speech,
):
    analysis = {
        "text": form.get("form", ""),
        "key": form.get("canonical_key", ""),
        "label": form.get("label", ""),
    }

    if part_of_speech == "verb":
        feature_keys = VERB_FEATURE_KEYS
    elif part_of_speech == "noun":
        feature_keys = NOUN_FEATURE_KEYS
    else:
        feature_keys = ()

    features = {
        key: form[key]
        for key in feature_keys
        if key in form
    }

    if features:
        analysis["features"] = features

    return analysis


def build_dictionary_search_result(search_result):
    analyses = [
        _build_analysis(
            form,
            search_result["part_of_speech"],
        )
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


def _localize_matched_forms(search_results, form_locale):
    if not form_locale:
        return search_results

    localized_results = []

    for result in search_results:
        matched_forms = result.get("matched_forms")

        if not matched_forms:
            localized_results.append(result)
            continue

        localized_results.append({
            **result,
            "matched_forms": [
                {
                    **form,
                    "label": localize_form_key(
                        form.get("canonical_key", ""),
                        part_of_speech=result[
                            "part_of_speech"
                        ],
                        locale=form_locale,
                    ),
                }
                for form in matched_forms
            ],
        })

    return localized_results



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


def search_dictionary_sqlite(
    db_path,
    query_text,
    query_language,
    lexeme_language,
    result_gloss_language,
    form_locale=None,
):
    search_results = search_lexicon_sqlite(
        db_path,
        query_text=query_text,
        query_language=query_language,
        lexeme_language=lexeme_language,
        result_gloss_language=result_gloss_language,
    )

    localized_results = _localize_matched_forms(
        search_results,
        form_locale,
    )

    return [
        build_dictionary_search_result(result)
        for result in localized_results
    ]
