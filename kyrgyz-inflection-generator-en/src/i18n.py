import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
LOCALES_DIR = ROOT_DIR / "locales"
SUPPORTED_LOCALES = ("zh", "en", "ru")

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

VERB_BASE_KEYS = (
    "negative_imperative",
    "negative_stem",
    "converb_p",
    "imperative",
    "infinitive",
    "stem",
)


def load_locale(locale):
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(
            f"Unsupported locale: {locale}. "
            f"Choose one of: {', '.join(SUPPORTED_LOCALES)}"
        )

    path = LOCALES_DIR / f"{locale}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _join(parts):
    return " · ".join(part for part in parts if part)


def _consume_prefix(value, candidates):
    for key in candidates:
        if value == key:
            return key, ""
        prefix = key + "_"
        if value.startswith(prefix):
            return key, value[len(prefix):]
    return None, value


def localize_noun_column(column, labels):
    if column in ("singular", "plural"):
        return labels["number"][column]

    number, rest = _consume_prefix(column, ("singular", "plural"))
    if number is None:
        return column

    parts = [labels["number"][number]]

    possessive, rest = _consume_prefix(rest, POSSESSIVE_KEYS)
    if possessive:
        parts.append(labels["possessive"][possessive])

    if rest == "special":
        parts.append(labels["other"]["special"])
        return _join(parts)
    if rest.startswith("special_"):
        parts.append(labels["other"]["special"])
        rest = rest[len("special_"):]

    case_name, rest = _consume_prefix(rest, CASE_KEYS)
    if case_name:
        parts.append(labels["case"][case_name])

    if rest == "interrogative":
        parts.append(labels["other"]["interrogative"])
        rest = ""

    if rest:
        return column
    return _join(parts)


def localize_verb_column(column, labels):
    if column in VERB_BASE_KEYS:
        return labels["other"][column]

    tense, person = _consume_prefix(column, TENSE_KEYS)
    if tense and person in labels["person"]:
        return _join([labels["tense"][tense], labels["person"][person]])

    return column


def localize_dataframe(df, locale, part_of_speech):
    labels = load_locale(locale)
    result = df.copy()

    meaning_column = f"meaning_{locale}"
    fallback_columns = (meaning_column, "meaning_en", "meaning_zh", "meaning_ru")
    selected_meaning = next((c for c in fallback_columns if c in result.columns), None)

    meaning_columns = [c for c in result.columns if c.startswith("meaning_")]
    if selected_meaning:
        result[labels["meaning"]] = result[selected_meaning]
    else:
        result[labels["meaning"]] = ""

    if meaning_columns:
        result = result.drop(columns=meaning_columns)

    localizer = localize_noun_column if part_of_speech == "noun" else localize_verb_column
    result = result.rename(columns={
        column: localizer(column, labels)
        for column in result.columns
        if column != labels["meaning"]
    })

    columns = [labels["meaning"]] + [
        column for column in result.columns if column != labels["meaning"]
    ]
    return result[columns]
